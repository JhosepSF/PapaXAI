"""
Vistas principales para el sistema PapaXAI.
Controla el flujo de navegación, carga de muestras, inferencia, XAI y exportación de reportes.
"""

import os
import uuid
import json
import logging
from datetime import datetime
from PIL import Image

from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse, FileResponse
from django.conf import settings
from django.core.files.base import ContentFile
from django.views.decorators.http import require_http_methods

from .models import Diagnostico
from .forms import DiagnosticoUploadForm
from .services.model_loader import get_model_loader
from .services.image_processing import validate_and_load_image, prepare_image_for_inference, ImageProcessingError
from .services.inference import get_inference_service
from .services.explainability import get_xai_service
from .services.pdf_report import generate_diagnostic_pdf
from .services.patologias import CATALOGO_PATOLOGIAS, get_patologia_info

logger = logging.getLogger(__name__)

def inicio_view(request):
    """Pantalla 1: Inicio editorial botánico y presentación de PapaXAI."""
    loader = get_model_loader()
    metrics = loader.get_metrics()
    
    context = {
        'total_patologias': len(CATALOGO_PATOLOGIAS),
        'patologias': CATALOGO_PATOLOGIAS,
        'metrics': metrics,
    }
    return render(request, 'diagnostico/inicio.html', context)

def analizar_view(request):
    """Pantalla 2: Interfaz de carga, arrastrar y soltar, y selección de muestras."""
    form = DiagnosticoUploadForm()
    
    # Muestras de prueba disponibles
    muestras_dir = os.path.join(settings.BASE_DIR, 'media', 'muestras')
    manifest_path = os.path.join(muestras_dir, 'fotos_test_manifest.json')
    muestras_list = []
    
    if os.path.exists(manifest_path):
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                muestras_list = json.load(f)
        except Exception as e:
            logger.warning("No se pudo leer el manifest de fotos_test: %s", e)

    if request.method == 'POST':
        form = DiagnosticoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                uploaded_file = form.cleaned_data.get('imagen')
                muestra_key = form.cleaned_data.get('muestra_seleccionada')
                
                # Caso A: Se seleccionó una imagen de prueba predefinida
                if muestra_key and not uploaded_file:
                    target_sample_path = os.path.join(muestras_dir, muestra_key)
                    if not os.path.exists(target_sample_path):
                        # Intentar en ResNet50_XGB/fotos_test
                        target_sample_path = os.path.join(settings.BASE_DIR, 'ResNet50_XGB', 'fotos_test', muestra_key)
                        
                    if not os.path.exists(target_sample_path):
                        form.add_error(None, f"No se encontró el archivo de prueba '{muestra_key}'.")
                        return render(request, 'diagnostico/analizar.html', {'form': form, 'muestras': muestras_list})
                    
                    with open(target_sample_path, 'rb') as f:
                        file_bytes = f.read()
                    pil_img, (w, h) = validate_and_load_image(target_sample_path)
                    orig_filename = muestra_key
                    file_size_kb = round(len(file_bytes) / 1024, 2)
                    content_file = ContentFile(file_bytes, name=muestra_key)
                    
                # Caso B: El usuario subió una imagen real
                else:
                    orig_filename = uploaded_file.name
                    file_size_kb = round(uploaded_file.size / 1024, 2)
                    pil_img, (w, h) = validate_and_load_image(uploaded_file)
                    uploaded_file.seek(0)
                    content_file = uploaded_file

                # Preprocesar imagen
                batch_arr, arr_224, pil_224 = prepare_image_for_inference(pil_img)
                
                # Ejecutar inferencia ResNet50 + XGBoost
                inference_service = get_inference_service()
                inf_result = inference_service.predict(batch_arr)
                
                # Ejecutar explicabilidad XAI por oclusión
                xai_service = get_xai_service()
                xai_result = xai_service.generate_explanation(
                    img_arr_224=arr_224,
                    target_class_label=inf_result['predicted_class'],
                    baseline_probability=inf_result['max_probability']
                )

                # Persistir en base de datos
                diagnostico = Diagnostico(
                    nombre_archivo_original=orig_filename,
                    peso_archivo_kb=file_size_kb,
                    dimensiones_originales=f"{w} x {h} px",
                    clase_predicha=inf_result['predicted_class'],
                    clase_predicha_es=inf_result['predicted_class_es'],
                    probabilidad_maxima=inf_result['max_probability'],
                    probabilidades=inf_result['probabilities_dict'],
                    tiempo_inferencia_ms=inf_result['latency_ms'],
                    tiempo_xai_ms=xai_result['latency_ms']
                )
                
                # Guardar imagen original y referencias XAI
                diagnostico.imagen_original.save(
                    f"{uuid.uuid4().hex[:10]}_{orig_filename}",
                    content_file,
                    save=False
                )
                diagnostico.mapa_calor_xai.name = xai_result['heatmap_path']
                diagnostico.superposicion_xai.name = xai_result['overlay_path']
                diagnostico.save()

                # Si es una petición AJAX, responder JSON
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({
                        'status': 'success',
                        'redirect_url': diagnostico.get_absolute_url()
                    })

                return redirect(diagnostico.get_absolute_url())

            except ImageProcessingError as e:
                form.add_error(None, str(e))
            except Exception as e:
                logger.exception("Error durante el diagnóstico:")
                form.add_error(None, f"Ocurrió un error inesperado al procesar la imagen: {str(e)}")

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            errors = [str(err) for errs in form.errors.values() for err in errs]
            return JsonResponse({'status': 'error', 'errors': errors}, status=400)

    context = {
        'form': form,
        'muestras': muestras_list,
        'patologias': CATALOGO_PATOLOGIAS,
    }
    return render(request, 'diagnostico/analizar.html', context)

def resultado_view(request, pk):
    """Pantalla 3: Resultado del diagnóstico foliar y explicabilidad XAI."""
    diagnostico = get_object_or_404(Diagnostico, pk=pk)
    loader = get_model_loader()
    
    # Preparar datos ordenados de probabilidades para las barras visuales
    probs_data = []
    if isinstance(diagnostico.probabilidades, dict):
        for label, prob in diagnostico.probabilidades.items():
            prob_float = float(prob)
            probs_data.append({
                'label': label,
                'label_es': loader.get_label_es(label),
                'probability': prob_float,
                'percentage': round(prob_float * 100, 2),
                'is_winner': (label == diagnostico.clase_predicha),
                'info': get_patologia_info(label)
            })
        probs_data.sort(key=lambda x: x['probability'], reverse=True)

    pat_info = get_patologia_info(diagnostico.clase_predicha)

    context = {
        'diagnostico': diagnostico,
        'pat_info': pat_info,
        'probs_data': probs_data,
        'prob_ganadora_pct': round(diagnostico.probabilidad_maxima * 100, 2),
    }
    return render(request, 'diagnostico/resultado.html', context)

def descargar_pdf_view(request, pk):
    """Genera y descarga el reporte técnico formal en formato PDF."""
    diagnostico = get_object_or_404(Diagnostico, pk=pk)
    pdf_buffer = generate_diagnostic_pdf(diagnostico)
    
    filename = f"PapaXAI_Diagnostico_{str(diagnostico.id)[:8]}.pdf"
    response = HttpResponse(pdf_buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response

def acerca_view(request):
    """Pantalla 4: Acerca del sistema, arquitectura ResNet50 + XGBoost y XAI."""
    loader = get_model_loader()
    metrics = loader.get_metrics()
    config = loader.get_config()

    context = {
        'patologias': CATALOGO_PATOLOGIAS,
        'metrics': metrics,
        'config': config,
    }
    return render(request, 'diagnostico/acerca.html', context)

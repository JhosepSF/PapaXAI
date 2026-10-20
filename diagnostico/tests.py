"""
Pruebas automatizadas para el sistema PapaXAI.
Verifica carga de vistas, procesamiento de inferencia, explicabilidad XAI y reporte PDF.
"""

import os
import json
from django.test import TestCase, Client
from django.urls import reverse
from django.conf import settings
from .models import Diagnostico
from .services.model_loader import get_model_loader
from .services.image_processing import validate_and_load_image, prepare_image_for_inference
from .services.inference import get_inference_service
from .services.explainability import get_xai_service

class PapaXAITestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.samples_dir = os.path.join(settings.BASE_DIR, 'ResNet50_XGB', 'fotos_test')
        self.foto_anthracnose = os.path.join(self.samples_dir, 'prueba_01_Anthracnose.jpg')
        self.foto_healthy = os.path.join(self.samples_dir, 'prueba_02_Healthy.jpg')

    def test_pantallas_principales_cargan_correctamente(self):
        """Verifica que las rutas estáticas y vistas principales respondan 200 OK."""
        # 1. Inicio
        resp_inicio = self.client.get(reverse('diagnostico:inicio'))
        self.assertEqual(resp_inicio.status_code, 200)
        self.assertContains(resp_inicio, "Comprende la salud de tus cultivos, hoja por hoja")

        # 2. Analizar
        resp_analizar = self.client.get(reverse('diagnostico:analizar'))
        self.assertEqual(resp_analizar.status_code, 200)
        self.assertContains(resp_analizar, "Analizar muestra foliar")

        # 3. Acerca de
        resp_acerca = self.client.get(reverse('diagnostico:acerca'))
        self.assertEqual(resp_acerca.status_code, 200)
        self.assertContains(resp_acerca, "ResNet50 + XGBoost")

    def test_model_loader_singleton(self):
        """Verifica que el cargador de modelos sea un Singleton y contenga 5 clases."""
        loader1 = get_model_loader()
        loader2 = get_model_loader()
        self.assertIs(loader1, loader2)
        self.assertEqual(len(loader1.labels), 5)
        self.assertIn('Anthracnose', loader1.labels)
        self.assertIn('Healthy', loader1.labels)

    def test_pipeline_completo_con_foto_test(self):
        """
        Ejecuta el pipeline real sobre prueba_01_Anthracnose.jpg y valida
        que la predicción sea Anthracnose y coincida con el baseline experimental.
        """
        self.assertTrue(os.path.exists(self.foto_anthracnose), "La foto de prueba 1 debe existir")
        
        # Validar y procesar imagen
        pil_img, (w, h) = validate_and_load_image(self.foto_anthracnose)
        self.assertGreater(w, 0)
        self.assertGreater(h, 0)

        batch_arr, arr_224, pil_224 = prepare_image_for_inference(pil_img)
        self.assertEqual(batch_arr.shape, (1, 224, 224, 3))
        self.assertEqual(arr_224.shape, (224, 224, 3))

        # Inferencia
        inf_service = get_inference_service()
        inf_res = inf_service.predict(batch_arr)

        self.assertEqual(inf_res['predicted_class'], 'Anthracnose')
        self.assertEqual(inf_res['predicted_class_es'], 'Antracnosis')
        self.assertGreater(inf_res['max_probability'], 0.95)

        # Explicabilidad XAI
        xai_service = get_xai_service()
        xai_res = xai_service.generate_explanation(
            arr_224,
            inf_res['predicted_class'],
            inf_res['max_probability']
        )
        self.assertTrue(os.path.exists(os.path.join(settings.MEDIA_ROOT, xai_res['heatmap_path'])))
        self.assertTrue(os.path.exists(os.path.join(settings.MEDIA_ROOT, xai_res['overlay_path'])))

    def test_flujo_web_diagnostico_y_pdf(self):
        """
        Verifica el flujo web completo:
        1. Envío POST con muestra de prueba
        2. Redirección a la vista de resultado
        3. Comprobación de la ficha y mapa XAI
        4. Descarga del reporte PDF
        """
        resp_post = self.client.post(reverse('diagnostico:analizar'), {
            'muestra_seleccionada': 'prueba_02_Healthy.jpg'
        })
        self.assertEqual(resp_post.status_code, 302)
        
        diag = Diagnostico.objects.first()
        self.assertIsNotNone(diag)
        self.assertEqual(diag.clase_predicha, 'Healthy')

        # Vista de resultado
        resp_res = self.client.get(diag.get_absolute_url())
        self.assertEqual(resp_res.status_code, 200)
        self.assertContains(resp_res, "Hoja sana")

        # Descarga de PDF
        resp_pdf = self.client.get(reverse('diagnostico:descargar_pdf', kwargs={'pk': str(diag.id)}))
        self.assertEqual(resp_pdf.status_code, 200)
        self.assertEqual(resp_pdf['Content-Type'], 'application/pdf')
        self.assertGreater(len(resp_pdf.content), 5000)

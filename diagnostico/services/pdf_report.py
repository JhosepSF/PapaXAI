"""
Servicio de generación de reportes técnicos en formato PDF con ReportLab.
Diseño sobrio, editorial y botánico para documentar el diagnóstico y la explicabilidad XAI.
"""

import os
from io import BytesIO
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage, KeepTogether, HRFlowable
)
from .patologias import get_patologia_info

def generate_diagnostic_pdf(diagnostico):
    """
    Genera un documento PDF en memoria a partir de un objeto Diagnostico.
    Retorna un buffer BytesIO listo para streaming HTTP.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    
    # Paleta botánica
    c_primary = colors.HexColor('#345B48')
    c_secondary = colors.HexColor('#78927C')
    c_dark = colors.HexColor('#25342B')
    c_muted = colors.HexColor('#6F7D71')
    c_bg_light = colors.HexColor('#F7F8F3')
    c_border = colors.HexColor('#DEE5DC')
    c_accent = colors.HexColor('#C7A776')

    # Estilos tipográficos
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=c_primary
    )
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=c_muted
    )
    section_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=c_primary,
        spaceAfter=6
    )
    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=c_dark
    )
    small_muted = ParagraphStyle(
        'SmallMuted',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11,
        textColor=c_muted
    )
    pred_style = ParagraphStyle(
        'PredClass',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=17,
        textColor=c_primary
    )

    story = []

    # 1. Encabezado con membrete editorial
    header_data = [
        [
            Paragraph("<b>PapaXAI</b> | Sistema de Diagnóstico Agrícola Foliar", title_style),
            Paragraph(f"<b>Fecha:</b> {diagnostico.fecha_creacion.strftime('%d/%m/%Y %H:%M')}<br/><b>ID:</b> {str(diagnostico.id)[:13]}...", subtitle_style)
        ]
    ]
    t_header = Table(header_data, colWidths=[380, 160])
    t_header.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t_header)
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceBefore=4, spaceAfter=12))

    # 2. Información del Caso y Diagnóstico Principal
    pat_info = get_patologia_info(diagnostico.clase_predicha)
    pct = round(diagnostico.probabilidad_maxima * 100, 2)

    diag_box_data = [
        [
            Paragraph("<b>DIAGNÓSTICO PREDICHO</b>", small_muted),
            Paragraph("<b>CONFIANZA DEL MODELO</b>", small_muted),
            Paragraph("<b>AGENTE FITOPATÓGENO</b>", small_muted)
        ],
        [
            Paragraph(f"<b>{diagnostico.clase_predicha_es}</b><br/><font color='#6F7D71' size=8>({diagnostico.clase_predicha})</font>", pred_style),
            Paragraph(f"<font size=16 color='#345B48'><b>{pct}%</b></font><br/><font color='#6F7D71' size=8>Probabilidad XGBoost</font>", body_style),
            Paragraph(f"<i>{pat_info['agente']}</i><br/><font color='#6F7D71' size=8>{pat_info['tipo_patogeno']}</font>", body_style)
        ]
    ]
    t_diag = Table(diag_box_data, colWidths=[200, 140, 200])
    t_diag.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), c_bg_light),
        ('BOX', (0, 0), (-1, -1), 1, c_border),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, c_border),
        ('PADDING', (0, 0), (-1, -1), 8),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(t_diag)
    story.append(Spacer(1, 14))

    # 3. Tríptico Visual: Original, Mapa XAI y Superposición
    story.append(Paragraph("Evaluación Visual y Explicabilidad por Oclusión (XAI)", section_heading))
    
    img_cells = []
    titles_cells = [
        Paragraph("<b>1. Fotografía original</b>", small_muted),
        Paragraph("<b>2. Mapa de calor (Oclusión)</b>", small_muted),
        Paragraph("<b>3. Superposición explicativa</b>", small_muted)
    ]

    # Cargar imágenes si existen
    def get_rl_image(img_field, width=170, height=170):
        if img_field and hasattr(img_field, 'path') and os.path.exists(img_field.path):
            try:
                return RLImage(img_field.path, width=width, height=height)
            except Exception:
                pass
        # Fallback texto si no existe
        return Paragraph("<font color='#A0AEC0'>Imagen no disponible</font>", small_muted)

    img_cells.append(get_rl_image(diagnostico.imagen_original, 170, 170))
    img_cells.append(get_rl_image(diagnostico.mapa_calor_xai, 170, 170))
    img_cells.append(get_rl_image(diagnostico.superposicion_xai, 170, 170))

    t_images = Table([titles_cells, img_cells], colWidths=[180, 180, 180])
    t_images.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BACKGROUND', (0, 1), (-1, 1), c_bg_light),
        ('BOX', (0, 0), (-1, -1), 0.5, c_border),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, c_border),
        ('PADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(t_images)
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "<i>Nota sobre XAI: Las áreas resaltadas identifican regiones foliares cuya alteración tuvo mayor impacto "
        "en la reducción de confianza del clasificador. No constituyen un mapeo geométrico exhaustivo de los tejidos necrosados.</i>",
        small_muted
    ))
    story.append(Spacer(1, 14))

    # 4. Distribución de Probabilidades Multiclase
    story.append(Paragraph("Distribución de Probabilidades (XGBoost)", section_heading))
    
    prob_rows = [
        [
            Paragraph("<b>Categoría</b>", small_muted),
            Paragraph("<b>Nombre Científico / Tipo</b>", small_muted),
            Paragraph("<b>Probabilidad</b>", small_muted),
            Paragraph("<b>Porcentaje</b>", small_muted)
        ]
    ]

    if isinstance(diagnostico.probabilidades, dict):
        # Mapeo de nombres
        nombres_es = {
            'Anthracnose': 'Antracnosis',
            'BacterialSpot': 'Mancha bacteriana',
            'Curl': 'Enrollamiento foliar',
            'Healthy': 'Hoja sana',
            'RingSpot': 'Mancha anular'
        }
        for cat_en, p_val in sorted(diagnostico.probabilidades.items(), key=lambda x: x[1], reverse=True):
            cat_es = nombres_es.get(cat_en, cat_en)
            cat_info = get_patologia_info(cat_en)
            p_float = float(p_val)
            is_winner = (cat_en == diagnostico.clase_predicha)
            highlight = "color='#345B48' fontName='Helvetica-Bold'" if is_winner else ""
            
            prob_rows.append([
                Paragraph(f"<font {highlight}>{cat_es} ({cat_en})</font>", body_style),
                Paragraph(f"<i>{cat_info['agente']}</i>", small_muted),
                Paragraph(f"{p_float:.6f}", body_style),
                Paragraph(f"<b>{p_float * 100:.2f}%</b>", body_style)
            ])

    t_probs = Table(prob_rows, colWidths=[160, 200, 90, 90])
    t_probs.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_bg_light),
        ('BOX', (0, 0), (-1, -1), 0.5, c_border),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, c_border),
        ('PADDING', (0, 0), (-1, -1), 4),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(t_probs)
    story.append(Spacer(1, 12))

    # 5. Recomendación Agronómica y Descripción Fitopatológica
    story.append(Paragraph("Descripción Fitopatológica y Manejo Agronómico", section_heading))
    desc_text = f"<b>Sintomatología:</b> {pat_info['descripcion']}<br/><br/><b>Manejo Técnico Sugerido:</b> {pat_info['manejo_recomendado']}"
    t_desc = Table([[Paragraph(desc_text, body_style)]], colWidths=[540])
    t_desc.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), c_bg_light),
        ('BOX', (0, 0), (-1, -1), 0.5, c_border),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(t_desc)
    story.append(Spacer(1, 14))

    # 6. Parámetros Técnicos y Descargo Legal
    story.append(HRFlowable(width="100%", thickness=0.5, color=c_border, spaceBefore=4, spaceAfter=8))
    tech_info = (
        f"<b>Arquitectura:</b> ResNet50 Fine-Tuned (Extractor 2,048 dims) + XGBoost (Clasificador multiclase) | "
        f"<b>Latencia inferencia:</b> {diagnostico.tiempo_inferencia_ms:.1f} ms | "
        f"<b>Latencia XAI:</b> {diagnostico.tiempo_xai_ms:.1f} ms<br/>"
        f"<b>Aviso ético y científico:</b> Documento emitido como soporte visual en el marco de la investigación "
        f"universitaria de tesis. No reemplaza análisis fitopatológico oficial de laboratorio ni la pericia presencial de un profesional calificado."
    )
    story.append(Paragraph(tech_info, small_muted))

    # Construir documento
    doc.build(story)
    buffer.seek(0)
    return buffer

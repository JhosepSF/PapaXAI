"""
Catálogo fitopatológico científico para las enfermedades foliares del cultivo de papaya (Carica papaya L.).
Proporciona descripciones técnicas, agentes etiológicos y recomendaciones agronómicas.
"""

CATALOGO_PATOLOGIAS = {
    'Anthracnose': {
        'nombre_es': 'Antracnosis foliar',
        'nombre_en': 'Anthracnose',
        'agente': 'Colletotrichum gloeosporioides (Penz.) Penz. & Sacc.',
        'tipo_patogeno': 'Hongo ascomiceto',
        'color_estado': '#C05621', # Ámbar oscuro / terracota
        'nivel_alerta': 'Moderado a Alto',
        'descripcion': (
            'Enfermedad fúngica caracterizada por lesiones necróticas circulares a irregulares '
            'con márgenes bien definidos y tonos pardo-rojizos a negruzcos. Con frecuencia se observan '
            'acérvulos concéntricos en el haz de las hojas maduras bajo condiciones de alta humedad relativa.'
        ),
        'sintomas_clave': [
            'Manchas redondeadas u ovaladas de color marrón oscuro con halo clorótico tenue.',
            'Pérdida de área fotosintética activa y perforaciones en centros necróticos senescentes.',
            'Diseminación favorecida por salpicaduras de lluvia y temperaturas entre 24 °C y 28 °C.'
        ],
        'manejo_recomendado': (
            'Eliminación de hojas senescentes infectadas para reducir inóculo. Mejorar la aireación '
            'del dosel mediante podas sanitarias y distancias de siembra adecuadas. En ataques severos, '
            'aplicación preventiva de fungicidas cúpricos o ditiocarbamatos bajo supervisión técnica.'
        )
    },
    'BacterialSpot': {
        'nombre_es': 'Mancha bacteriana foliar',
        'nombre_en': 'Bacterial Spot',
        'agente': 'Pseudomonas carica-papayae / Xanthomonas spp.',
        'tipo_patogeno': 'Bacteria fitopatógena',
        'color_estado': '#9B2C2C', # Rojo carmesí profundo
        'nivel_alerta': 'Alto',
        'descripcion': (
            'Bacteriosis foliar caracterizada por manchas acuosas inicialmente translúcidas (aspecto aceitoso) '
            'que progresan rápidamente a lesiones angulares delimitadas por las nervaduras secundarias, '
            'tornándose pardo-oscuras con un halo amarillento muy pronunciado.'
        ),
        'sintomas_clave': [
            'Lesiones iniciales translúcidas de consistencia acuosa en el envés foliar.',
            'Bordes angulares definidos por nervaduras secundarias y terciarias.',
            'Quemazón foliar y defoliación prematura en períodos cálidos con lluvias intermitentes.'
        ],
        'manejo_recomendado': (
            'Evitar el riego por aspersión que propague bacterias por salpicadura. Desinfección rigurosa '
            'de herramientas de corte con hipoclorito de sodio o amonio cuaternario. Tratamientos preventivos '
            'con formulaciones de cobre bactericida e inducción de resistencia sistémica.'
        )
    },
    'Curl': {
        'nombre_es': 'Enrollamiento foliar',
        'nombre_en': 'Leaf Curl',
        'agente': 'Papaya leaf curl virus (PaLCV) / Begomovirus',
        'tipo_patogeno': 'Virus (Vector: Mosca blanca Bemisia tabaci)',
        'color_estado': '#B7791F', # Ocre dorado
        'nivel_alerta': 'Severo',
        'descripcion': (
            'Virosis sistémica que induce severas anomalías morfogenéticas en la lámina foliar, '
            'incluyendo enroscamiento marginal hacia el haz o el envés, rugosidad pronunciada, '
            'engrosamiento y retorcimiento de nervaduras principales, y enanismo en brotes terminales.'
        ),
        'sintomas_clave': [
            'Curvatura y enroscamiento acentuado de los márgenes foliares hacia arriba o abajo.',
            'Nervaduras abultadas y clorosis intervenal con consistencia quebradiza del limbo.',
            'Detención del desarrollo apical y reducción drástica en la floración.'
        ],
        'manejo_recomendado': (
            'Control integrado del vector transmisor (mosca blanca Bemisia tabaci) mediante trampas '
            'cromáticas amarillas y control biológico. Erradicación inmediata (roguing) de plantas '
            'con sintomatología comprobada para evitar focos de diseminación en el lote.'
        )
    },
    'Healthy': {
        'nombre_es': 'Hoja sana',
        'nombre_en': 'Healthy Leaf',
        'agente': 'Ninguno detectado (Tejido fisiológicamente íntegro)',
        'tipo_patogeno': 'Fisiología óptima',
        'color_estado': '#2F855A', # Verde botánico sereno
        'nivel_alerta': 'Favorable / Normal',
        'descripcion': (
            'Lámina foliar en estado fisiológico óptimo, con pigmentación clorofílica homogénea, '
            'turgencia celular adecuada, nervaduras de aspecto normal y ausencia de lesiones necróticas, '
            'clorosis patológica o deformaciones morfológicas.'
        ),
        'sintomas_clave': [
            'Coloración verde intensa y uniforme en haz y envés.',
            'Lámina palmeada extendida sin distorsiones marginales.',
            'Ausencia de pústulas, manchas acuosas, halos o anillos virales.'
        ],
        'manejo_recomendado': (
            'Mantener el plan de nutrición balanceada (nitrógeno, potasio, boro, zinc) y monitoreo '
            'fitosanitario periódico cada 7 a 14 días para preservación de la sanidad del cultivo.'
        )
    },
    'RingSpot': {
        'nombre_es': 'Mancha anular de la papaya',
        'nombre_en': 'Papaya Ringspot',
        'agente': 'Papaya ringspot virus (PRSV-P) / Potyvirus',
        'tipo_patogeno': 'Virus (Vector: Pulgones / Áfidos)',
        'color_estado': '#7B341E', # Rojo óxido
        'nivel_alerta': 'Crítico',
        'descripcion': (
            'Considerada la enfermedad viral más destructiva en plantaciones de papaya a nivel mundial. '
            'Se manifiesta mediante manchas cloróticas en forma de anillos concéntricos en hojas jóvenes, '
            'mosaico severo, afinamiento de la lámina (apariencia de "cordel") y rayas aceitosas en pecíolos.'
        ),
        'sintomas_clave': [
            'Anillos concéntricos cloróticos y áreas cloróticas circulares en lámina foliar.',
            'Mosaico verde claro/oscuro moteado y severa reducción de la superficie foliar.',
            'Estrías o bandas oscuras con aspecto aceitoso en pecíolos y tallos jóvenes.'
        ],
        'manejo_recomendado': (
            'No existe cura química directa. Erradicación sistemática de plantas infectadas tan pronto '
            'se detecten. Manejo preventivo de poblaciones de pulgones alados mediante barreras vivas '
            '(maíz o sorgo) y empleo de germoplasma con tolerancia regional comprobada.'
        )
    }
}

def get_patologia_info(label_key):
    """Retorna la ficha técnica de la patología o un valor por defecto."""
    return CATALOGO_PATOLOGIAS.get(label_key, {
        'nombre_es': label_key,
        'nombre_en': label_key,
        'agente': 'No especificado',
        'tipo_patogeno': 'No clasificado',
        'color_estado': '#4A5568',
        'nivel_alerta': 'Indeterminado',
        'descripcion': 'Sin información fitopatológica registrada para esta categoría.',
        'sintomas_clave': [],
        'manejo_recomendado': 'Consultar con un ingeniero agrónomo especialista.'
    })

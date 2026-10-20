# PapaXAI — Sistema Inteligente de Diagnóstico Agrícola Foliar y XAI

<div align="center">

![PapaXAI Banner](static/img/papaya_botanical_plate.jpg)

### *"Sistema inteligente de diagnóstico agrícola basado en aprendizaje profundo y XAI para la detección de enfermedades en cultivos de papaya"*

**Cultivo evaluado:** *Carica papaya L.* &nbsp;|&nbsp; **Arquitectura:** ResNet50 Fine-Tuned + XGBoost &nbsp;|&nbsp; **Explicabilidad:** Oclusión Sistemática (7×7)

[![Python 3.12](https://img.shields.io/badge/Python-3.12%2B-345B48?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Django 6.0](https://img.shields.io/badge/Django-6.0-274536?style=flat-square&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![TensorFlow 2.21](https://img.shields.io/badge/TensorFlow-2.21-FF6F00?style=flat-square&logo=tensorflow&logoColor=white)](https://www.tensorflow.org/)
[![XGBoost](https://img.shields.io/badge/XGBoost-Multiclass-C7A776?style=flat-square)](https://xgboost.readthedocs.io/)
[![XAI](https://img.shields.io/badge/XAI-Occlusion%20Sensitivity-78927C?style=flat-square)](https://arxiv.org/abs/1311.2901)
[![ReportLab](https://img.shields.io/badge/Reports-PDF%20ReportLab-C05621?style=flat-square)](https://www.reportlab.com/)

</div>

---

## 1. Resumen Ejecutivo y Propósito

**PapaXAI** es una plataforma web integral desarrollada como producto de investigación y tesis universitaria. Su objetivo es proporcionar a agricultores, extensionistas rurales e investigadores fitopatológicos una herramienta precisa, accesible y científicamente transparente para la detección precoz de anomalías y enfermedades foliares en el cultivo de papaya (*Carica papaya L.*).

A diferencia de las arquitecturas de "caja negra" convencionales, PapaXAI implementa una **arquitectura híbrida desacoplada** complementada con un motor de **Inteligencia Artificial Explicable (XAI)** basado en sensibilidad por oclusión, permitiendo auditar visualmente las regiones foliares que sustentan cada predicción.

---

## 2. Cobertura Fitopatológica

El sistema reconoce y evalúa cinco categorías fundamentales en el ciclo vegetativo del papayo:

| # | Categoría (Modelo) | Denominación en Español | Agente Etiológico / Causa | Nivel de Alerta |
|---|---|---|---|:---:|
| 1 | **Anthracnose** | Antracnosis foliar | *Colletotrichum gloeosporioides* (Hongo) | Moderado / Alto |
| 2 | **BacterialSpot** | Mancha bacteriana | *Pseudomonas carica-papayae* / *Xanthomonas* spp. | Alto |
| 3 | **Curl** | Enrollamiento foliar | *Papaya leaf curl virus* (PaLCV / Begomovirus) | Severo |
| 4 | **Healthy** | Hoja sana | Tejido vegetal fisiológicamente íntegro | Normal |
| 5 | **RingSpot** | Mancha anular de la papaya | *Papaya ringspot virus* (PRSV-P / Potyvirus) | Crítico |

Cada diagnóstico genera una ficha fitosanitaria detallada con la sintomatología típica, epidemiología y recomendaciones de Manejo Integrado de Plagas y Enfermedades (MIP).

---

## 3. Fundamentos de la Arquitectura Híbrida

```text
[ Fotografía Foliar (JPG/PNG/WEBP) ]
                 │
                 ▼
[ Preprocesamiento: 224×224 px Bilinear + Normalización BGR ImageNet ]
                 │
                 ▼
[ Extractor Convolucional: ResNet50 Fine-Tuned (extractor.keras) ]
                 │
                 ▼
[ Vector Latente de Características: 2,048 Dimensiones ]
                 │
                 ▼
[ Clasificador Multiclase: XGBoost 300 Estimadores (classifier.json) ]
                 │
                 ├──────────────────────────────────────────┐
                 ▼                                          ▼
   [ Distribución de Probabilidades ]        [ Módulo de Explicabilidad (XAI) ]
   - Antracnosis (% real)                     - Cuadrícula 7×7 (49 parches de 32×32 px)
   - Mancha bacteriana (% real)               - Perturbación con valor neutro (127.5)
   - Enrollamiento foliar (% real)            - Caída de confianza: ΔP = max(0, P_base - P_ocluida)
   - Hoja sana (% real)                       - Interpolación bicúbica a 224×224 px
   - Mancha anular (% real)                   - Mapa de calor térmico (Jet) + Superposición
```

### ¿Por qué este Ensamble?
- **Extractor ResNet50 (2,048 dims):** Aprovecha sus conexiones residuales (*skip-connections*) para extraer texturas micro-necróticas y bordes angulares sin degradación de gradiente.
- **Clasificador XGBoost:** Ajusta hiperplanos de decisión óptimos sobre el espacio tabular de 2,048 características con regularización $L_1$ y $L_2$, reduciendo drásticamente el sobreajuste y logrando una latencia clasificatoria inferior a **5 milisegundos**.
- **Oclusión vs. Grad-CAM:** Como el clasificador final es tabular (árboles de gradiente potenciados) y no una cabeza densa lineal conectada a la CNN, el uso de Grad-CAM sería teóricamente inválido. La **oclusión sistemática evalúa el comportamiento real del pipeline completo ante perturbaciones espaciales**.

---

## 4. Resultados y Métricas Experimentales (Test Set)

El modelo fue evaluado formalmente sobre el conjunto de prueba independiente de **163 muestras foliares** (sin fuga de datos durante entrenamiento ni búsqueda de hiperparámetros):

| Métrica de Evaluación | Valor Experimental | Descripción Estadística |
|---|:---:|---|
| **Exactitud (*Accuracy*)** | **88.96%** | Proporción global de predicciones correctas (0.88957) |
| **F1-Score Macro** | **88.01%** | Media armónica no ponderada entre clases (0.88010) |
| **F1-Score Ponderado (*Weighted*)** | **88.68%** | F1 ajustado por la distribución de soporte (0.88683) |
| **Precisión Macro** | **89.48%** | Tasa de acierto de predicciones positivas (0.89480) |
| **Sensibilidad / Recall Macro** | **87.75%** | Capacidad de detección de casos reales (0.87749) |
| **AUC-ROC Macro (OvR)** | **0.9864** | Área bajo la curva One-vs-Rest multiclase (0.98639) |
| **Especificidad Macro** | **97.13%** | Capacidad para descartar verdaderos negativos (0.97128) |
| **Intervalo Confianza F1 (95%)** | **[82.60% — 93.08%]** | Estimación no paramétrica por técnica Bootstrap |
| **Latencia de Inferencia Mediana** | **102.08 ms** | Tiempo mediano por muestra en CPU |
| **Latencia Inferencia p95** | **109.26 ms** | Percentil 95 de latencia en CPU |

### Validación Cruzada con Muestras de Test
El sistema replica exactamente los resultados de referencia del pipeline de Colab (`prueba_inferencia.csv`):
- `prueba_01_Anthracnose.jpg`: Predicho **Antracnosis** con **99.2805%** de probabilidad.
- `prueba_02_Healthy.jpg`: Predicho **Hoja sana** con **99.6502%** de probabilidad.

---

## 5. Identidad Visual y Experiencia de Usuario

PapaXAI adopta una **dirección de arte botánica editorial**, inspirada en herbarios y publicaciones científicas clásicas contemporáneas:

- **Paleta Cromática Natural:**
  - Fondo: Marfil cálido `#F7F8F3`
  - Superficies: Blanco suave `#FFFFFF`
  - Verde principal botánico: `#345B48`
  - Verde salvia secundario: `#78927C`
  - Verde claro para acentos: `#E9F0E7`
  - Tipografía de lectura: `#25342B`
  - Líneas divisorias finas: `#DEE5DC`
  - Acento ocre vegetal: `#C7A776`
- **Tipografía:**
  - *Manrope:* Títulos y métricas con geometría contemporánea.
  - *Inter:* Cuerpo de texto y tablas con máxima legibilidad en pantallas móviles y de escritorio.
  - *Newsreader:* Nombres botánicos en latín y citas taxonómicas.
- **Sin Dependencias SPA:** Desarrollado íntegramente con Django Templates, CSS3 modular y Vanilla JavaScript, garantizando carga inmediata y compatibilidad universal.

---

## 6. Estructura del Proyecto

```text
PapaXAI/
├── manage.py
├── .gitignore                        # Reglas de exclusión para Git
├── .env.example                      # Variables de entorno de referencia
├── requirements.txt                  # Dependencias del proyecto
├── README.md                         # Memoria y documentación técnica
├── config/
│   ├── settings.py                   # Configuración de Django, medios, estáticos y seguridad
│   ├── urls.py                       # Enrutador principal de URLs
│   ├── wsgi.py
│   └── asgi.py
├── diagnostico/
│   ├── models.py                     # Modelo Diagnostico con UUID y persistencia de artefactos
│   ├── views.py                      # Controladores: inicio, analizar, resultado, pdf, acerca
│   ├── urls.py                       # Rutas canónicas de la aplicación
│   ├── forms.py                      # Formulario con validación estricta de imágenes (PIL)
│   ├── tests.py                      # Pruebas automatizadas (inferencia, vistas, XAI, PDF)
│   ├── services/
│   │   ├── model_loader.py           # Patrón Singleton thread-safe para extractor y clasificador
│   │   ├── image_processing.py       # Validación de integridad, resize bilinear y preprocess_input
│   │   ├── inference.py              # Inferencia híbrida ResNet50 (2048) + XGBoost
│   │   ├── explainability.py         # Oclusión XAI por lotes (49 regiones) con mapa Jet
│   │   ├── patologias.py             # Diccionario taxonómico de enfermedades y manejo MIP
│   │   └── pdf_report.py             # Generación de reportes técnicos formales con ReportLab
│   └── templates/
│       └── diagnostico/
│           ├── inicio.html           # Pantalla 1: Portada editorial y protocolo de 3 pasos
│           ├── analizar.html         # Pantalla 2: Estudio de carga, drag & drop y selector test
│           ├── resultado.html        # Pantalla 3: Ficha diagnóstica y tríptico visual XAI
│           └── acerca.html           # Pantalla 4: Memoria técnica, diagrama de flujo y métricas
├── templates/
│   └── base.html                     # Plantilla base con encabezado, menú y pie institucional
├── static/
│   ├── css/
│   │   └── papaxai.css               # Sistema de diseño botánico
│   ├── js/
│   │   └── papaxai.js                # Lógica drag-and-drop, vista previa y barra de progreso
│   └── img/
│       └── papaya_botanical_plate.jpg# Lámina botánica científica de Carica papaya L.
├── media/
│   ├── uploads/                      # Fotografías cargadas por usuarios (ignorado en git)
│   ├── xai/                          # Mapas de calor y superposiciones (ignorado en git)
│   └── muestras/                     # Fotos de prueba de la tesis (fotos_test)
└── ml_models/
    ├── extractor.keras               # Red convolucional ResNet50 fine-tuned (95 MB)
    ├── classifier.json               # Clasificador multiclase XGBoost (1 MB)
    ├── config.json                   # Orden estricto de clases e hiperparámetros
    └── metricas_test.json            # Métricas experimentales en el test set
```

---

## 7. Instalación y Puesta en Marcha

### Prerrequisitos
- Python 3.12 (o 3.10 / 3.11).
- Sistema operativo: Windows, Linux o macOS.

### Paso a Paso

1. **Ubicarse en el directorio del proyecto:**
   ```bash
   cd PapaXAI
   ```

2. **Crear y activar el entorno virtual:**
   ```bash
   python -m venv .venv
   
   # En Windows PowerShell:
   .\.venv\Scripts\Activate.ps1
   
   # En Linux / macOS:
   source .venv/bin/activate
   ```

3. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Aplicar las migraciones de base de datos:**
   ```bash
   python manage.py migrate
   ```

5. **Ejecutar la suite de pruebas unitarias:**
   ```bash
   python manage.py test diagnostico
   ```
   *Debe reportar `Ran 4 tests ... OK` confirmando la integridad del pipeline.*

6. **Iniciar el servidor de desarrollo:**
   ```bash
   python manage.py runserver 127.0.0.1:8000
   ```

7. **Acceder a la aplicación:**
   Abrir en cualquier navegador: **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)**

---

## 8. Consideraciones para Entornos Windows (MAX_PATH)

En sistemas Windows, la ruta por defecto tiene un límite heredado de 260 caracteres (`MAX_PATH`). Debido a que las librerías internas de C++ de TensorFlow contienen rutas profundas, puede presentarse el error `[Errno 2] No such file or directory` durante la instalación de paquetes en carpetas anidadas.

### Soluciones recomendadas:

- **Opción A (Recomendada en el entorno virtual):**  
  En el archivo `.venv/pyvenv.cfg`, habilitar:
  ```ini
  include-system-site-packages = true
  ```
  Esto permite que el entorno virtual reutilice el TensorFlow global del sistema (instalado en una ruta más corta) junto a sus propios paquetes aislados.

- **Opción B (Habilitación permanente en Windows):**  
  Abrir PowerShell como Administrador y ejecutar:
  ```powershell
  New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" -Name "LongPathsEnabled" -Value 1 -PropertyType DWORD -Force
  ```

---

## 9. Pantallas del Sistema

### Pantalla 1: Inicio (`/`)
Presentación institucional con lámina botánica de *Carica papaya*, navegación principal, resumen del protocolo de 3 pasos y catálogo de las 5 patologías.

### Pantalla 2: Estudio de Análisis (`/analizar/`)
Área de carga interactiva con Drag & Drop, validación de formato (JPG, PNG, WEBP) y tamaño (<10 MB), galería de muestras del test set para pruebas en un clic, panel lateral de buenas prácticas fotográficas e indicador visual del progreso.

### Pantalla 3: Resultado del Diagnóstico (`/resultado/<uuid>/`)
Identificador único e impredecible UUIDv4 (protección contra IDOR), dictamen fitopatológico principal, barras horizontales de probabilidades multiclase, tríptico visual comparativo XAI (Original, Mapa de calor por oclusión, Superposición) y descarga directa del reporte técnico formal en PDF generado con ReportLab.

### Pantalla 4: Acerca del Sistema (`/acerca-de/`)
Memoria técnica del proyecto de tesis, diagrama interactivo de la arquitectura de datos, fundamentación teórica de la explicabilidad por oclusión sistemática, tabla completa de métricas experimentales del conjunto de prueba y consideraciones agronómicas/éticas.

---

## 10. Aviso Ético y Científico

> [!IMPORTANT]
> **PapaXAI** es una herramienta computacional concebida exclusivamente para apoyo visual y soporte analítico preliminar en el marco de la investigación universitaria. Sus predicciones y mapas de calor **no reemplazan el dictamen de un ingeniero agrónomo colegiado ni las pruebas analíticas fitopatológicas oficiales de laboratorio (aislamiento en medio de cultivo, PCR o serología ELISA)**.

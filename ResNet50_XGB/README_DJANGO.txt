EXPORTACIÓN PARA DJANGO - ResNet50_XGB

Contenido:
 artefactos/extractor.keras         Extractor CNN fine-tuned
 artefactos/classifier.json       Clasificador ya entrenado
 artefactos/config.json             Etiquetas, tamaño y preprocesamiento
 fotos_test/                       Dos fotografías reales extraídas de Test
 fotos_test/fotos_test_manifest.json  Etiquetas originales para probar
 prueba_inferencia.csv              Resultado de verificación (si se ejecutó)

PASOS DE INFERENCIA DJANGO:
 1. Instalar versiones compatibles de TensorFlow/Keras y joblib o xgboost.
 2. Cargar extractor.keras una vez al iniciar el servidor (compile=False).
 3. Cargar clasificador con joblib.load() si es .joblib, o XGBClassifier.load_model() si es .json.
 4. Abrir imagen, convertir a RGB, redimensionar a 224x224 (PIL bilinear),
    convertir a float32 en [0,255].
 5. Preprocesamiento para resnet50: tf.keras.applications.resnet50.preprocess_input.
 6. embedding = extractor.predict(imagen_preprocesada[None,...])
 7. probabilidades = clasificador.predict_proba(embedding)[0]
 8. Reordenar probabilidades con classifier.classes_ a los índices de config.json.
 9. Mostrar etiqueta, probabilidad y advertencia de uso académico.

SEGURIDAD: validar tipo/tamaño de archivo subido en Django. No cargar artefactos
joblib de terceros: el formato permite ejecución arbitraria durante deserialización.
XAI NO INCLUIDA en este paquete: se podrá programar en el backend por oclusión
sobre el pipeline híbrido, sin reentrenar ningún componente.

REPRODUCIBILIDAD: las dos fotos son ejemplos de demostración, no una evaluación
nueva ni sustituyen el informe de Test sobre las 163 imágenes.

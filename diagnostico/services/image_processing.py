"""
Servicio de procesamiento y validación técnica de imágenes foliares.
Garantiza el formato RGB, tamaño 224x224 y preprocesamiento exacto para ResNet50.
"""

import io
from PIL import Image
import numpy as np

ALLOWED_FORMATS = {'JPEG', 'JPG', 'PNG', 'WEBP'}

class ImageProcessingError(Exception):
    """Excepción para errores de validación o conversión de imágenes."""
    pass

def validate_and_load_image(file_obj_or_path):
    """
    Valida la integridad de la imagen y comprueba que sea un archivo visual válido.
    Retorna la imagen en formato PIL.Image en modo RGB y sus dimensiones originales.
    """
    try:
        if hasattr(file_obj_or_path, 'read'):
            file_bytes = file_obj_or_path.read()
            if hasattr(file_obj_or_path, 'seek'):
                file_obj_or_path.seek(0)
            img_io = io.BytesIO(file_bytes)
            
            # Verificación estructural sin decodificar completamente
            with Image.open(img_io) as test_img:
                img_format = (test_img.format or '').upper()
                if img_format not in ALLOWED_FORMATS:
                    raise ImageProcessingError(
                        f"Formato no admitido '{img_format}'. Formatos permitidos: JPG, PNG, WEBP."
                    )
                orig_width, orig_height = test_img.size
            
            # Apertura real para manipulación
            img = Image.open(io.BytesIO(file_bytes))
        else:
            with Image.open(file_obj_or_path) as test_img:
                img_format = (test_img.format or '').upper()
                if img_format not in ALLOWED_FORMATS:
                    raise ImageProcessingError(
                        f"Formato no admitido '{img_format}'. Formatos permitidos: JPG, PNG, WEBP."
                    )
                orig_width, orig_height = test_img.size
            img = Image.open(file_obj_or_path)
            
        # Convertir a RGB (elimina transparencias alfa o paletas indexadas)
        if img.mode != 'RGB':
            img = img.convert('RGB')
            
        return img, (orig_width, orig_height)
        
    except ImageProcessingError:
        raise
    except Exception as e:
        raise ImageProcessingError(f"El archivo proporcionado no es una imagen válida o está dañado: {str(e)}")

def prepare_image_for_inference(pil_img):
    """
    Convierte la imagen PIL a la estructura requerida por el pipeline:
    1. Redimensionar a 224x224 usando interpolación Bilinear (según README_DJANGO.txt)
    2. Convertir a float32 con valores en [0, 255]
    3. Aplicar tf.keras.applications.resnet50.preprocess_input
    Retorna:
    - img_preprocessed_batch: array (1, 224, 224, 3) listo para ResNet50
    - img_arr_224: array (224, 224, 3) en rango [0, 255] para el módulo de oclusión XAI
    - img_resized_pil: PIL.Image de 224x224
    """
    img_resized_pil = pil_img.resize((224, 224), Image.BILINEAR)
    img_arr_224 = np.array(img_resized_pil, dtype=np.float32) # [0, 255]
    
    # Preprocesamiento ResNet50 (convierte RGB a BGR y resta la media de ImageNet)
    import tensorflow as tf
    img_preprocessed = tf.keras.applications.resnet50.preprocess_input(img_arr_224.copy())
    img_preprocessed_batch = np.expand_dims(img_preprocessed, axis=0)
    
    return img_preprocessed_batch, img_arr_224, img_resized_pil

"""
Módulo de Explicabilidad (XAI): Análisis de Sensibilidad por Oclusión.
Evalúa el pipeline completo ResNet50 + XGBoost perturbando parches de 32x32 píxeles
y cuantificando la reducción en la probabilidad de la clase predicha.
"""

import os
import time
import uuid
import logging
from io import BytesIO
from datetime import datetime
from PIL import Image
import numpy as np
import matplotlib
matplotlib.use('Agg') # Backend no interactivo para entornos de servidor
import matplotlib.pyplot as plt

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from .model_loader import get_model_loader

logger = logging.getLogger(__name__)

class OcclusionXAIService:
    def __init__(self, patch_size=32, neutral_value=127.5):
        self.patch_size = patch_size
        self.neutral_value = neutral_value
        self.loader = get_model_loader()

    def generate_explanation(self, img_arr_224, target_class_label, baseline_probability):
        """
        Ejecuta el análisis de oclusión:
        - img_arr_224: np.ndarray (224, 224, 3) con valores en [0, 255]
        - target_class_label: nombre de la clase predicha (ej. 'Anthracnose')
        - baseline_probability: probabilidad predicha sin oclusión
        Retorna:
        - heatmap_rel_path: ruta relativa en media del mapa de calor
        - overlay_rel_path: ruta relativa en media de la superposición
        - latency_ms: tiempo de procesamiento en ms
        """
        t_start = time.perf_counter()
        import tensorflow as tf

        extractor = self.loader.get_extractor()
        classifier = self.loader.get_classifier()
        labels = self.loader.labels
        
        if target_class_label not in labels:
            raise ValueError(f"Clase objetivo '{target_class_label}' no reconocida en {labels}")
            
        target_idx = labels.index(target_class_label)
        classes_order = getattr(classifier, 'classes_', np.arange(len(labels)))
        target_pos = np.where(classes_order == target_idx)[0][0] if target_idx in classes_order else target_idx

        # Parámetros de la cuadrícula
        grid_size = 224 // self.patch_size # 7
        total_patches = grid_size * grid_size # 49

        # Construcción eficiente del lote ocluido (Batch tensor)
        occluded_batch = np.zeros((total_patches, 224, 224, 3), dtype=np.float32)
        patch_coords = []
        
        idx = 0
        for r in range(grid_size):
            for c in range(grid_size):
                y1 = r * self.patch_size
                y2 = min(y1 + self.patch_size, 224)
                x1 = c * self.patch_size
                x2 = min(x1 + self.patch_size, 224)
                
                # Crear copia y sustituir región por valor neutro (gris 127.5)
                occluded_img = img_arr_224.copy()
                occluded_img[y1:y2, x1:x2, :] = self.neutral_value
                
                # Preprocesamiento ResNet50
                occluded_batch[idx] = tf.keras.applications.resnet50.preprocess_input(occluded_img)
                patch_coords.append((r, c))
                idx += 1

        # Inferencia por lotes: extractor ResNet50 + clasificador XGBoost
        batch_features = extractor.predict(occluded_batch, batch_size=total_patches, verbose=0)
        batch_probs = classifier.predict_proba(batch_features)

        # Cálculo de sensibilidad por oclusión:
        # Importancia = max(0, probabilidad_base - probabilidad_ocluida)
        # Una caída drástica indica que el parche contiene rasgos patognomónicos clave
        grid_importance = np.zeros((grid_size, grid_size), dtype=np.float32)
        for i, (r, c) in enumerate(patch_coords):
            prob_occluded = float(batch_probs[i, target_pos])
            drop = baseline_probability - prob_occluded
            grid_importance[r, c] = max(0.0, drop)

        # Normalización min-max del mapa de calor a [0, 1]
        max_val = np.max(grid_importance)
        if max_val > 0.0:
            grid_importance = grid_importance / max_val

        # Interpolación bicúbica a resolución nativa 224x224 para visualización suave
        grid_uint8 = (grid_importance * 255.0).astype(np.uint8)
        heatmap_pil = Image.fromarray(grid_uint8).resize((224, 224), Image.BICUBIC)
        heatmap_norm = np.array(heatmap_pil, dtype=np.float32) / 255.0

        # Aplicación de mapa de color 'jet'
        cmap = matplotlib.colormaps['jet']
        heatmap_rgb = cmap(heatmap_norm)[:, :, :3] # Rango [0, 1]

        # Generación de la superposición (Overlay): 55% imagen original + 45% mapa de calor
        orig_norm = img_arr_224 / 255.0
        overlay_rgb = 0.55 * orig_norm + 0.45 * heatmap_rgb
        overlay_rgb = np.clip(overlay_rgb, 0.0, 1.0)

        # Convertir a imágenes PIL en uint8
        heatmap_img = Image.fromarray((heatmap_rgb * 255.0).astype(np.uint8))
        overlay_img = Image.fromarray((overlay_rgb * 255.0).astype(np.uint8))

        # Guardar en Django storage
        today = datetime.now().strftime('%Y/%m/%d')
        unique_token = uuid.uuid4().hex[:12]
        
        heatmap_filename = f"xai/{today}/heatmap_{unique_token}.png"
        overlay_filename = f"xai/{today}/overlay_{unique_token}.png"

        # Guardar mapa de calor
        h_io = BytesIO()
        heatmap_img.save(h_io, format='PNG')
        heatmap_path = default_storage.save(heatmap_filename, ContentFile(h_io.getvalue()))

        # Guardar superposición
        o_io = BytesIO()
        overlay_img.save(o_io, format='PNG')
        overlay_path = default_storage.save(overlay_filename, ContentFile(o_io.getvalue()))

        t_end = time.perf_counter()
        latency_ms = (t_end - t_start) * 1000.0

        logger.info(
            "Explicación XAI generada en %.2f ms para clase '%s' (puntos evaluados: %d)",
            latency_ms, target_class_label, total_patches
        )

        return {
            'heatmap_path': heatmap_path,
            'overlay_path': overlay_path,
            'latency_ms': round(latency_ms, 2),
            'grid_shape': [grid_size, grid_size],
            'max_drop': float(max_val)
        }

def get_xai_service():
    return OcclusionXAIService()

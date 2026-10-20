"""
Servicio de inferencia para el modelo híbrido ResNet50 + XGBoost.
Extrae embeddings de 2,048 dimensiones y predice las probabilidades multiclase.
"""

import time
import logging
import numpy as np
from .model_loader import get_model_loader

logger = logging.getLogger(__name__)

class InferenceService:
    def __init__(self):
        self.loader = get_model_loader()

    def predict(self, preprocessed_batch):
        """
        Ejecuta la inferencia híbrida:
        1. Extracción de características visuales con ResNet50 fine-tuned (vector de 2048 dims)
        2. Clasificación multiclase con XGBoost
        3. Mapeo riguroso de probabilidades y clases según config.json
        Retorna diccionario con resultados estructurados y tiempos.
        """
        t_start = time.perf_counter()

        extractor = self.loader.get_extractor()
        classifier = self.loader.get_classifier()
        labels = self.loader.labels
        labels_es = self.loader.labels_es

        # 1. Extracción de características
        features = extractor.predict(preprocessed_batch, verbose=0)
        
        # Validar dimensión
        if features.shape[-1] != 2048:
            raise ValueError(f"Dimensión de características esperada 2048, obtenida {features.shape[-1]}")

        # 2. Inferencia XGBoost
        raw_probs = classifier.predict_proba(features)[0]

        # 3. Mapeo con classifier.classes_
        # En caso de que classes_ tenga un orden específico:
        classes_order = getattr(classifier, 'classes_', np.arange(len(labels)))
        
        ordered_probs = {}
        ordered_probs_list = []
        
        for idx, label in enumerate(labels):
            # Obtener la posición de la clase en classes_
            if idx in classes_order:
                pos = np.where(classes_order == idx)[0][0]
                prob_val = float(raw_probs[pos])
            else:
                prob_val = float(raw_probs[idx])
            ordered_probs[label] = prob_val
            ordered_probs_list.append({
                'label': label,
                'label_es': self.loader.get_label_es(label),
                'probability': prob_val,
                'percentage': round(prob_val * 100, 2)
            })

        # 4. Determinar la clase ganadora
        max_idx = int(np.argmax([item['probability'] for item in ordered_probs_list]))
        winning_item = ordered_probs_list[max_idx]
        
        t_end = time.perf_counter()
        latency_ms = (t_end - t_start) * 1000.0

        # Ordenar lista de probabilidades de mayor a menor para visualización ordenada
        ordered_by_prob = sorted(ordered_probs_list, key=lambda x: x['probability'], reverse=True)

        return {
            'predicted_class': winning_item['label'],
            'predicted_class_es': winning_item['label_es'],
            'max_probability': winning_item['probability'],
            'max_percentage': winning_item['percentage'],
            'probabilities_dict': ordered_probs,
            'probabilities_list': ordered_probs_list,
            'probabilities_sorted': ordered_by_prob,
            'latency_ms': round(latency_ms, 2),
            'feature_dim': features.shape[-1],
        }

def get_inference_service():
    return InferenceService()

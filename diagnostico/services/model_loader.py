"""
Servicio de carga única (Singleton) de los artefactos del modelo ResNet50 + XGBoost.
Evita recargar los pesos en cada petición y mantiene la coherencia de clases.
"""

import os
import json
import logging
import threading
from django.conf import settings
import numpy as np

logger = logging.getLogger(__name__)

class ModelLoader:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(ModelLoader, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if getattr(self, '_initialized', False):
            return
        
        self.extractor = None
        self.classifier = None
        self.config = {}
        self.metrics = {}
        self.labels = []
        self.labels_es = []
        self.label_to_id = {}
        self.probability_order = []
        self.models_dir = getattr(settings, 'ML_MODELS_DIR', None)
        
        self._load_config()
        self._initialized = True

    def _load_config(self):
        if not self.models_dir:
            return
        config_path = os.path.join(self.models_dir, 'config.json')
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            self.labels = self.config.get('labels', [])
            self.labels_es = self.config.get('labels_es', [])
            self.label_to_id = self.config.get('label_to_id', {})
            self.probability_order = self.config.get('probability_order', self.labels)
            logger.info("Configuración de clases y pipeline cargada exitosamente.")

        metrics_path = os.path.join(self.models_dir, 'metricas_test.json')
        if os.path.exists(metrics_path):
            with open(metrics_path, 'r', encoding='utf-8') as f:
                self.metrics = json.load(f)

    def get_extractor(self):
        """Carga el extractor ResNet50 de manera perezosa y segura."""
        if self.extractor is None:
            with self._lock:
                if self.extractor is None:
                    import tensorflow as tf
                    extractor_path = os.path.join(self.models_dir, 'extractor.keras')
                    logger.info("Cargando extractor CNN fine-tuned: %s", extractor_path)
                    self.extractor = tf.keras.models.load_model(extractor_path, compile=False)
                    logger.info("Extractor ResNet50 cargado en memoria exitosamente.")
        return self.extractor

    def get_classifier(self):
        """Carga el clasificador XGBoost de manera perezosa y segura."""
        if self.classifier is None:
            with self._lock:
                if self.classifier is None:
                    import xgboost as xgb
                    classifier_path = os.path.join(self.models_dir, 'classifier.json')
                    logger.info("Cargando clasificador XGBoost: %s", classifier_path)
                    clf = xgb.XGBClassifier()
                    clf.load_model(classifier_path)
                    self.classifier = clf
                    logger.info("Clasificador XGBoost cargado exitosamente.")
        return self.classifier

    def get_config(self):
        return self.config

    def get_metrics(self):
        return self.metrics

    def get_label_es(self, label_en):
        """Traduce una etiqueta en inglés a su denominación en español."""
        if label_en in self.labels:
            idx = self.labels.index(label_en)
            if idx < len(self.labels_es):
                return self.labels_es[idx]
        return label_en

# Helper para instanciación global
def get_model_loader():
    return ModelLoader()

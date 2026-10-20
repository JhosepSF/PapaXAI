"""
Modelos de datos para el sistema PapaXAI.
Almacena diagnósticos foliares, probabilidades del clasificador y artefactos visuales XAI.
"""

import uuid
from django.db import models
from django.urls import reverse
from .services.patologias import get_patologia_info

class Diagnostico(models.Model):
    """
    Registro inmutable de un diagnóstico foliar generado por PapaXAI.
    Utiliza UUIDv4 como clave primaria para evitar la enumeración maliciosa (IDOR).
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="Identificador único (UUID)"
    )
    imagen_original = models.ImageField(
        upload_to='uploads/%Y/%m/%d/',
        verbose_name="Fotografía original"
    )
    nombre_archivo_original = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Nombre original del archivo"
    )
    peso_archivo_kb = models.FloatField(
        default=0.0,
        verbose_name="Peso del archivo (KB)"
    )
    dimensiones_originales = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Dimensiones originales (WxH)"
    )
    clase_predicha = models.CharField(
        max_length=100,
        verbose_name="Clase predicha (Inglés)"
    )
    clase_predicha_es = models.CharField(
        max_length=100,
        verbose_name="Clase predicha (Español)"
    )
    probabilidad_maxima = models.FloatField(
        verbose_name="Probabilidad máxima devuelta"
    )
    probabilidades = models.JSONField(
        default=dict,
        verbose_name="Distribución completa de probabilidades"
    )
    mapa_calor_xai = models.ImageField(
        upload_to='xai/%Y/%m/%d/',
        blank=True,
        null=True,
        verbose_name="Mapa de calor por oclusión"
    )
    superposicion_xai = models.ImageField(
        upload_to='xai/%Y/%m/%d/',
        blank=True,
        null=True,
        verbose_name="Superposición explicativa (Overlay)"
    )
    tiempo_inferencia_ms = models.FloatField(
        default=0.0,
        verbose_name="Tiempo de inferencia (ms)"
    )
    tiempo_xai_ms = models.FloatField(
        default=0.0,
        verbose_name="Tiempo de generación XAI (ms)"
    )
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha y hora de diagnóstico"
    )
    notas_fitopatologicas = models.TextField(
        blank=True,
        verbose_name="Observaciones fitopatológicas"
    )

    class Meta:
        verbose_name = "Diagnóstico Foliar"
        verbose_name_plural = "Diagnósticos Foliares"
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"{self.clase_predicha_es} ({self.porcentaje_confianza}%) - {self.fecha_creacion.strftime('%Y-%m-%d %H:%M')}"

    @property
    def porcentaje_confianza(self):
        return round(self.probabilidad_maxima * 100, 2)

    @property
    def info_patologia(self):
        return get_patologia_info(self.clase_predicha)

    def get_absolute_url(self):
        return reverse('diagnostico:resultado', kwargs={'pk': str(self.id)})

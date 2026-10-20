"""
Rutas URL para la aplicación de diagnóstico de PapaXAI.
"""

from django.urls import path
from . import views

app_name = 'diagnostico'

urlpatterns = [
    path('', views.inicio_view, name='inicio'),
    path('analizar/', views.analizar_view, name='analizar'),
    path('resultado/<uuid:pk>/', views.resultado_view, name='resultado'),
    path('resultado/<uuid:pk>/pdf/', views.descargar_pdf_view, name='descargar_pdf'),
    path('acerca-de/', views.acerca_view, name='acerca'),
]

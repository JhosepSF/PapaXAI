"""
Formularios para la carga y validación de imágenes foliares en PapaXAI.
"""

from django import forms
from django.core.exceptions import ValidationError
from .services.image_processing import validate_and_load_image, ImageProcessingError

MAX_FILE_SIZE_MB = 10
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'webp'}

class DiagnosticoUploadForm(forms.Form):
    """
    Formulario estricto para recepción de fotografías foliares.
    Valida extensión, peso, cabecera de archivo y decodificación PIL.
    """
    imagen = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'id': 'file-input',
            'class': 'hidden-file-input',
            'accept': '.jpg,.jpeg,.png,.webp,image/jpeg,image/png,image/webp'
        }),
        error_messages={
            'invalid_image': 'El archivo subido no es una imagen válida o está dañado.'
        }
    )
    
    muestra_seleccionada = forms.CharField(
        required=False,
        widget=forms.HiddenInput()
    )

    def clean(self):
        cleaned_data = super().clean()
        imagen = cleaned_data.get('imagen')
        muestra = cleaned_data.get('muestra_seleccionada')

        if not imagen and not muestra:
            raise ValidationError('Por favor selecciona una fotografía de hoja de papaya o utiliza una imagen de prueba.')

        if imagen:
            # 1. Validar tamaño en bytes
            if imagen.size > MAX_FILE_SIZE_BYTES:
                raise ValidationError(
                    f"El archivo pesa {imagen.size / (1024 * 1024):.1f} MB, superando el límite de {MAX_FILE_SIZE_MB} MB."
                )

            # 2. Validar extensión de archivo
            ext = (imagen.name.split('.')[-1] if '.' in imagen.name else '').lower()
            if ext not in ALLOWED_EXTENSIONS:
                raise ValidationError(
                    f"Extensión .{ext} no permitida. Formatos válidos: JPG, JPEG, PNG, WEBP."
                )

            # 3. Validación técnica profunda de integridad
            try:
                # Validar con PIL
                validate_and_load_image(imagen)
            except ImageProcessingError as e:
                raise ValidationError(str(e))
            except Exception as e:
                raise ValidationError(f"Error al procesar la estructura de la imagen: {str(e)}")

        return cleaned_data

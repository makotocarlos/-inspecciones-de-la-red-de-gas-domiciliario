"""
Custom validators for data validation
"""
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.conf import settings
# import magic  # Temporarily disabled - requires libmagic installation
import os


def validate_file_size(file):
    """
    Validate that file size is within allowed limit
    """
    if file.size > settings.MAX_UPLOAD_SIZE:
        raise ValidationError(
            f'El tamaño del archivo no puede exceder {settings.MAX_UPLOAD_SIZE / 1024 / 1024}MB'
        )


def validate_image_file(file):
    """
    Validate that uploaded file is a valid image
    """
    validate_file_size(file)
    
    # Check file extension
    ext = os.path.splitext(file.name)[1].lower()
    allowed_extensions = ['.jpg', '.jpeg', '.png', '.webp']
    
    if ext not in allowed_extensions:
        raise ValidationError(
            f'Formato de imagen no permitido. Use: {", ".join(allowed_extensions)}'
        )
    
    # Check MIME type (disabled - requires libmagic)
    # try:
    #     mime = magic.from_buffer(file.read(1024), mime=True)
    #     file.seek(0)
    #     
    #     if mime not in settings.ALLOWED_IMAGE_TYPES:
    #         raise ValidationError('El archivo no es una imagen válida')
    # except Exception:
    #     pass


def validate_pdf_file(file):
    """
    Validate that uploaded file is a valid PDF
    """
    validate_file_size(file)
    
    # Check file extension
    ext = os.path.splitext(file.name)[1].lower()
    if ext != '.pdf':
        raise ValidationError('El archivo debe ser un PDF')
    
    # Check MIME type (disabled - requires libmagic)
    # try:
    #     mime = magic.from_buffer(file.read(1024), mime=True)
    #     file.seek(0)
    #     
    #     if mime not in settings.ALLOWED_DOCUMENT_TYPES:
    #         raise ValidationError('El archivo no es un PDF válido')
    # except Exception:
    #     pass


def validate_dni(value):
    """
    Validate Colombian DNI (Cédula de Ciudadanía)
    """
    if not value.isdigit():
        raise ValidationError('El DNI debe contener solo números')
    
    if len(value) < 6 or len(value) > 10:
        raise ValidationError('El DNI debe tener entre 6 y 10 dígitos')


def validate_license_number(value):
    """
    Validate inspector license number
    """
    if len(value) < 5:
        raise ValidationError('El número de licencia debe tener al menos 5 caracteres')

"""
Advanced Error Handling and Custom Exceptions
Professional error management for enterprise-grade applications.
"""

from rest_framework.views import exception_handler
from rest_framework.exceptions import APIException
from rest_framework import status
from django.core.exceptions import ValidationError as DjangoValidationError
from django.http import Http404
from django.db import DatabaseError, IntegrityError
import logging
import traceback

logger = logging.getLogger('django.request')


class BaseAPIException(APIException):
    """Base exception class for custom API exceptions."""
    
    def __init__(self, detail=None, code=None, status_code=None):
        super().__init__(detail, code)
        if status_code:
            self.status_code = status_code


class BusinessLogicError(BaseAPIException):
    """Raised when business logic validation fails."""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Business logic validation failed'
    default_code = 'business_logic_error'


class ResourceNotFoundError(BaseAPIException):
    """Raised when a requested resource is not found."""
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'The requested resource was not found'
    default_code = 'resource_not_found'


class PermissionDeniedError(BaseAPIException):
    """Raised when user lacks required permissions."""
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = 'You do not have permission to perform this action'
    default_code = 'permission_denied'


class AuthenticationFailedError(BaseAPIException):
    """Raised when authentication fails."""
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = 'Authentication failed'
    default_code = 'authentication_failed'


class ValidationError(BaseAPIException):
    """Raised when data validation fails."""
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    default_detail = 'Validation failed'
    default_code = 'validation_error'


class ConflictError(BaseAPIException):
    """Raised when there's a resource conflict."""
    status_code = status.HTTP_409_CONFLICT
    default_detail = 'Resource conflict detected'
    default_code = 'conflict_error'


class RateLimitExceededError(BaseAPIException):
    """Raised when rate limit is exceeded."""
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    default_detail = 'Rate limit exceeded'
    default_code = 'rate_limit_exceeded'


class ServiceUnavailableError(BaseAPIException):
    """Raised when a service is temporarily unavailable."""
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = 'Service temporarily unavailable'
    default_code = 'service_unavailable'


class InternalServerError(BaseAPIException):
    """Raised for internal server errors."""
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = 'An internal server error occurred'
    default_code = 'internal_server_error'


# Domain-specific exceptions

class InspectionError(BusinessLogicError):
    """Base exception for inspection-related errors."""
    default_detail = 'Inspection operation failed'
    default_code = 'inspection_error'


class InspectionNotScheduledError(InspectionError):
    """Raised when attempting operation on unscheduled inspection."""
    default_detail = 'Inspection has not been scheduled yet'
    default_code = 'inspection_not_scheduled'


class InspectionAlreadyCompletedError(InspectionError):
    """Raised when attempting to modify completed inspection."""
    default_detail = 'Inspection has already been completed'
    default_code = 'inspection_already_completed'


class InspectorNotAssignedError(InspectionError):
    """Raised when inspector is required but not assigned."""
    default_detail = 'No inspector has been assigned to this inspection'
    default_code = 'inspector_not_assigned'


class ReportGenerationError(BaseAPIException):
    """Raised when report generation fails."""
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = 'Failed to generate report'
    default_code = 'report_generation_failed'


class EmailSendError(BaseAPIException):
    """Raised when email sending fails."""
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = 'Failed to send email'
    default_code = 'email_send_failed'


class FileUploadError(BaseAPIException):
    """Raised when file upload fails."""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'File upload failed'
    default_code = 'file_upload_failed'


class InvalidFileTypeError(FileUploadError):
    """Raised when uploaded file type is invalid."""
    default_detail = 'Invalid file type'
    default_code = 'invalid_file_type'


class FileSizeExceededError(FileUploadError):
    """Raised when uploaded file is too large."""
    default_detail = 'File size exceeds maximum allowed'
    default_code = 'file_size_exceeded'


def custom_exception_handler(exc, context):
    """
    Custom exception handler for DRF.
    Provides enhanced error responses with detailed information.
    """
    from django.utils import timezone
    
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)
    
    # Get the request object
    request = context.get('request')
    view = context.get('view')
    
    # Log the exception
    log_exception(exc, request, view)
    
    # If response is None, handle unhandled exceptions
    if response is None:
        response = handle_unhandled_exception(exc, request)
    else:
        # Enhance the response with additional information
        response = enhance_error_response(response, exc, request)
    
    return response


def enhance_error_response(response, exc, request):
    """
    Enhance error response with additional context.
    """
    from django.utils import timezone
    
    # Get error details
    error_code = getattr(exc, 'default_code', 'error')
    error_message = str(exc.detail) if hasattr(exc, 'detail') else str(exc)
    
    # Build enhanced response
    response.data = {
        'success': False,
        'error': {
            'code': error_code,
            'message': error_message,
            'details': response.data if isinstance(response.data, dict) else {'detail': response.data},
        },
        'meta': {
            'timestamp': timezone.now().isoformat(),
            'path': request.path if request else None,
            'method': request.method if request else None,
        }
    }
    
    return response


def handle_unhandled_exception(exc, request):
    """
    Handle exceptions not caught by DRF's exception handler.
    """
    from rest_framework.response import Response
    from django.utils import timezone
    from django.conf import settings
    
    # Determine status code and error message
    if isinstance(exc, Http404):
        status_code = status.HTTP_404_NOT_FOUND
        error_message = 'Resource not found'
        error_code = 'not_found'
    elif isinstance(exc, DjangoValidationError):
        status_code = status.HTTP_400_BAD_REQUEST
        error_message = 'Validation error'
        error_code = 'validation_error'
    elif isinstance(exc, IntegrityError):
        status_code = status.HTTP_409_CONFLICT
        error_message = 'Database integrity error - possible duplicate'
        error_code = 'integrity_error'
    elif isinstance(exc, DatabaseError):
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        error_message = 'Database error'
        error_code = 'database_error'
    else:
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        error_message = 'An unexpected error occurred'
        error_code = 'internal_server_error'
    
    # Build error response
    error_data = {
        'success': False,
        'error': {
            'code': error_code,
            'message': error_message,
            'details': str(exc) if settings.DEBUG else {},
        },
        'meta': {
            'timestamp': timezone.now().isoformat(),
            'path': request.path if request else None,
            'method': request.method if request else None,
        }
    }
    
    # Add stack trace in debug mode
    if settings.DEBUG:
        error_data['error']['traceback'] = traceback.format_exc()
    
    return Response(error_data, status=status_code)


def log_exception(exc, request, view):
    """
    Log exception details for debugging and monitoring.
    """
    error_info = {
        'exception_type': type(exc).__name__,
        'exception_message': str(exc),
        'path': request.path if request else 'Unknown',
        'method': request.method if request else 'Unknown',
        'view': view.__class__.__name__ if view else 'Unknown',
        'user': str(request.user) if request and hasattr(request, 'user') else 'Anonymous',
    }
    
    # Log error
    if isinstance(exc, (InternalServerError, DatabaseError)):
        logger.error(
            f"Server Error: {error_info['exception_type']} - {error_info['exception_message']}",
            extra=error_info,
            exc_info=True
        )
    elif isinstance(exc, (ValidationError, BusinessLogicError)):
        logger.warning(
            f"Validation Error: {error_info['exception_type']} - {error_info['exception_message']}",
            extra=error_info
        )
    else:
        logger.info(
            f"API Exception: {error_info['exception_type']} - {error_info['exception_message']}",
            extra=error_info
        )


class ErrorContext:
    """
    Context manager for handling errors in code blocks.
    
    Usage:
        with ErrorContext('User creation'):
            user = User.objects.create(...)
    """
    
    def __init__(self, operation_name: str, raise_exception: bool = True):
        self.operation_name = operation_name
        self.raise_exception = raise_exception
        self.error = None
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.error = exc_val
            logger.error(
                f"Error in {self.operation_name}: {exc_type.__name__} - {exc_val}",
                exc_info=True
            )
            
            if not self.raise_exception:
                return True  # Suppress the exception
        
        return False


def handle_errors(operation_name: str = None):
    """
    Decorator for error handling in functions.
    
    Usage:
        @handle_errors('Create user')
        def create_user(data):
            ...
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            op_name = operation_name or func.__name__
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(
                    f"Error in {op_name}: {type(e).__name__} - {str(e)}",
                    exc_info=True
                )
                raise
        return wrapper
    return decorator


# Error messages catalog (i18n ready)
ERROR_MESSAGES = {
    # Authentication
    'auth_failed': 'Las credenciales proporcionadas son inválidas',
    'auth_required': 'Se requiere autenticación para acceder a este recurso',
    'token_expired': 'El token de autenticación ha expirado',
    'token_invalid': 'El token de autenticación es inválido',
    
    # Permissions
    'permission_denied': 'No tiene permisos para realizar esta acción',
    'admin_required': 'Se requieren privilegios de administrador',
    'inspector_required': 'Esta acción solo está disponible para inspectores',
    
    # Validation
    'required_field': 'Este campo es obligatorio',
    'invalid_format': 'El formato del campo es inválido',
    'invalid_choice': 'Opción inválida seleccionada',
    'duplicate_entry': 'Ya existe un registro con estos datos',
    
    # Inspections
    'inspection_not_found': 'La inspección solicitada no existe',
    'inspection_not_scheduled': 'La inspección no ha sido programada',
    'inspection_completed': 'La inspección ya ha sido completada',
    'inspector_not_assigned': 'No hay inspector asignado a esta inspección',
    'cannot_modify_completed': 'No se puede modificar una inspección completada',
    
    # Reports
    'report_generation_failed': 'Error al generar el reporte',
    'report_not_found': 'El reporte solicitado no existe',
    
    # Files
    'file_too_large': 'El archivo excede el tamaño máximo permitido',
    'invalid_file_type': 'Tipo de archivo no permitido',
    'upload_failed': 'Error al cargar el archivo',
    
    # General
    'server_error': 'Error interno del servidor',
    'service_unavailable': 'Servicio temporalmente no disponible',
    'rate_limit_exceeded': 'Ha excedido el límite de solicitudes',
}


def get_error_message(key: str, default: str = None) -> str:
    """
    Get error message from catalog.
    
    Args:
        key: Error message key
        default: Default message if key not found
    
    Returns:
        Error message string
    """
    return ERROR_MESSAGES.get(key, default or 'Error desconocido')

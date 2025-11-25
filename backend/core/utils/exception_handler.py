"""
Custom Exception Handler for DRF
Enhanced error handling with detailed responses and professional logging.
"""

from rest_framework.views import exception_handler as drf_exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError as DjangoValidationError
from django.http import Http404
from django.db import DatabaseError, IntegrityError
from django.utils import timezone
import logging
import traceback
from django.conf import settings

logger = logging.getLogger('django.request')


def custom_exception_handler(exc, context):
    """
    Custom exception handler providing professional error responses.
    
    Features:
    - Standardized error format
    - Detailed logging
    - Debug information in development
    - Security-safe error messages in production
    - Request context preservation
    """
    # Get the standard exception response
    response = drf_exception_handler(exc, context)
    
    # Get request and view context
    request = context.get('request')
    view = context.get('view')
    
    # Log the exception
    log_exception(exc, request, view)
    
    if response is not None:
        # Enhance DRF's error response
        custom_response_data = {
            'success': False,
            'error': {
                'code': get_error_code(exc),
                'message': get_error_message(response.data),
                'details': response.data,
            },
            'meta': {
                'timestamp': timezone.now().isoformat(),
                'path': request.path if request else None,
                'method': request.method if request else None,
            }
        }
        
        # Add debug information in development
        if settings.DEBUG:
            custom_response_data['debug'] = {
                'exception_type': type(exc).__name__,
                'exception_message': str(exc),
                'view': view.__class__.__name__ if view else None,
            }
        
        response.data = custom_response_data
        
    else:
        # Handle exceptions not caught by DRF
        response = handle_generic_exception(exc, request)
    
    return response


def handle_generic_exception(exc, request):
    """
    Handle exceptions not handled by DRF's default handler.
    """
    # Determine appropriate status code and message
    if isinstance(exc, Http404):
        status_code = status.HTTP_404_NOT_FOUND
        error_code = 'not_found'
        error_message = 'El recurso solicitado no fue encontrado'
    elif isinstance(exc, DjangoValidationError):
        status_code = status.HTTP_400_BAD_REQUEST
        error_code = 'validation_error'
        error_message = 'Error de validación en los datos proporcionados'
    elif isinstance(exc, IntegrityError):
        status_code = status.HTTP_409_CONFLICT
        error_code = 'integrity_error'
        error_message = 'Conflicto de integridad - El registro ya existe'
    elif isinstance(exc, DatabaseError):
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        error_code = 'database_error'
        error_message = 'Error de base de datos'
    elif isinstance(exc, PermissionError):
        status_code = status.HTTP_403_FORBIDDEN
        error_code = 'permission_denied'
        error_message = 'No tiene permisos para realizar esta acción'
    else:
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        error_code = 'internal_error'
        error_message = 'Ha ocurrido un error interno del servidor'
    
    # Build error response
    error_data = {
        'success': False,
        'error': {
            'code': error_code,
            'message': error_message,
            'details': {
                'exception': type(exc).__name__,
                'message': str(exc) if settings.DEBUG else None,
            }
        },
        'meta': {
            'timestamp': timezone.now().isoformat(),
            'path': request.path if request else None,
            'method': request.method if request else None,
        }
    }
    
    # Add full traceback in debug mode
    if settings.DEBUG:
        error_data['debug'] = {
            'traceback': traceback.format_exc(),
            'exception_type': type(exc).__name__,
            'exception_message': str(exc),
        }
    
    return Response(error_data, status=status_code)


def get_error_code(exc):
    """Extract error code from exception."""
    if hasattr(exc, 'default_code'):
        return exc.default_code
    elif hasattr(exc, 'code'):
        return exc.code
    else:
        return type(exc).__name__().lower().replace('exception', '').replace('error', '')


def get_error_message(data):
    """Extract user-friendly error message from response data."""
    if isinstance(data, dict):
        if 'detail' in data:
            return str(data['detail'])
        elif 'non_field_errors' in data:
            return str(data['non_field_errors'][0]) if data['non_field_errors'] else 'Error de validación'
        else:
            # Get first error from any field
            for key, value in data.items():
                if isinstance(value, list) and value:
                    return f"{key}: {str(value[0])}"
            return 'Error de validación en los datos proporcionados'
    elif isinstance(data, list):
        return str(data[0]) if data else 'Error en la solicitud'
    else:
        return str(data)


def log_exception(exc, request, view):
    """
    Log exception with context for debugging and monitoring.
    """
    # Build context information
    context_info = {
        'exception_type': type(exc).__name__,
        'exception_message': str(exc),
        'path': request.path if request else 'N/A',
        'method': request.method if request else 'N/A',
        'view': view.__class__.__name__ if view else 'N/A',
        'user': str(request.user) if request and hasattr(request, 'user') else 'Anonymous',
        'ip_address': get_client_ip(request) if request else 'N/A',
    }
    
    # Categorize and log appropriately
    if is_server_error(exc):
        logger.error(
            f"SERVER ERROR [{context_info['exception_type']}]: {context_info['exception_message']}",
            extra=context_info,
            exc_info=True
        )
    elif is_client_error(exc):
        logger.warning(
            f"CLIENT ERROR [{context_info['exception_type']}]: {context_info['exception_message']}",
            extra=context_info
        )
    else:
        logger.info(
            f"API EXCEPTION [{context_info['exception_type']}]: {context_info['exception_message']}",
            extra=context_info
        )


def is_server_error(exc):
    """Check if exception is a server error (5xx)."""
    if hasattr(exc, 'status_code'):
        return 500 <= exc.status_code < 600
    return isinstance(exc, (DatabaseError, Exception))


def is_client_error(exc):
    """Check if exception is a client error (4xx)."""
    if hasattr(exc, 'status_code'):
        return 400 <= exc.status_code < 500
    return isinstance(exc, (DjangoValidationError, ValueError))


def get_client_ip(request):
    """Extract client IP from request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR', 'Unknown')
    return ip

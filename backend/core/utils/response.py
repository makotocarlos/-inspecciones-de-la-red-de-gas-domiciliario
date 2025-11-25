"""
Standardized API response utilities
"""
from rest_framework.response import Response
from rest_framework import status


class APIResponse:
    """
    Standard API response format
    """
    
    @staticmethod
    def success(data=None, message='Operación exitosa', status_code=status.HTTP_200_OK):
        """
        Return success response
        """
        return Response({
            'success': True,
            'message': message,
            'data': data
        }, status=status_code)
    
    @staticmethod
    def created(data=None, message='Recurso creado exitosamente'):
        """
        Return created response
        """
        return APIResponse.success(data, message, status.HTTP_201_CREATED)
    
    @staticmethod
    def error(message='Error en la operación', details=None, status_code=status.HTTP_400_BAD_REQUEST):
        """
        Return error response
        """
        return Response({
            'success': False,
            'error': {
                'message': message,
                'details': details or {},
                'code': status_code
            }
        }, status=status_code)
    
    @staticmethod
    def not_found(message='Recurso no encontrado'):
        """
        Return 404 response
        """
        return APIResponse.error(message, status_code=status.HTTP_404_NOT_FOUND)
    
    @staticmethod
    def unauthorized(message='No autorizado'):
        """
        Return 401 response
        """
        return APIResponse.error(message, status_code=status.HTTP_401_UNAUTHORIZED)
    
    @staticmethod
    def forbidden(message='Acceso denegado'):
        """
        Return 403 response
        """
        return APIResponse.error(message, status_code=status.HTTP_403_FORBIDDEN)

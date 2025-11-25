"""
API Response Standards and Utilities
Professional API response formatting and error handling.
"""

from rest_framework.response import Response
from rest_framework import status
from django.core.paginator import Paginator
from typing import Any, Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class APIResponse:
    """
    Standardized API response wrapper for consistent response format.
    
    Response Format:
    {
        "success": true/false,
        "message": "Human readable message",
        "data": {...} or [...],
        "errors": {...},
        "meta": {
            "timestamp": "2024-01-01T00:00:00Z",
            "request_id": "uuid",
            "pagination": {...}
        }
    }
    """
    
    @staticmethod
    def success(
        data: Any = None,
        message: str = "Operation successful",
        status_code: int = status.HTTP_200_OK,
        meta: Optional[Dict] = None
    ) -> Response:
        """
        Return a successful API response.
        
        Args:
            data: Response payload
            message: Success message
            status_code: HTTP status code
            meta: Additional metadata
        
        Returns:
            DRF Response object
        """
        from django.utils import timezone
        
        response_data = {
            "success": True,
            "message": message,
            "data": data,
            "meta": {
                "timestamp": timezone.now().isoformat(),
                **(meta or {})
            }
        }
        
        return Response(response_data, status=status_code)
    
    @staticmethod
    def error(
        message: str = "An error occurred",
        errors: Optional[Dict] = None,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        data: Any = None
    ) -> Response:
        """
        Return an error API response.
        
        Args:
            message: Error message
            errors: Detailed error information
            status_code: HTTP status code
            data: Additional data (if any)
        
        Returns:
            DRF Response object
        """
        from django.utils import timezone
        
        response_data = {
            "success": False,
            "message": message,
            "errors": errors or {},
            "data": data,
            "meta": {
                "timestamp": timezone.now().isoformat(),
            }
        }
        
        logger.error(f"API Error: {message} - Errors: {errors}")
        
        return Response(response_data, status=status_code)
    
    @staticmethod
    def paginated(
        queryset,
        serializer_class,
        request,
        page: int = 1,
        page_size: int = 20,
        message: str = "Data retrieved successfully"
    ) -> Response:
        """
        Return a paginated API response.
        
        Args:
            queryset: Django QuerySet
            serializer_class: DRF Serializer class
            request: Request object
            page: Page number
            page_size: Items per page
            message: Success message
        
        Returns:
            Paginated Response
        """
        from django.utils import timezone
        
        paginator = Paginator(queryset, page_size)
        page_obj = paginator.get_page(page)
        
        serializer = serializer_class(
            page_obj.object_list,
            many=True,
            context={'request': request}
        )
        
        response_data = {
            "success": True,
            "message": message,
            "data": serializer.data,
            "meta": {
                "timestamp": timezone.now().isoformat(),
                "pagination": {
                    "page": page,
                    "page_size": page_size,
                    "total_pages": paginator.num_pages,
                    "total_items": paginator.count,
                    "has_next": page_obj.has_next(),
                    "has_previous": page_obj.has_previous(),
                    "next_page": page_obj.next_page_number() if page_obj.has_next() else None,
                    "previous_page": page_obj.previous_page_number() if page_obj.has_previous() else None,
                }
            }
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
    
    @staticmethod
    def created(
        data: Any,
        message: str = "Resource created successfully",
        meta: Optional[Dict] = None
    ) -> Response:
        """Return a 201 Created response."""
        return APIResponse.success(
            data=data,
            message=message,
            status_code=status.HTTP_201_CREATED,
            meta=meta
        )
    
    @staticmethod
    def no_content(
        message: str = "Operation successful"
    ) -> Response:
        """Return a 204 No Content response."""
        return APIResponse.success(
            message=message,
            status_code=status.HTTP_204_NO_CONTENT
        )
    
    @staticmethod
    def not_found(
        message: str = "Resource not found",
        errors: Optional[Dict] = None
    ) -> Response:
        """Return a 404 Not Found response."""
        return APIResponse.error(
            message=message,
            errors=errors,
            status_code=status.HTTP_404_NOT_FOUND
        )
    
    @staticmethod
    def unauthorized(
        message: str = "Authentication required",
        errors: Optional[Dict] = None
    ) -> Response:
        """Return a 401 Unauthorized response."""
        return APIResponse.error(
            message=message,
            errors=errors,
            status_code=status.HTTP_401_UNAUTHORIZED
        )
    
    @staticmethod
    def forbidden(
        message: str = "Permission denied",
        errors: Optional[Dict] = None
    ) -> Response:
        """Return a 403 Forbidden response."""
        return APIResponse.error(
            message=message,
            errors=errors,
            status_code=status.HTTP_403_FORBIDDEN
        )
    
    @staticmethod
    def bad_request(
        message: str = "Invalid request",
        errors: Optional[Dict] = None
    ) -> Response:
        """Return a 400 Bad Request response."""
        return APIResponse.error(
            message=message,
            errors=errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    @staticmethod
    def server_error(
        message: str = "Internal server error",
        errors: Optional[Dict] = None
    ) -> Response:
        """Return a 500 Internal Server Error response."""
        logger.critical(f"Server Error: {message} - {errors}")
        return APIResponse.error(
            message=message,
            errors=errors,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class BulkOperationResponse:
    """Handle responses for bulk operations."""
    
    @staticmethod
    def success_with_failures(
        successful: List[Dict],
        failed: List[Dict],
        message: str = "Bulk operation completed"
    ) -> Response:
        """
        Return response for bulk operation with partial success.
        
        Args:
            successful: List of successfully processed items
            failed: List of failed items with error details
            message: Operation message
        
        Returns:
            Response with detailed success/failure information
        """
        from django.utils import timezone
        
        response_data = {
            "success": len(failed) == 0,
            "message": message,
            "data": {
                "successful": successful,
                "failed": failed,
            },
            "meta": {
                "timestamp": timezone.now().isoformat(),
                "summary": {
                    "total": len(successful) + len(failed),
                    "successful_count": len(successful),
                    "failed_count": len(failed),
                    "success_rate": round(len(successful) / (len(successful) + len(failed)) * 100, 2) if (len(successful) + len(failed)) > 0 else 0
                }
            }
        }
        
        status_code = status.HTTP_207_MULTI_STATUS if failed else status.HTTP_200_OK
        
        return Response(response_data, status=status_code)


class FileUploadResponse:
    """Handle responses for file upload operations."""
    
    @staticmethod
    def upload_success(
        file_url: str,
        file_name: str,
        file_size: int,
        file_type: str,
        message: str = "File uploaded successfully"
    ) -> Response:
        """
        Return response for successful file upload.
        
        Args:
            file_url: URL to access the uploaded file
            file_name: Original filename
            file_size: File size in bytes
            file_type: MIME type
            message: Success message
        
        Returns:
            Standardized file upload response
        """
        from django.utils import timezone
        
        response_data = {
            "success": True,
            "message": message,
            "data": {
                "url": file_url,
                "filename": file_name,
                "size": file_size,
                "size_human": format_file_size(file_size),
                "type": file_type,
            },
            "meta": {
                "timestamp": timezone.now().isoformat(),
            }
        }
        
        return Response(response_data, status=status.HTTP_201_CREATED)
    
    @staticmethod
    def upload_error(
        message: str = "File upload failed",
        errors: Optional[Dict] = None
    ) -> Response:
        """Return response for failed file upload."""
        return APIResponse.error(
            message=message,
            errors=errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.
    
    Args:
        size_bytes: File size in bytes
    
    Returns:
        Formatted string (e.g., "1.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"


def validate_file_upload(file, allowed_types: List[str], max_size: int) -> Dict[str, Any]:
    """
    Validate uploaded file against type and size restrictions.
    
    Args:
        file: Uploaded file object
        allowed_types: List of allowed MIME types
        max_size: Maximum file size in bytes
    
    Returns:
        Dict with 'valid' boolean and 'errors' list
    """
    errors = []
    
    # Check file type
    if file.content_type not in allowed_types:
        errors.append(f"Invalid file type. Allowed types: {', '.join(allowed_types)}")
    
    # Check file size
    if file.size > max_size:
        errors.append(f"File too large. Maximum size: {format_file_size(max_size)}")
    
    # Check file name
    if not file.name:
        errors.append("File name is required")
    
    # Check for potentially dangerous file extensions
    dangerous_extensions = ['.exe', '.sh', '.bat', '.cmd', '.com', '.pif']
    if any(file.name.lower().endswith(ext) for ext in dangerous_extensions):
        errors.append("File type not allowed for security reasons")
    
    return {
        'valid': len(errors) == 0,
        'errors': errors
    }


# HTTP Status Code Constants with Descriptions
STATUS_CODES = {
    # Success
    200: "OK - Request successful",
    201: "Created - Resource created successfully",
    202: "Accepted - Request accepted for processing",
    204: "No Content - Successful with no response body",
    
    # Client Errors
    400: "Bad Request - Invalid request format or parameters",
    401: "Unauthorized - Authentication required",
    403: "Forbidden - Permission denied",
    404: "Not Found - Resource not found",
    405: "Method Not Allowed - HTTP method not supported",
    406: "Not Acceptable - Cannot produce requested content type",
    409: "Conflict - Resource conflict (e.g., duplicate)",
    410: "Gone - Resource permanently deleted",
    413: "Payload Too Large - Request body too large",
    415: "Unsupported Media Type - Unsupported content type",
    422: "Unprocessable Entity - Validation failed",
    429: "Too Many Requests - Rate limit exceeded",
    
    # Server Errors
    500: "Internal Server Error - Server error",
    501: "Not Implemented - Feature not implemented",
    502: "Bad Gateway - Invalid response from upstream server",
    503: "Service Unavailable - Service temporarily unavailable",
    504: "Gateway Timeout - Upstream server timeout",
}

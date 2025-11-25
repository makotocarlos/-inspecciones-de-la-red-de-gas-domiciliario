"""
Advanced Request Logging Middleware
Tracks all API requests with performance metrics and user activity
"""
import time
import json
import logging
from django.utils import timezone
from django.db import connection
from django.conf import settings

logger = logging.getLogger(__name__)


class RequestLoggerMiddleware:
    """
    Professional request logging with performance tracking
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Start timing
        start_time = time.time()
        start_queries = len(connection.queries)
        
        # Get request metadata
        request_id = self._generate_request_id()
        request.request_id = request_id
        
        # Log request
        self._log_request(request, request_id)
        
        # Process request
        response = self.get_response(request)
        
        # Calculate metrics
        duration = time.time() - start_time
        query_count = len(connection.queries) - start_queries
        
        # Log response
        self._log_response(request, response, duration, query_count, request_id)
        
        # Add custom headers
        response['X-Request-ID'] = request_id
        response['X-Response-Time'] = f'{duration:.3f}s'
        response['X-Query-Count'] = str(query_count)
        
        return response
    
    def _generate_request_id(self):
        """Generate unique request ID"""
        import uuid
        return str(uuid.uuid4())[:8]
    
    def _log_request(self, request, request_id):
        """Log incoming request"""
        user = getattr(request, 'user', None)
        user_info = f"{user.email} ({user.role})" if user and user.is_authenticated else 'Anonymous'
        
        logger.info(
            f"[{request_id}] {request.method} {request.path} | User: {user_info} | IP: {self._get_client_ip(request)}"
        )
    
    def _log_response(self, request, response, duration, query_count, request_id):
        """Log response with metrics"""
        # Determine log level based on status code
        status = response.status_code
        if status >= 500:
            log_level = logging.ERROR
        elif status >= 400:
            log_level = logging.WARNING
        else:
            log_level = logging.INFO
        
        # Performance warning
        performance_warning = ""
        if duration > 1.0:
            performance_warning = " [SLOW]"
        if query_count > 20:
            performance_warning += " [HIGH DB QUERIES]"
        
        logger.log(
            log_level,
            f"[{request_id}] {request.method} {request.path} | "
            f"Status: {status} | Duration: {duration:.3f}s | "
            f"Queries: {query_count}{performance_warning}"
        )
        
        # Log slow queries in debug mode
        if settings.DEBUG and duration > 1.0:
            for query in connection.queries[-query_count:]:
                if float(query['time']) > 0.1:
                    logger.warning(f"Slow query ({query['time']}s): {query['sql'][:200]}")
    
    def _get_client_ip(self, request):
        """Get real client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class SecurityHeadersMiddleware:
    """
    Add advanced security headers to all responses
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        
        # Security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
        
        # Content Security Policy
        if not settings.DEBUG:
            response['Content-Security-Policy'] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "font-src 'self' data:; "
                "connect-src 'self';"
            )
        
        return response


class PerformanceMonitoringMiddleware:
    """
    Monitor and alert on performance issues
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.slow_request_threshold = 2.0  # seconds
        self.alert_on_slow_requests = True
    
    def __call__(self, request):
        start_time = time.time()
        
        response = self.get_response(request)
        
        duration = time.time() - start_time
        
        # Track performance metrics
        if duration > self.slow_request_threshold:
            self._alert_slow_request(request, duration)
            
            # Could integrate with monitoring services here
            # Example: Sentry, DataDog, New Relic
            if hasattr(settings, 'SENTRY_DSN'):
                import sentry_sdk
                sentry_sdk.capture_message(
                    f"Slow request: {request.method} {request.path}",
                    level='warning',
                    extras={'duration': duration}
                )
        
        return response
    
    def _alert_slow_request(self, request, duration):
        """Alert about slow requests"""
        logger.warning(
            f"PERFORMANCE: Slow request detected | "
            f"{request.method} {request.path} | "
            f"Duration: {duration:.3f}s"
        )


class AuditTrailMiddleware:
    """
    Track important user actions for audit purposes
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.tracked_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
        self.sensitive_paths = ['/api/users/', '/api/inspections/', '/api/reports/']
    
    def __call__(self, request):
        response = self.get_response(request)
        
        # Track sensitive operations
        if self._should_track(request, response):
            self._create_audit_log(request, response)
        
        return response
    
    def _should_track(self, request, response):
        """Determine if request should be tracked"""
        if request.method not in self.tracked_methods:
            return False
        
        if response.status_code >= 400:
            return False
        
        # Check if path matches sensitive patterns
        for path in self.sensitive_paths:
            if path in request.path:
                return True
        
        return False
    
    def _create_audit_log(self, request, response):
        """Create audit log entry"""
        user = getattr(request, 'user', None)
        
        audit_data = {
            'timestamp': timezone.now().isoformat(),
            'user': user.email if user and user.is_authenticated else 'Anonymous',
            'user_id': str(user.id) if user and user.is_authenticated else None,
            'action': request.method,
            'path': request.path,
            'ip_address': self._get_client_ip(request),
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            'status_code': response.status_code,
        }
        
        # Log to audit trail
        logger.info(f"AUDIT: {json.dumps(audit_data)}")
        
        # Could also save to database for compliance
        # AuditLog.objects.create(**audit_data)
    
    def _get_client_ip(self, request):
        """Get real client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

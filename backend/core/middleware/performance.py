"""
Performance Monitoring Middleware
Tracks request/response times and logs slow queries for optimization.
"""

import time
import logging
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger('performance')


class PerformanceMonitoringMiddleware(MiddlewareMixin):
    """
    Middleware to monitor and log performance metrics for each request.
    Tracks response time, query count, and identifies slow endpoints.
    """
    
    def process_request(self, request):
        """Mark the start time of the request."""
        request._start_time = time.time()
        return None
    
    def process_response(self, request, response):
        """Calculate and log performance metrics."""
        if hasattr(request, '_start_time'):
            duration = time.time() - request._start_time
            duration_ms = duration * 1000
            
            # Get query count from connection
            from django.db import connection
            query_count = len(connection.queries)
            
            # Log slow requests (over 1 second)
            if duration_ms > 1000:
                logger.warning(
                    f"Slow request detected: {request.method} {request.path} "
                    f"took {duration_ms:.2f}ms with {query_count} queries"
                )
            
            # Add performance headers (only in debug mode)
            if settings.DEBUG:
                response['X-Response-Time'] = f"{duration_ms:.2f}ms"
                response['X-Query-Count'] = str(query_count)
            
            # Log all requests in production
            if not settings.DEBUG:
                logger.info(
                    f"{request.method} {request.path} - "
                    f"Status: {response.status_code} - "
                    f"Time: {duration_ms:.2f}ms - "
                    f"Queries: {query_count}"
                )
        
        return response


class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Enhanced request logging middleware for security and audit trail.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = logging.getLogger('django.request')
    
    def __call__(self, request):
        # Log request details
        self.log_request(request)
        
        # Process request
        response = self.get_response(request)
        
        # Log response
        self.log_response(request, response)
        
        return response
    
    def log_request(self, request):
        """Log incoming request details."""
        user = getattr(request, 'user', None)
        user_id = user.id if user and user.is_authenticated else 'Anonymous'
        
        self.logger.info(
            f"Request: {request.method} {request.path} | "
            f"User: {user_id} | "
            f"IP: {self.get_client_ip(request)} | "
            f"User-Agent: {request.META.get('HTTP_USER_AGENT', 'Unknown')[:100]}"
        )
    
    def log_response(self, request, response):
        """Log response status."""
        if response.status_code >= 400:
            self.logger.warning(
                f"Response: {response.status_code} for {request.method} {request.path}"
            )
    
    @staticmethod
    def get_client_ip(request):
        """Extract client IP address from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', 'Unknown')
        return ip


class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Add additional security headers to all responses.
    Enhances security beyond Django's default settings.
    """
    
    def process_response(self, request, response):
        """Add security headers to response."""
        # Content Security Policy
        response['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self'; "
            "frame-ancestors 'none';"
        )
        
        # Permissions Policy (formerly Feature-Policy)
        response['Permissions-Policy'] = (
            "geolocation=(), "
            "microphone=(), "
            "camera=(), "
            "payment=(), "
            "usb=(), "
            "magnetometer=(), "
            "accelerometer=()"
        )
        
        # X-Content-Type-Options
        response['X-Content-Type-Options'] = 'nosniff'
        
        # X-Frame-Options
        response['X-Frame-Options'] = 'DENY'
        
        # X-XSS-Protection
        response['X-XSS-Protection'] = '1; mode=block'
        
        # Referrer Policy
        response['Referrer-Policy'] = 'same-origin'
        
        return response


class RateLimitMiddleware(MiddlewareMixin):
    """
    Simple rate limiting middleware based on IP address.
    For production, consider using django-ratelimit or similar.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.cache_key_prefix = 'rate_limit'
        self.requests_limit = 100  # requests per minute
        self.timeout = 60  # 1 minute
    
    def __call__(self, request):
        from django.core.cache import cache
        from django.http import JsonResponse
        
        # Get client IP
        ip = self.get_client_ip(request)
        
        # Skip rate limiting for authenticated staff users
        if hasattr(request, 'user') and request.user.is_authenticated and request.user.is_staff:
            return self.get_response(request)
        
        # Check rate limit
        cache_key = f"{self.cache_key_prefix}:{ip}"
        request_count = cache.get(cache_key, 0)
        
        if request_count >= self.requests_limit:
            logger = logging.getLogger('django.security')
            logger.warning(f"Rate limit exceeded for IP: {ip}")
            return JsonResponse(
                {
                    'error': 'Rate limit exceeded',
                    'message': f'Too many requests. Limit: {self.requests_limit} per minute.'
                },
                status=429
            )
        
        # Increment counter
        cache.set(cache_key, request_count + 1, self.timeout)
        
        return self.get_response(request)
    
    @staticmethod
    def get_client_ip(request):
        """Extract client IP address from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', 'Unknown')
        return ip

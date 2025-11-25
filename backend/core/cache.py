"""
Professional Caching Strategy
Redis-based caching with automatic invalidation
"""
from django.core.cache import cache
from django.conf import settings
from functools import wraps
import hashlib
import json
import logging

logger = logging.getLogger(__name__)


class CacheManager:
    """
    Centralized cache management with automatic invalidation
    """
    
    # Cache timeouts (in seconds)
    TIMEOUT_SHORT = 300  # 5 minutes
    TIMEOUT_MEDIUM = 1800  # 30 minutes
    TIMEOUT_LONG = 3600  # 1 hour
    TIMEOUT_EXTRA_LONG = 86400  # 24 hours
    
    # Cache key prefixes
    PREFIX_USER = 'user'
    PREFIX_INSPECTION = 'inspection'
    PREFIX_REPORT = 'report'
    PREFIX_DASHBOARD = 'dashboard'
    PREFIX_STATS = 'stats'
    
    @classmethod
    def _generate_key(cls, prefix, *args, **kwargs):
        """Generate unique cache key"""
        # Create unique string from arguments
        key_data = f"{prefix}:{args}:{sorted(kwargs.items())}"
        key_hash = hashlib.md5(key_data.encode()).hexdigest()
        return f"{prefix}:{key_hash}"
    
    @classmethod
    def get(cls, key, default=None):
        """Get value from cache"""
        try:
            value = cache.get(key, default)
            if value is not None:
                logger.debug(f"Cache HIT: {key}")
            else:
                logger.debug(f"Cache MISS: {key}")
            return value
        except Exception as e:
            logger.error(f"Cache GET error: {e}")
            return default
    
    @classmethod
    def set(cls, key, value, timeout=TIMEOUT_MEDIUM):
        """Set value in cache"""
        try:
            cache.set(key, value, timeout)
            logger.debug(f"Cache SET: {key} (timeout: {timeout}s)")
            return True
        except Exception as e:
            logger.error(f"Cache SET error: {e}")
            return False
    
    @classmethod
    def delete(cls, key):
        """Delete value from cache"""
        try:
            cache.delete(key)
            logger.debug(f"Cache DELETE: {key}")
            return True
        except Exception as e:
            logger.error(f"Cache DELETE error: {e}")
            return False
    
    @classmethod
    def delete_pattern(cls, pattern):
        """Delete all keys matching pattern"""
        try:
            cache.delete_pattern(pattern)
            logger.info(f"Cache DELETE PATTERN: {pattern}")
            return True
        except Exception as e:
            logger.error(f"Cache DELETE PATTERN error: {e}")
            return False
    
    @classmethod
    def clear(cls):
        """Clear entire cache"""
        try:
            cache.clear()
            logger.warning("Cache CLEARED")
            return True
        except Exception as e:
            logger.error(f"Cache CLEAR error: {e}")
            return False
    
    # Specific cache methods
    
    @classmethod
    def cache_user_data(cls, user_id, data, timeout=TIMEOUT_MEDIUM):
        """Cache user data"""
        key = f"{cls.PREFIX_USER}:{user_id}"
        return cls.set(key, data, timeout)
    
    @classmethod
    def get_user_data(cls, user_id):
        """Get cached user data"""
        key = f"{cls.PREFIX_USER}:{user_id}"
        return cls.get(key)
    
    @classmethod
    def invalidate_user_cache(cls, user_id):
        """Invalidate all user-related cache"""
        pattern = f"{cls.PREFIX_USER}:{user_id}*"
        return cls.delete_pattern(pattern)
    
    @classmethod
    def cache_inspection(cls, inspection_id, data, timeout=TIMEOUT_MEDIUM):
        """Cache inspection data"""
        key = f"{cls.PREFIX_INSPECTION}:{inspection_id}"
        return cls.set(key, data, timeout)
    
    @classmethod
    def get_inspection(cls, inspection_id):
        """Get cached inspection"""
        key = f"{cls.PREFIX_INSPECTION}:{inspection_id}"
        return cls.get(key)
    
    @classmethod
    def invalidate_inspection_cache(cls, inspection_id):
        """Invalidate inspection cache"""
        pattern = f"{cls.PREFIX_INSPECTION}:{inspection_id}*"
        return cls.delete_pattern(pattern)
    
    @classmethod
    def cache_dashboard_stats(cls, user_id, role, data, timeout=TIMEOUT_SHORT):
        """Cache dashboard statistics"""
        key = f"{cls.PREFIX_DASHBOARD}:{role}:{user_id}"
        return cls.set(key, data, timeout)
    
    @classmethod
    def get_dashboard_stats(cls, user_id, role):
        """Get cached dashboard stats"""
        key = f"{cls.PREFIX_DASHBOARD}:{role}:{user_id}"
        return cls.get(key)
    
    @classmethod
    def invalidate_dashboard_cache(cls, user_id=None):
        """Invalidate dashboard cache"""
        if user_id:
            pattern = f"{cls.PREFIX_DASHBOARD}:*:{user_id}*"
        else:
            pattern = f"{cls.PREFIX_DASHBOARD}:*"
        return cls.delete_pattern(pattern)
    
    @classmethod
    def cache_report(cls, report_id, pdf_bytes, timeout=TIMEOUT_EXTRA_LONG):
        """Cache generated PDF report"""
        key = f"{cls.PREFIX_REPORT}:{report_id}"
        return cls.set(key, pdf_bytes, timeout)
    
    @classmethod
    def get_report(cls, report_id):
        """Get cached PDF report"""
        key = f"{cls.PREFIX_REPORT}:{report_id}"
        return cls.get(key)
    
    @classmethod
    def invalidate_report_cache(cls, report_id):
        """Invalidate report cache"""
        key = f"{cls.PREFIX_REPORT}:{report_id}"
        return cls.delete(key)


def cache_view(timeout=CacheManager.TIMEOUT_MEDIUM, key_prefix=None):
    """
    Decorator to cache view results
    
    Usage:
        @cache_view(timeout=300, key_prefix='my_view')
        def my_view(request):
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            # Generate cache key
            user_id = str(request.user.id) if request.user.is_authenticated else 'anon'
            cache_key = f"{key_prefix or func.__name__}:{user_id}:{request.method}:{request.path}"
            
            # Try to get from cache
            cached_response = CacheManager.get(cache_key)
            if cached_response is not None:
                return cached_response
            
            # Execute function
            response = func(request, *args, **kwargs)
            
            # Cache response
            if response.status_code == 200:
                CacheManager.set(cache_key, response, timeout)
            
            return response
        return wrapper
    return decorator


def cache_method(timeout=CacheManager.TIMEOUT_MEDIUM, key_prefix=None):
    """
    Decorator to cache method results
    
    Usage:
        @cache_method(timeout=300)
        def expensive_calculation(self, param1, param2):
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            # Generate cache key from function name and arguments
            key = CacheManager._generate_key(
                key_prefix or func.__name__,
                *args,
                **kwargs
            )
            
            # Try to get from cache
            cached_result = CacheManager.get(key)
            if cached_result is not None:
                return cached_result
            
            # Execute function
            result = func(self, *args, **kwargs)
            
            # Cache result
            CacheManager.set(key, result, timeout)
            
            return result
        return wrapper
    return decorator

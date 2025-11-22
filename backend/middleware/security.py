"""
Security middleware for rate limiting and request validation
"""
from django.core.cache import cache
from django.http import JsonResponse
from django.conf import settings
import time
from functools import wraps
from utils.logger import setup_logging

logger = setup_logging(__name__)


class RateLimitMiddleware:
    """
    Global rate limiting middleware
    Limits requests per IP address
    """
    def __init__(self, get_response):
        self.get_response = get_response
        # Rate limits: (requests, time_window_seconds)
        self.rate_limits = {
            'default': (100, 60),  # 100 requests per minute
            'auth': (5, 300),      # 5 auth attempts per 5 minutes
            'upload': (10, 60),    # 10 uploads per minute
            'generate': (20, 60),  # 20 generations per minute
        }

    def __call__(self, request):
        # Skip rate limiting for admin and static files
        if request.path.startswith('/admin/') or request.path.startswith('/static/'):
            return self.get_response(request)

        # Get client IP
        ip = self.get_client_ip(request)
        
        # Determine rate limit key based on endpoint
        limit_key = self.get_limit_key(request.path)
        
        # Check rate limit
        if not self.check_rate_limit(ip, limit_key):
            logger.warning(f'Rate limit exceeded for {ip} on {request.path}')
            return JsonResponse({
                'error': 'Rate limit exceeded. Please try again later.'
            }, status=429)

        response = self.get_response(request)
        return response

    def get_client_ip(self, request):
        """Extract client IP from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def get_limit_key(self, path):
        """Determine which rate limit to apply based on path"""
        if '/auth/' in path or '/login/' in path or '/register/' in path:
            return 'auth'
        elif '/extract/' in path or '/upload/' in path:
            return 'upload'
        elif '/generate' in path:
            return 'generate'
        else:
            return 'default'

    def check_rate_limit(self, ip, limit_key):
        """Check if request is within rate limit"""
        max_requests, time_window = self.rate_limits.get(limit_key, self.rate_limits['default'])
        
        cache_key = f'rate_limit:{limit_key}:{ip}'
        current_time = int(time.time())
        
        # Get request timestamps from cache
        request_times = cache.get(cache_key, [])
        
        # Filter out old requests outside time window
        request_times = [t for t in request_times if current_time - t < time_window]
        
        # Check if limit exceeded
        if len(request_times) >= max_requests:
            return False
        
        # Add current request
        request_times.append(current_time)
        cache.set(cache_key, request_times, time_window)
        
        return True


class SecurityHeadersMiddleware:
    """
    Add security headers to all responses
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Add security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Content Security Policy (adjust as needed)
        if not settings.DEBUG:
            response['Content-Security-Policy'] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "font-src 'self' data:; "
                "connect-src 'self' https:;"
            )
        
        return response


def rate_limit(max_requests=10, time_window=60):
    """
    Decorator for view-specific rate limiting
    
    Usage:
        @rate_limit(max_requests=5, time_window=60)
        def my_view(request):
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            ip = request.META.get('REMOTE_ADDR')
            cache_key = f'rate_limit:{func.__name__}:{ip}'
            current_time = int(time.time())
            
            request_times = cache.get(cache_key, [])
            request_times = [t for t in request_times if current_time - t < time_window]
            
            if len(request_times) >= max_requests:
                logger.warning(f'Rate limit exceeded for {ip} on {func.__name__}')
                return JsonResponse({
                    'error': 'Too many requests. Please try again later.'
                }, status=429)
            
            request_times.append(current_time)
            cache.set(cache_key, request_times, time_window)
            
            return func(request, *args, **kwargs)
        return wrapper
    return decorator

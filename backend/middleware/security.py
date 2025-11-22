"""
Security middleware for rate limiting and request validation
"""
from django.core.cache import cache
from django.http import JsonResponse
from django.conf import settings
import time
import asyncio
from functools import wraps
from asgiref.sync import iscoroutinefunction, sync_to_async
from utils.logger import setup_logging

logger = setup_logging(__name__)


class RateLimitMiddleware:
    """
    Global rate limiting middleware
    Supports both Sync (WSGI) and Async (ASGI) modes explicitly
    """
    def __init__(self, get_response):
        self.get_response = get_response
        self.is_async = iscoroutinefunction(get_response)
        
        # Rate limits: (requests, time_window_seconds)
        self.rate_limits = {
            'default': (100, 60),  # 100 requests per minute
            'auth': (5, 300),      # 5 auth attempts per 5 minutes
            'upload': (10, 60),    # 10 uploads per minute
            'generate': (20, 60),  # 20 generations per minute
        }

    def __call__(self, request):
        if self.is_async:
            return self.__acall__(request)
        
        # Sync Logic
        if self.should_skip(request):
            return self.get_response(request)

        ip = self.get_client_ip(request)
        limit_key = self.get_limit_key(request.path)

        if not self.check_rate_limit_sync(ip, limit_key):
            logger.warning(f'Rate limit exceeded for {ip} on {request.path}')
            return JsonResponse({
                'error': 'Rate limit exceeded. Please try again later.'
            }, status=429)

        return self.get_response(request)

    async def __acall__(self, request):
        # Async Logic
        if self.should_skip(request):
            return await self.get_response(request)

        ip = self.get_client_ip(request)
        limit_key = self.get_limit_key(request.path)

        # Use async check to avoid blocking the event loop
        is_allowed = await self.check_rate_limit_async(ip, limit_key)
        
        if not is_allowed:
            logger.warning(f'Rate limit exceeded for {ip} on {request.path}')
            return JsonResponse({
                'error': 'Rate limit exceeded. Please try again later.'
            }, status=429)

        return await self.get_response(request)

    def should_skip(self, request):
        return request.path.startswith('/admin/') or request.path.startswith('/static/')

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def get_limit_key(self, path):
        if '/auth/' in path or '/login/' in path or '/register/' in path:
            return 'auth'
        elif '/extract/' in path or '/upload/' in path:
            return 'upload'
        elif '/generate' in path:
            return 'generate'
        else:
            return 'default'

    # --- Sync Implementation ---
    def check_rate_limit_sync(self, ip, limit_key):
        max_requests, time_window = self.rate_limits.get(limit_key, self.rate_limits['default'])
        cache_key = f'rate_limit:{limit_key}:{ip}'
        current_time = int(time.time())
        
        request_times = cache.get(cache_key, [])
        request_times = [t for t in request_times if current_time - t < time_window]
        
        if len(request_times) >= max_requests:
            return False
        
        request_times.append(current_time)
        cache.set(cache_key, request_times, time_window)
        return True

    # --- Async Implementation ---
    async def check_rate_limit_async(self, ip, limit_key):
        max_requests, time_window = self.rate_limits.get(limit_key, self.rate_limits['default'])
        cache_key = f'rate_limit:{limit_key}:{ip}'
        current_time = int(time.time())
        
        # Try to use native async cache methods if available (Django 3.1+)
        # Otherwise fallback to sync_to_async wrapper
        try:
            request_times = await cache.aget(cache_key, [])
        except AttributeError:
            request_times = await sync_to_async(cache.get)(cache_key, [])

        request_times = [t for t in request_times if current_time - t < time_window]
        
        if len(request_times) >= max_requests:
            return False
        
        request_times.append(current_time)
        
        try:
            await cache.aset(cache_key, request_times, time_window)
        except AttributeError:
            await sync_to_async(cache.set)(cache_key, request_times, time_window)
            
        return True


class SecurityHeadersMiddleware:
    """
    Add security headers to all responses
    """
    def __init__(self, get_response):
        self.get_response = get_response
        self.is_async = iscoroutinefunction(get_response)

    def __call__(self, request):
        if self.is_async:
            return self.__acall__(request)
        
        response = self.get_response(request)
        return self.process_response(response)

    async def __acall__(self, request):
        response = await self.get_response(request)
        return self.process_response(response)

    def process_response(self, response):
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
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
    Decorator for view-specific rate limiting.
    Automatically handles both Sync and Async views.
    """
    def decorator(func):
        if iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(request, *args, **kwargs):
                ip = request.META.get('REMOTE_ADDR')
                cache_key = f'rate_limit:{func.__name__}:{ip}'
                current_time = int(time.time())
                
                # Async cache retrieval
                try:
                    request_times = await cache.aget(cache_key, [])
                except AttributeError:
                    request_times = await sync_to_async(cache.get)(cache_key, [])

                request_times = [t for t in request_times if current_time - t < time_window]
                
                if len(request_times) >= max_requests:
                    logger.warning(f'Rate limit exceeded for {ip} on {func.__name__}')
                    return JsonResponse({
                        'error': 'Too many requests. Please try again later.'
                    }, status=429)
                
                request_times.append(current_time)
                
                # Async cache setting
                try:
                    await cache.aset(cache_key, request_times, time_window)
                except AttributeError:
                    await sync_to_async(cache.set)(cache_key, request_times, time_window)
                
                return await func(request, *args, **kwargs)
            return async_wrapper
        else:
            @wraps(func)
            def sync_wrapper(request, *args, **kwargs):
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
            return sync_wrapper
    return decorator
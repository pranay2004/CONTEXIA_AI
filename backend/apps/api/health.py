"""
System health monitoring and diagnostics
"""
from django.http import JsonResponse
from django.db import connection
from django.core.cache import cache
from django.conf import settings
import psutil
import time
from utils.logger import setup_logging

logger = setup_logging(__name__)


def health_check(request):
    """
    Comprehensive health check endpoint
    Returns system status, database connectivity, cache, and resource usage
    """
    start_time = time.time()
    health_status = {
        'status': 'healthy',
        'timestamp': int(time.time()),
        'checks': {},
        'metrics': {}
    }
    
    # 1. Database Check
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
        health_status['checks']['database'] = {
            'status': 'ok',
            'connection': 'active'
        }
    except Exception as e:
        logger.error(f'Database health check failed: {e}')
        health_status['status'] = 'unhealthy'
        health_status['checks']['database'] = {
            'status': 'error',
            'message': str(e)
        }
    
    # 2. Cache Check
    try:
        cache_key = 'health_check_test'
        cache.set(cache_key, 'ok', 10)
        cache_value = cache.get(cache_key)
        health_status['checks']['cache'] = {
            'status': 'ok' if cache_value == 'ok' else 'error',
            'type': settings.CACHES['default']['BACKEND'].split('.')[-1]
        }
    except Exception as e:
        logger.error(f'Cache health check failed: {e}')
        health_status['checks']['cache'] = {
            'status': 'error',
            'message': str(e)
        }
    
    # 3. System Metrics
    try:
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        health_status['metrics'] = {
            'cpu': {
                'usage_percent': cpu_percent,
                'cores': psutil.cpu_count()
            },
            'memory': {
                'total_mb': round(memory.total / (1024 * 1024), 2),
                'available_mb': round(memory.available / (1024 * 1024), 2),
                'usage_percent': memory.percent
            },
            'disk': {
                'total_gb': round(disk.total / (1024 * 1024 * 1024), 2),
                'free_gb': round(disk.free / (1024 * 1024 * 1024), 2),
                'usage_percent': disk.percent
            }
        }
        
        # Alert if resources are critically low
        if memory.percent > 90:
            health_status['status'] = 'degraded'
            health_status['warnings'] = health_status.get('warnings', [])
            health_status['warnings'].append('High memory usage')
        
        if disk.percent > 90:
            health_status['status'] = 'degraded'
            health_status['warnings'] = health_status.get('warnings', [])
            health_status['warnings'].append('Low disk space')
            
    except Exception as e:
        logger.error(f'System metrics collection failed: {e}')
        health_status['metrics']['error'] = str(e)
    
    # 4. Response Time
    response_time_ms = (time.time() - start_time) * 1000
    health_status['response_time_ms'] = round(response_time_ms, 2)
    
    # Set HTTP status code
    status_code = 200 if health_status['status'] in ['healthy', 'degraded'] else 503
    
    return JsonResponse(health_status, status=status_code)


def readiness_check(request):
    """
    Kubernetes readiness probe - check if service can handle requests
    """
    try:
        # Quick database check
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
        
        return JsonResponse({'status': 'ready'}, status=200)
    except Exception as e:
        logger.error(f'Readiness check failed: {e}')
        return JsonResponse({'status': 'not ready', 'error': str(e)}, status=503)


def liveness_check(request):
    """
    Kubernetes liveness probe - check if service is alive
    """
    return JsonResponse({'status': 'alive'}, status=200)

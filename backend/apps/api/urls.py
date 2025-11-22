from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    extract_content, 
    generate_content, 
    generate_content_stream,
    check_task_status,
    get_generated_content,
    list_trends,
    generate_viral_hooks,
    user_analytics,
    upload_voice_sample,
    recent_activity, # ✅ Used in dashboard
    TrendArticleViewSet
)

# Import health check views
from .health import health_check, readiness_check, liveness_check

# Import photo processing views
from apps.media.views import (
    process_photo,
    create_collage,
    batch_process,
    get_templates,
    get_filters
)

router = DefaultRouter()
router.register(r'trends', TrendArticleViewSet)

urlpatterns = [
    path('', include(router.urls)),
    
    # Core Pipelines
    path('extract/', extract_content, name='extract_content'),
    path('generate/', generate_content, name='generate_content'),
    path('generate-stream/', generate_content_stream, name='generate_content_stream'),
    
    # Helper/Status
    path('jobs/<str:task_id>/', check_task_status, name='check_task_status'),
    
    # Analytics & User
    path('generated-content/<int:content_id>/', get_generated_content, name='get_generated_content'),
    path('hooks/generate/', generate_viral_hooks, name='generate_viral_hooks'),
    path('analytics/', user_analytics, name='user_analytics'),
    path('stats/recent-activity/', recent_activity, name='recent_activity'), # ✅ Dashboard feed
    path('analyze-my-voice-file/', upload_voice_sample, name='upload_voice_sample'),
    
    # Photo Processing
    path('photos/process/', process_photo, name='process_photo'),
    path('photos/collage/', create_collage, name='create_collage'),
    path('photos/batch/', batch_process, name='batch_process'),
    path('photos/templates/', get_templates, name='get_templates'),
    path('photos/filters/', get_filters, name='get_filters'),
    
    # System Health & Monitoring
    path('health/', health_check, name='health_check'),
    path('health/ready/', readiness_check, name='readiness_check'),
    path('health/live/', liveness_check, name='liveness_check'),
]
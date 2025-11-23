"""
URL configuration for TrendMaster AI
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # ✅ SPECIFIC ROUTES FIRST (Fixes the 404 error)
    path('api/auth/register/', include('apps.users.urls')),
    path('api/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/social/', include('apps.social.urls')),
    path('api/users/', include('apps.users.urls')),  # Add users profile endpoint

    # ✅ GENERIC CATCH-ALL LAST
    path('api/', include('apps.api.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
"""
URL Configuration for Social Media Integration
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SocialAccountViewSet,
    ScheduledPostViewSet,
    PostingScheduleViewSet,
    PublishedPostAnalyticsViewSet,
    PostViewSet,
)
from .views_image_generation import ImageGenerationViewSet
from .views_stock_photos import StockPhotoViewSet
from .views_image_editor import ImageEditorViewSet

app_name = 'social'

router = DefaultRouter()
router.register(r'accounts', SocialAccountViewSet, basename='social-account')
router.register(r'scheduled-posts', ScheduledPostViewSet, basename='scheduled-post')
router.register(r'posts', PostViewSet, basename='posts')
router.register(r'posting-schedules', PostingScheduleViewSet, basename='posting-schedule')
router.register(r'analytics', PublishedPostAnalyticsViewSet, basename='post-analytics')
router.register(r'image-generation', ImageGenerationViewSet, basename='image-generation')
router.register(r'stock-photos', StockPhotoViewSet, basename='stock-photos')
router.register(r'image-editor', ImageEditorViewSet, basename='image-editor')

urlpatterns = [
    path('', include(router.urls)),
]
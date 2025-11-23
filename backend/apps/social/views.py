"""
API Views for Social Media Integration
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Sum, Count, Avg
from django.db.models.functions import TruncDate
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
import secrets
import hashlib
import base64
import logging

from .models import SocialAccount, ScheduledPost, PostingSchedule, PublishedPostAnalytics
from .serializers import (
    SocialAccountSerializer,
    SocialAccountConnectSerializer,
    ScheduledPostSerializer,
    PostingScheduleSerializer,
    PublishedPostAnalyticsSerializer,
    PostAnalyticsSummarySerializer,
)
from .oauth.linkedin_oauth import LinkedInOAuth
from .oauth.twitter_oauth import TwitterOAuth
from .tasks import publish_scheduled_post, cancel_scheduled_post

logger = logging.getLogger(__name__)

class SocialAccountViewSet(viewsets.ModelViewSet):
    """ViewSet for managing social media accounts"""
    serializer_class = SocialAccountSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Return empty queryset if user is not authenticated
        if not self.request.user or not self.request.user.is_authenticated:
            return SocialAccount.objects.none()
        return SocialAccount.objects.filter(user=self.request.user).order_by('-created_at')
    
    def list(self, request, *args, **kwargs):
        """Override list to handle unauthenticated users gracefully"""
        try:
            if not request.user or not request.user.is_authenticated:
                return Response([], status=200)
            return super().list(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error listing social accounts: {e}")
            return Response([], status=200)  # Return empty list instead of 500
    
    @action(detail=False, methods=['post'], url_path='initiate-oauth')
    def initiate_oauth(self, request):
        platform = request.data.get('platform')
        if platform not in ['linkedin', 'twitter', 'facebook', 'instagram']:
            return Response({'error': 'Invalid platform'}, status=400)
        
        state = secrets.token_urlsafe(32)
        request.session[f'oauth_state_{platform}'] = state
        
        try:
            auth_url = ""
            if platform == 'linkedin':
                oauth = LinkedInOAuth()
                auth_url = oauth.get_authorization_url(state=state)
            elif platform == 'twitter':
                code_verifier = secrets.token_urlsafe(64)
                code_challenge = base64.urlsafe_b64encode(
                    hashlib.sha256(code_verifier.encode()).digest()
                ).decode().rstrip('=')
                request.session[f'code_verifier_{platform}'] = code_verifier
                oauth = TwitterOAuth()
                auth_url = oauth.get_authorization_url(code_challenge=code_challenge, state=state)
            
            return Response({'authorization_url': auth_url, 'state': state, 'platform': platform})
        except Exception as e:
            logger.error(f"OAuth init failed: {e}")
            return Response({'error': str(e)}, status=500)
    
    @action(detail=False, methods=['post'], url_path='connect')
    def connect_account(self, request):
        serializer = SocialAccountConnectSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        platform = serializer.validated_data['platform']
        code = serializer.validated_data['code']
        state = request.data.get('state')
        
        # Log request details for debugging
        logger.info(f"OAuth connect attempt for {platform}")
        logger.info(f"State received: {state}")
        
        # Verify State
        stored_state = request.session.get(f'oauth_state_{platform}')
        logger.info(f"Stored state: {stored_state}")
        
        if stored_state and stored_state != state:
            logger.warning(f"State mismatch for {platform}: expected {stored_state}, got {state}")
            return Response({'error': 'Invalid state parameter. Please try connecting again.'}, status=400)
        
        try:
            defaults = {}
            account_id = None
            
            if platform == 'linkedin':
                oauth = LinkedInOAuth()
                logger.info(f"Attempting LinkedIn token exchange with code: {code[:10]}...")
                
                try:
                    token_data = oauth.exchange_code_for_token(code)
                    logger.info("LinkedIn token exchange successful")
                except Exception as token_error:
                    logger.error(f"LinkedIn token exchange error: {str(token_error)}")
                    # Clear the state to prevent reuse
                    if f'oauth_state_{platform}' in request.session:
                        del request.session[f'oauth_state_{platform}']
                    raise
                
                try:
                    user_info = oauth.get_user_info(token_data['access_token'])
                    logger.info(f"LinkedIn user info retrieved: {user_info.get('sub')}")
                except Exception as user_error:
                    logger.error(f"LinkedIn user info error: {str(user_error)}")
                    raise
                
                account_id = user_info.get('sub')
                # FIX: Updated fields to match model (account_handle, profile_image_url)
                defaults = {
                    'account_name': user_info.get('name', 'LinkedIn User'),
                    'account_handle': user_info.get('email', '').split('@')[0],
                    'profile_image_url': user_info.get('picture', ''),
                    'access_token': token_data['access_token'],
                    'refresh_token': token_data.get('refresh_token'),
                    'token_expires_at': token_data.get('expires_at'),
                }
            elif platform == 'twitter':
                code_verifier = request.session.get(f'code_verifier_{platform}')
                if not code_verifier:
                    logger.error("Twitter code_verifier not found in session")
                    return Response({'error': 'Session expired. Please try connecting again.'}, status=400)
                
                oauth = TwitterOAuth()
                token_data = oauth.exchange_code_for_token(code, code_verifier)
                user_info = oauth.get_user_info(token_data['access_token'])
                data = user_info.get('data', {})
                account_id = data.get('id')
                # FIX: Updated fields to match model
                defaults = {
                    'account_name': data.get('name', 'Twitter User'),
                    'account_handle': data.get('username', ''),
                    'profile_image_url': data.get('profile_image_url', ''),
                    'access_token': token_data['access_token'],
                    'refresh_token': token_data.get('refresh_token'),
                    'token_expires_at': token_data.get('expires_at'),
                }
                
                # Clear code_verifier after use
                if f'code_verifier_{platform}' in request.session:
                    del request.session[f'code_verifier_{platform}']

            if not account_id:
                return Response({'error': 'Failed to retrieve account ID'}, status=400)

            # Clear state after successful connection
            if f'oauth_state_{platform}' in request.session:
                del request.session[f'oauth_state_{platform}']

            account, created = SocialAccount.objects.update_or_create(
                user=request.user,
                platform=platform,
                account_id=account_id,
                defaults=defaults
            )
            
            action = "connected" if created else "updated"
            logger.info(f"LinkedIn account {action} successfully for user {request.user.id}")
            
            return Response({'message': 'Connected', 'account': SocialAccountSerializer(account).data})
            
        except Exception as e:
            logger.error(f"Connection failed for {platform}: {str(e)}")
            # Clean up session on error
            if f'oauth_state_{platform}' in request.session:
                del request.session[f'oauth_state_{platform}']
            if f'code_verifier_{platform}' in request.session:
                del request.session[f'code_verifier_{platform}']
            return Response({'error': str(e)}, status=500)

    @action(detail=True, methods=['post'], url_path='disconnect')
    def disconnect_account(self, request, pk=None):
        account = self.get_object()
        account.delete()
        return Response({'message': 'Account disconnected'})


class ScheduledPostViewSet(viewsets.ModelViewSet):
    serializer_class = ScheduledPostSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return ScheduledPost.objects.filter(
            social_account__user=self.request.user
        ).order_by('-scheduled_time')
    
    def perform_create(self, serializer):
        social_account = serializer.validated_data['social_account']
        if social_account.user != self.request.user:
            raise PermissionDenied("Invalid account")
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['post'], url_path='publish-now')
    def publish_now(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        post = serializer.save(user=self.request.user, status='pending', scheduled_time=timezone.now())
        task = publish_scheduled_post.delay(post.id)
        post.celery_task_id = task.id
        post.save()
        return Response({'status': 'queued', 'task_id': task.id}, status=201)


class PostViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'], url_path='direct-post')
    def direct_post(self, request):
        platform = request.data.get('platform')
        content = request.data.get('content')
        
        account = SocialAccount.objects.filter(user=request.user, platform=platform, is_active=True).first()
        if not account:
            return Response({'error': f'No active {platform} account found. Please connect one first.'}, status=404)

        image_urls = []
        if 'images' in request.FILES:
            images = request.FILES.getlist('images')
            for img in images:
                file_path = default_storage.save(f"posts/{request.user.id}/{img.name}", ContentFile(img.read()))
                url = request.build_absolute_uri(settings.MEDIA_URL + file_path) if settings.MEDIA_URL else file_path
                image_urls.append(url)

        post = ScheduledPost.objects.create(
            user=request.user,
            social_account=account,
            content_text=content,
            images=image_urls,
            scheduled_time=timezone.now(),
            status='pending',
            metadata={'type': 'direct'}
        )
        
        task = publish_scheduled_post.delay(post.id)
        post.celery_task_id = task.id
        post.save()

        return Response({'status': 'queued', 'post_id': post.id}, status=201)


# --- FIX: Added the missing PostingScheduleViewSet ---
class PostingScheduleViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PostingScheduleSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return PostingSchedule.objects.filter(user=self.request.user)


class PublishedPostAnalyticsViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PublishedPostAnalyticsSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return PublishedPostAnalytics.objects.filter(
            scheduled_post__user=self.request.user
        ).order_by('-published_at')

    @action(detail=False, methods=['get'], url_path='summary')
    def analytics_summary(self, request):
        qs = self.get_queryset()
        total_posts = qs.count()
        aggs = qs.aggregate(
            total_likes=Sum('likes_count'),
            total_comments=Sum('comments_count'),
            total_shares=Sum('shares_count'),
            total_impressions=Sum('impressions'),
            avg_engagement=Avg('engagement_rate')
        )
        platforms = qs.values('scheduled_post__social_account__platform').annotate(
            count=Count('id'),
            engagement=Avg('engagement_rate')
        )
        return Response({
            'total_posts': total_posts,
            'total_likes': aggs['total_likes'] or 0,
            'total_comments': aggs['total_comments'] or 0,
            'total_impressions': aggs['total_impressions'] or 0,
            'avg_engagement_rate': aggs['avg_engagement'] or 0.0,
            'platform_breakdown': list(platforms)
        })

    @action(detail=False, methods=['get'], url_path='dashboard-data')
    def dashboard_data(self, request):
        qs = self.get_queryset()
        daily_stats = qs.annotate(date=TruncDate('published_at')).values('date').annotate(
            impressions=Sum('impressions'),
            likes=Sum('likes_count')
        ).order_by('date')[:30]
        
        top_posts = qs.order_by('-engagement_rate')[:5]
        top_posts_data = PublishedPostAnalyticsSerializer(top_posts, many=True).data
        
        return Response({
            'engagement_trend': list(daily_stats),
            'top_posts': top_posts_data
        })
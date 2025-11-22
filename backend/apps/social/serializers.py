"""
Serializers for Social Media Integration
"""
from rest_framework import serializers
from .models import SocialAccount, ScheduledPost, PostingSchedule, PublishedPostAnalytics
from django.utils import timezone


class SocialAccountSerializer(serializers.ModelSerializer):
    """Serializer for social media accounts"""
    
    is_token_expired = serializers.SerializerMethodField()
    days_until_expiry = serializers.SerializerMethodField()
    
    class Meta:
        model = SocialAccount
        fields = [
            'id',
            'platform',
            'account_id',
            'account_name',
            'account_username',
            'profile_picture_url',
            'is_active',
            'token_expires_at',
            'is_token_expired',
            'days_until_expiry',
            'metadata',
            'connected_at',
            'last_used_at',
        ]
        read_only_fields = [
            'id',
            'connected_at',
            'last_used_at',
        ]
    
    def get_is_token_expired(self, obj):
        """Check if token is expired"""
        if not obj.token_expires_at:
            return False
        return timezone.now() >= obj.token_expires_at
    
    def get_days_until_expiry(self, obj):
        """Calculate days until token expires"""
        if not obj.token_expires_at:
            return None
        delta = obj.token_expires_at - timezone.now()
        return max(0, delta.days)


class SocialAccountConnectSerializer(serializers.Serializer):
    """Serializer for connecting social accounts"""
    
    platform = serializers.ChoiceField(choices=['linkedin', 'twitter', 'facebook', 'instagram'])
    code = serializers.CharField(help_text="Authorization code from OAuth callback")
    code_verifier = serializers.CharField(
        required=False,
        help_text="PKCE code verifier (required for Twitter)"
    )


class ScheduledPostSerializer(serializers.ModelSerializer):
    """Serializer for scheduled posts"""
    
    social_account_name = serializers.CharField(
        source='social_account.account_name',
        read_only=True
    )
    social_account_platform = serializers.CharField(
        source='social_account.platform',
        read_only=True
    )
    time_until_post = serializers.SerializerMethodField()
    
    class Meta:
        model = ScheduledPost
        fields = [
            'id',
            'social_account',
            'social_account_name',
            'social_account_platform',
            'content_text',
            'content_html',
            'image_urls',
            'video_url',
            'scheduled_time',
            'time_until_post',
            'status',
            'error_message',
            'platform_post_id',
            'platform_post_url',
            'celery_task_id',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'status',
            'error_message',
            'platform_post_id',
            'platform_post_url',
            'celery_task_id',
            'created_at',
            'updated_at',
        ]
    
    def get_time_until_post(self, obj):
        """Calculate time until scheduled post"""
        if obj.status not in ['draft', 'pending']:
            return None
        
        delta = obj.scheduled_time - timezone.now()
        if delta.total_seconds() < 0:
            return "Overdue"
        
        hours = int(delta.total_seconds() // 3600)
        minutes = int((delta.total_seconds() % 3600) // 60)
        
        if hours > 24:
            days = hours // 24
            return f"{days} day{'s' if days != 1 else ''}"
        elif hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"
    
    def validate_scheduled_time(self, value):
        """Ensure scheduled time is in the future"""
        if value <= timezone.now():
            raise serializers.ValidationError("Scheduled time must be in the future")
        return value
    
    def validate_content_text(self, value):
        """Validate content length based on platform"""
        if not value or len(value.strip()) == 0:
            raise serializers.ValidationError("Content cannot be empty")
        
        # Platform-specific length limits
        platform = self.initial_data.get('social_account_platform')
        if platform == 'twitter' and len(value) > 280:
            raise serializers.ValidationError("Twitter posts cannot exceed 280 characters")
        elif platform == 'linkedin' and len(value) > 3000:
            raise serializers.ValidationError("LinkedIn posts cannot exceed 3000 characters")
        
        return value


class PostingScheduleSerializer(serializers.ModelSerializer):
    """Serializer for AI-recommended posting schedules"""
    
    social_account_name = serializers.CharField(
        source='social_account.account_name',
        read_only=True
    )
    time_slot_display = serializers.SerializerMethodField()
    
    class Meta:
        model = PostingSchedule
        fields = [
            'id',
            'social_account',
            'social_account_name',
            'weekday',
            'hour',
            'minute',
            'time_slot_display',
            'confidence_score',
            'reasoning',
            'historical_data',
            'is_active',
            'created_at',
        ]
        read_only_fields = [
            'id',
            'created_at',
        ]
    
    def get_time_slot_display(self, obj):
        """Format time slot for display"""
        weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        weekday_name = weekdays[obj.weekday] if 0 <= obj.weekday < 7 else 'Unknown'
        
        # Format time with AM/PM
        hour_12 = obj.hour % 12 or 12
        am_pm = 'AM' if obj.hour < 12 else 'PM'
        
        return f"{weekday_name} at {hour_12}:{obj.minute:02d} {am_pm}"


class PublishedPostAnalyticsSerializer(serializers.ModelSerializer):
    """Serializer for post analytics"""
    
    post_content = serializers.CharField(
        source='post.content_text',
        read_only=True
    )
    post_platform = serializers.CharField(
        source='post.social_account.platform',
        read_only=True
    )
    engagement_rate_display = serializers.SerializerMethodField()
    
    class Meta:
        model = PublishedPostAnalytics
        fields = [
            'id',
            'post',
            'post_content',
            'post_platform',
            'likes',
            'comments',
            'shares',
            'impressions',
            'reach',
            'clicks',
            'video_views',
            'saves',
            'engagement_rate',
            'engagement_rate_display',
            'click_through_rate',
            'platform_metadata',
            'fetched_at',
            'published_at',
        ]
        read_only_fields = [
            'id',
            'engagement_rate',
            'click_through_rate',
            'fetched_at',
        ]
    
    def get_engagement_rate_display(self, obj):
        """Format engagement rate as percentage"""
        if obj.engagement_rate:
            return f"{obj.engagement_rate:.2f}%"
        return "N/A"


class PostAnalyticsSummarySerializer(serializers.Serializer):
    """Serializer for aggregated analytics summary"""
    
    total_posts = serializers.IntegerField()
    total_likes = serializers.IntegerField()
    total_comments = serializers.IntegerField()
    total_shares = serializers.IntegerField()
    total_impressions = serializers.IntegerField()
    total_reach = serializers.IntegerField()
    avg_engagement_rate = serializers.FloatField()
    top_performing_post = PublishedPostAnalyticsSerializer(required=False)
    platform_breakdown = serializers.DictField()

from rest_framework import serializers
from .models import SocialAccount, ScheduledPost, PostingSchedule, PublishedPostAnalytics
from django.utils import timezone

class SocialAccountSerializer(serializers.ModelSerializer):
    is_token_expired = serializers.SerializerMethodField()
    days_until_expiry = serializers.SerializerMethodField()
    
    class Meta:
        model = SocialAccount
        fields = [
            'id',
            'platform',
            'account_id',
            'account_name',
            'account_handle',      # FIX: Updated field name
            'profile_image_url',   # FIX: Updated field name
            'is_active',
            'token_expires_at',
            'is_token_expired',
            'days_until_expiry',
            'account_data',        # FIX: Updated field name
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_is_token_expired(self, obj):
        if not obj.token_expires_at: return False
        return timezone.now() >= obj.token_expires_at
    
    def get_days_until_expiry(self, obj):
        if not obj.token_expires_at: return None
        delta = obj.token_expires_at - timezone.now()
        return max(0, delta.days)

class SocialAccountConnectSerializer(serializers.Serializer):
    platform = serializers.ChoiceField(choices=['linkedin', 'twitter', 'facebook', 'instagram'])
    code = serializers.CharField()
    code_verifier = serializers.CharField(required=False)

class ScheduledPostSerializer(serializers.ModelSerializer):
    social_account_name = serializers.CharField(source='social_account.account_name', read_only=True)
    social_account_platform = serializers.CharField(source='social_account.platform', read_only=True)
    time_until_post = serializers.SerializerMethodField()
    
    class Meta:
        model = ScheduledPost
        fields = [
            'id', 'social_account', 'social_account_name', 'social_account_platform',
            'content_text', 'content_html', 'images', 'video_url', 'scheduled_time',
            'time_until_post', 'status', 'error_message', 'platform_post_id', 
            'platform_post_url', 'celery_task_id', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'status', 'error_message', 'platform_post_id', 'platform_post_url', 'celery_task_id', 'created_at', 'updated_at']
    
    def get_time_until_post(self, obj):
        if obj.status not in ['draft', 'pending']: return None
        delta = obj.scheduled_time - timezone.now()
        return "Overdue" if delta.total_seconds() < 0 else f"{int(delta.total_seconds() // 60)}m"

    def validate_scheduled_time(self, value): return value
    def validate_content_text(self, value):
        if not value or len(value.strip()) == 0: raise serializers.ValidationError("Content cannot be empty")
        return value

class PostingScheduleSerializer(serializers.ModelSerializer):
    social_account_name = serializers.CharField(source='social_account.account_name', read_only=True)
    time_slot_display = serializers.SerializerMethodField()
    class Meta:
        model = PostingSchedule
        fields = '__all__'
    def get_time_slot_display(self, obj): return f"{obj.day_of_week} {obj.hour_utc}:{obj.minute}"

class PublishedPostAnalyticsSerializer(serializers.ModelSerializer):
    post_content = serializers.CharField(source='scheduled_post.content_text', read_only=True)
    post_platform = serializers.CharField(source='scheduled_post.social_account.platform', read_only=True)
    engagement_rate_display = serializers.SerializerMethodField()
    class Meta:
        model = PublishedPostAnalytics
        fields = '__all__'
    def get_engagement_rate_display(self, obj): return f"{obj.engagement_rate:.2f}%"

class PostAnalyticsSummarySerializer(serializers.Serializer):
    total_posts = serializers.IntegerField()
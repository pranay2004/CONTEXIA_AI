"""
Social Media Account and Scheduling Models
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
# from encrypted_model_fields.fields import EncryptedCharField, EncryptedTextField  # Disabled for now
import json

User = get_user_model()


class SocialAccount(models.Model):
    """Connected social media accounts with encrypted tokens"""
    
    PLATFORM_CHOICES = [
        ('linkedin', 'LinkedIn'),
        ('twitter', 'Twitter/X'),
        ('facebook', 'Facebook'),
        ('instagram', 'Instagram'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='social_accounts')
    platform = models.CharField(max_length=50, choices=PLATFORM_CHOICES)
    account_name = models.CharField(max_length=255)  # Display name
    account_id = models.CharField(max_length=255)  # Platform user ID
    account_handle = models.CharField(max_length=255, null=True, blank=True)  # @username
    profile_image_url = models.URLField(null=True, blank=True)
    
    # OAuth tokens (TODO: Add encryption in production)
    access_token = models.TextField()
    refresh_token = models.TextField(null=True, blank=True)
    token_expires_at = models.DateTimeField(null=True, blank=True)
    
    # Account status
    is_active = models.BooleanField(default=True)
    last_synced_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)
    
    # Metadata
    account_data = models.JSONField(default=dict)  # Platform-specific data
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'platform', 'account_id']
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'platform']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.account_name} ({self.get_platform_display()})"
    
    def is_token_expired(self):
        """Check if access token is expired"""
        if not self.token_expires_at:
            return False
        return timezone.now() >= self.token_expires_at
    
    def needs_refresh(self):
        """Check if token needs refresh (expires in < 1 hour)"""
        if not self.token_expires_at:
            return False
        return timezone.now() >= (self.token_expires_at - timezone.timedelta(hours=1))


class ScheduledPost(models.Model):
    """Posts scheduled for future publishing"""
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending', 'Pending'),
        ('published', 'Published'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='scheduled_posts')
    social_account = models.ForeignKey(SocialAccount, on_delete=models.CASCADE, related_name='scheduled_posts')
    
    # Content
    content_text = models.TextField()
    content_html = models.TextField(null=True, blank=True)
    images = models.JSONField(default=list)  # List of image URLs/IDs
    video_url = models.URLField(null=True, blank=True)
    link_url = models.URLField(null=True, blank=True)
    link_preview = models.JSONField(null=True, blank=True)
    
    # Scheduling
    scheduled_time = models.DateTimeField()
    timezone = models.CharField(max_length=50, default='UTC')
    is_optimal_time = models.BooleanField(default=False)  # AI recommended time
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    platform_post_id = models.CharField(max_length=255, null=True, blank=True)
    platform_post_url = models.URLField(null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)
    retry_count = models.IntegerField(default=0)
    
    # Publishing
    published_at = models.DateTimeField(null=True, blank=True)
    celery_task_id = models.CharField(max_length=255, null=True, blank=True)
    
    # Analytics (fetched after publishing)
    engagement_data = models.JSONField(null=True, blank=True)
    last_analytics_fetch = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    generated_content_id = models.IntegerField(null=True, blank=True)  # Link to GeneratedContent
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['scheduled_time']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['scheduled_time', 'status']),
            models.Index(fields=['social_account', 'status']),
        ]
    
    def __str__(self):
        return f"{self.social_account.platform} - {self.scheduled_time.strftime('%Y-%m-%d %H:%M')}"
    
    def is_ready_to_publish(self):
        """Check if post is ready to be published"""
        return (
            self.status == 'pending' and
            timezone.now() >= self.scheduled_time and
            self.social_account.is_active
        )
    
    def get_content_preview(self, length=100):
        """Get truncated content for preview"""
        if len(self.content_text) <= length:
            return self.content_text
        return self.content_text[:length] + '...'


class PostingSchedule(models.Model):
    """AI-recommended optimal posting times per user and platform"""
    
    WEEKDAY_CHOICES = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posting_schedules')
    platform = models.CharField(max_length=50)
    
    # Time slot
    day_of_week = models.IntegerField(choices=WEEKDAY_CHOICES)
    hour_utc = models.IntegerField()  # 0-23
    minute = models.IntegerField(default=0)  # 0, 15, 30, 45
    
    # AI Analysis
    score = models.FloatField()  # 0-100, confidence score
    reason = models.TextField()  # AI explanation
    based_on_data = models.JSONField(default=dict)  # Historical performance data
    
    # Status
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'platform', 'day_of_week', 'hour_utc', 'minute']
        ordering = ['-score']
        indexes = [
            models.Index(fields=['user', 'platform', '-score']),
        ]
    
    def __str__(self):
        day_name = dict(self.WEEKDAY_CHOICES)[self.day_of_week]
        return f"{self.platform} - {day_name} {self.hour_utc:02d}:{self.minute:02d} (Score: {self.score:.1f})"


class PublishedPostAnalytics(models.Model):
    """Analytics data for published posts"""
    
    scheduled_post = models.OneToOneField(ScheduledPost, on_delete=models.CASCADE, related_name='analytics')
    
    # Engagement metrics
    likes_count = models.IntegerField(default=0)
    comments_count = models.IntegerField(default=0)
    shares_count = models.IntegerField(default=0)
    retweets_count = models.IntegerField(default=0)  # Twitter
    saves_count = models.IntegerField(default=0)  # Instagram
    
    # Reach metrics
    impressions = models.IntegerField(default=0)
    reach = models.IntegerField(default=0)
    clicks = models.IntegerField(default=0)
    
    # Calculated metrics
    engagement_rate = models.FloatField(default=0.0)  # (likes+comments+shares)/impressions * 100
    ctr = models.FloatField(default=0.0)  # clicks/impressions * 100
    
    # Audience data
    audience_data = models.JSONField(null=True, blank=True)  # Demographics, locations
    
    # Timestamps
    first_fetch_at = models.DateTimeField(auto_now_add=True)
    last_fetch_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = 'Published post analytics'
    
    def __str__(self):
        return f"Analytics for {self.scheduled_post}"
    
    def calculate_engagement_rate(self):
        """Calculate engagement rate"""
        if self.impressions == 0:
            return 0.0
        total_engagement = self.likes_count + self.comments_count + self.shares_count
        return (total_engagement / self.impressions) * 100
    
    def calculate_ctr(self):
        """Calculate click-through rate"""
        if self.impressions == 0:
            return 0.0
        return (self.clicks / self.impressions) * 100

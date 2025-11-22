"""
Django Admin Configuration for Social Media Integration
"""
from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import SocialAccount, ScheduledPost, PostingSchedule, PublishedPostAnalytics


@admin.register(SocialAccount)
class SocialAccountAdmin(admin.ModelAdmin):
    """Admin interface for Social Accounts"""
    
    list_display = [
        'id',
        'user',
        'platform_badge',
        'account_handle',
        'account_name',
        'is_active',
        'token_status',
        'created_at',
    ]
    
    list_filter = [
        'platform',
        'is_active',
        'created_at',
    ]
    
    search_fields = [
        'user__username',
        'user__email',
        'account_name',
        'account_handle',
        'account_id',
    ]
    
    readonly_fields = [
        'id',
        'account_id',
        'created_at',
        'last_synced_at',
        'token_status_detail',
    ]
    
    fieldsets = (
        ('Account Information', {
            'fields': (
                'id',
                'user',
                'platform',
                'account_id',
                'account_name',
                'account_handle',
                'profile_image_url',
            )
        }),
        ('OAuth Tokens', {
            'fields': (
                'access_token',
                'refresh_token',
                'token_expires_at',
                'token_status_detail',
            ),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': (
                'is_active',
                'created_at',
                'last_synced_at',
                'error_message',
            )
        }),
        ('Metadata', {
            'fields': ('account_data',),
            'classes': ('collapse',)
        }),
    )
    
    def platform_badge(self, obj):
        """Display platform with colored badge"""
        colors = {
            'linkedin': '#0077B5',
            'twitter': '#1DA1F2',
            'facebook': '#4267B2',
            'instagram': '#E4405F',
        }
        color = colors.get(obj.platform, '#666')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.platform.upper()
        )
    platform_badge.short_description = 'Platform'
    
    def token_status(self, obj):
        """Display token expiration status"""
        if not obj.token_expires_at:
            return format_html('<span style="color: gray;">No expiration</span>')
        
        now = timezone.now()
        if now >= obj.token_expires_at:
            return format_html('<span style="color: red;">❌ Expired</span>')
        
        days_left = (obj.token_expires_at - now).days
        if days_left < 7:
            return format_html('<span style="color: orange;">⚠️ {} days</span>', days_left)
        
        return format_html('<span style="color: green;">✅ {} days</span>', days_left)
    token_status.short_description = 'Token Status'
    
    def token_status_detail(self, obj):
        """Detailed token status"""
        if not obj.token_expires_at:
            return "No expiration set"
        
        now = timezone.now()
        if now >= obj.token_expires_at:
            return format_html('<span style="color: red; font-weight: bold;">EXPIRED on {}</span>', obj.token_expires_at)
        
        delta = obj.token_expires_at - now
        return f"Expires in {delta.days} days ({obj.token_expires_at})"
    token_status_detail.short_description = 'Token Expiration Details'


@admin.register(ScheduledPost)
class ScheduledPostAdmin(admin.ModelAdmin):
    """Admin interface for Scheduled Posts"""
    
    list_display = [
        'id',
        'social_account',
        'content_preview',
        'scheduled_time',
        'status_badge',
        'created_at',
    ]
    
    list_filter = [
        'status',
        'social_account__platform',
        'scheduled_time',
        'created_at',
    ]
    
    search_fields = [
        'content_text',
        'social_account__account_name',
        'social_account__user__username',
    ]
    
    readonly_fields = [
        'id',
        'celery_task_id',
        'platform_post_id',
        'platform_post_url',
        'created_at',
        'updated_at',
    ]
    
    fieldsets = (
        ('Post Information', {
            'fields': (
                'id',
                'social_account',
                'content_text',
                'content_html',
            )
        }),
        ('Media', {
            'fields': (
                'images',
                'video_url',
                'link_url',
            )
        }),
        ('Scheduling', {
            'fields': (
                'scheduled_time',
                'status',
                'celery_task_id',
            )
        }),
        ('Platform Response', {
            'fields': (
                'platform_post_id',
                'platform_post_url',
                'error_message',
            ),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': (
                'created_at',
                'updated_at',
            )
        }),
    )
    
    def content_preview(self, obj):
        """Show content preview"""
        preview = obj.content_text[:100]
        if len(obj.content_text) > 100:
            preview += '...'
        return preview
    content_preview.short_description = 'Content'
    
    def status_badge(self, obj):
        """Display status with colored badge"""
        colors = {
            'draft': '#6c757d',
            'pending': '#ffc107',
            'published': '#28a745',
            'failed': '#dc3545',
            'cancelled': '#6c757d',
        }
        color = colors.get(obj.status, '#666')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.status.upper()
        )
    status_badge.short_description = 'Status'


@admin.register(PostingSchedule)
class PostingScheduleAdmin(admin.ModelAdmin):
    """Admin interface for Posting Schedules"""
    
    list_display = [
        'id',
        'user',
        'platform',
        'time_slot_display',
        'confidence_badge',
        'is_active',
        'created_at',
    ]
    
    list_filter = [
        'day_of_week',
        'is_active',
        'platform',
        'created_at',
    ]
    
    search_fields = [
        'user__username',
        'platform',
        'reason',
    ]
    
    readonly_fields = [
        'id',
        'created_at',
    ]
    
    fieldsets = (
        ('Schedule Information', {
            'fields': (
                'id',
                'user',
                'platform',
                'day_of_week',
                'hour_utc',
                'minute',
            )
        }),
        ('AI Recommendations', {
            'fields': (
                'score',
                'reason',
                'based_on_data',
            )
        }),
        ('Status', {
            'fields': (
                'is_active',
                'created_at',
            )
        }),
    )
    
    def time_slot_display(self, obj):
        """Format time slot"""
        weekdays = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        weekday = weekdays[obj.day_of_week] if 0 <= obj.day_of_week < 7 else '?'
        hour_12 = obj.hour_utc % 12 or 12
        am_pm = 'AM' if obj.hour_utc < 12 else 'PM'
        return f"{weekday} {hour_12}:{obj.minute:02d} {am_pm}"
    time_slot_display.short_description = 'Time Slot'
    
    def confidence_badge(self, obj):
        """Display confidence score with color"""
        if obj.score >= 80:
            color = '#28a745'
        elif obj.score >= 60:
            color = '#ffc107'
        else:
            color = '#dc3545'
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-weight: bold;">{}%</span>',
            color,
            int(obj.score)
        )
    confidence_badge.short_description = 'Confidence'


@admin.register(PublishedPostAnalytics)
class PublishedPostAnalyticsAdmin(admin.ModelAdmin):
    """Admin interface for Post Analytics"""
    
    list_display = [
        'id',
        'scheduled_post',
        'first_fetch_at',
        'engagement_display',
        'reach_display',
        'engagement_rate_display',
    ]
    
    list_filter = [
        'scheduled_post__social_account__platform',
        'first_fetch_at',
        'last_fetch_at',
    ]
    
    search_fields = [
        'scheduled_post__content_text',
        'scheduled_post__social_account__account_name',
    ]
    
    readonly_fields = [
        'id',
        'engagement_rate',
        'ctr',
        'first_fetch_at',
        'last_fetch_at',
    ]
    
    fieldsets = (
        ('Post Information', {
            'fields': (
                'id',
                'scheduled_post',
                'first_fetch_at',
                'last_fetch_at',
            )
        }),
        ('Engagement Metrics', {
            'fields': (
                'likes_count',
                'comments_count',
                'shares_count',
                'retweets_count',
                'saves_count',
            )
        }),
        ('Reach Metrics', {
            'fields': (
                'impressions',
                'reach',
                'clicks',
            )
        }),
        ('Calculated Metrics', {
            'fields': (
                'engagement_rate',
                'ctr',
            )
        }),
        ('Platform Data', {
            'fields': (
                'audience_data',
            ),
            'classes': ('collapse',)
        }),
    )
    
    def engagement_display(self, obj):
        """Display total engagement"""
        total = (obj.likes_count or 0) + (obj.comments_count or 0) + (obj.shares_count or 0)
        return format_html('<strong>{:,}</strong>', total)
    engagement_display.short_description = 'Total Engagement'
    
    def reach_display(self, obj):
        """Display reach/impressions"""
        reach = obj.reach or obj.impressions or 0
        return format_html('{:,}', reach)
    reach_display.short_description = 'Reach'
    
    def engagement_rate_display(self, obj):
        """Display engagement rate"""
        if obj.engagement_rate:
            if obj.engagement_rate >= 5:
                color = '#28a745'
            elif obj.engagement_rate >= 2:
                color = '#ffc107'
            else:
                color = '#dc3545'
            
            return format_html(
                '<span style="color: {}; font-weight: bold;">{:.2f}%</span>',
                color,
                obj.engagement_rate
            )
        return 'N/A'
    engagement_rate_display.short_description = 'Engagement Rate'

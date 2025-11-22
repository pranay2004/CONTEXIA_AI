"""
Signals for social media integration
"""
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from .models import ScheduledPost, PublishedPostAnalytics


@receiver(post_save, sender=ScheduledPost)
def create_analytics_on_publish(sender, instance, created, **kwargs):
    """Create analytics record when post is published"""
    if instance.status == 'published' and instance.platform_post_id:
        PublishedPostAnalytics.objects.get_or_create(
            scheduled_post=instance,
            defaults={
                'impressions': 0,
                'reach': 0,
                'clicks': 0,
            }
        )


@receiver(pre_save, sender=ScheduledPost)
def set_published_timestamp(sender, instance, **kwargs):
    """Set published_at timestamp when status changes to published"""
    if instance.pk:
        old_instance = ScheduledPost.objects.filter(pk=instance.pk).first()
        if old_instance and old_instance.status != 'published' and instance.status == 'published':
            instance.published_at = timezone.now()

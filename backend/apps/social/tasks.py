"""
Celery Tasks for Social Media Publishing
"""
from celery import shared_task
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=300)
def publish_scheduled_post(self, post_id: int):
    """
    Celery task to publish a scheduled post
    
    Args:
        post_id: ScheduledPost ID
        
    Retries: 3 times with 5 minute delay
    """
    from apps.social.models import ScheduledPost
    from apps.social.publishers import (
        LinkedInPublisher, 
        TwitterPublisher,
        FacebookPublisher,
        InstagramPublisher
    )
    from apps.social.publishers.base import PublishError
    
    try:
        # Get post
        post = ScheduledPost.objects.select_related('social_account').get(id=post_id)
        
        # Check if already published or cancelled
        if post.status in ['published', 'cancelled']:
            logger.info(f"Post {post_id} already {post.status}, skipping")
            return f"Post {post_id} already {post.status}"
        
        # Update status to publishing
        post.status = 'publishing'
        post.save()
        
        # Get appropriate publisher
        platform = post.social_account.platform
        publisher_map = {
            'linkedin': LinkedInPublisher,
            'twitter': TwitterPublisher,
            'facebook': FacebookPublisher,
            'instagram': InstagramPublisher,
        }
        
        if platform not in publisher_map:
            raise ValueError(f"Unsupported platform: {platform}")
        
        publisher = publisher_map[platform](post.social_account)
        
        # Publish based on media type
        try:
            if post.video_url:
                # Video post
                result = publisher.publish_with_video(
                    content=post.content_text or post.content_html,
                    video_url=post.video_url
                )
            elif post.image_urls and len(post.image_urls) > 0:
                # Image post
                result = publisher.publish_with_image(
                    content=post.content_text or post.content_html,
                    image_urls=post.image_urls
                )
            else:
                # Text only
                result = publisher.publish_text(
                    content=post.content_text or post.content_html
                )
            
            # Update post with success
            publisher.update_post_status(
                post=post,
                status='published',
                platform_post_id=result['post_id'],
                platform_post_url=result['post_url']
            )
            
            # Create analytics record
            from apps.social.models import PublishedPostAnalytics
            PublishedPostAnalytics.objects.create(post=post)
            
            logger.info(f"Successfully published post {post_id} to {platform}")
            return f"Published post {post_id} to {platform}: {result['post_url']}"
            
        except PublishError as e:
            # Publishing failed - update status
            publisher.update_post_status(
                post=post,
                status='failed',
                error_message=str(e)
            )
            publisher.log_publish_attempt(post=post, success=False, error=str(e))
            
            # Retry if we have retries left
            if self.request.retries < self.max_retries:
                logger.warning(f"Post {post_id} publish failed, retrying: {e}")
                raise self.retry(exc=e)
            else:
                logger.error(f"Post {post_id} publish failed after {self.max_retries} retries: {e}")
                raise
        
    except ObjectDoesNotExist:
        logger.error(f"Post {post_id} not found")
        raise
    except Exception as e:
        logger.error(f"Unexpected error publishing post {post_id}: {e}", exc_info=True)
        
        # Try to update post status
        try:
            post = ScheduledPost.objects.get(id=post_id)
            post.status = 'failed'
            post.error_message = f"Unexpected error: {str(e)}"
            post.save()
        except:
            pass
        
        # Retry if possible
        if self.request.retries < self.max_retries:
            raise self.retry(exc=e)
        else:
            raise


@shared_task
def check_and_publish_due_posts():
    """
    Periodic task to check for posts due for publishing
    
    Should be run every minute via Celery Beat
    """
    from apps.social.models import ScheduledPost
    
    # Get posts that are due
    now = timezone.now()
    due_posts = ScheduledPost.objects.filter(
        status='pending',
        scheduled_time__lte=now
    ).select_related('social_account')
    
    count = 0
    for post in due_posts:
        # Queue for publishing
        task = publish_scheduled_post.delay(post.id)
        
        # Store task ID
        post.celery_task_id = task.id
        post.save()
        
        count += 1
        logger.info(f"Queued post {post.id} for publishing (task {task.id})")
    
    if count > 0:
        logger.info(f"Queued {count} posts for publishing")
    
    return f"Queued {count} posts for publishing"


@shared_task
def retry_failed_post(post_id: int):
    """
    Retry a failed post
    
    Args:
        post_id: ScheduledPost ID
    """
    from apps.social.models import ScheduledPost
    
    try:
        post = ScheduledPost.objects.get(id=post_id)
        
        if post.status != 'failed':
            return f"Post {post_id} is not in failed status"
        
        # Reset status to pending
        post.status = 'pending'
        post.error_message = None
        post.save()
        
        # Queue for publishing
        task = publish_scheduled_post.delay(post_id)
        post.celery_task_id = task.id
        post.save()
        
        logger.info(f"Retrying failed post {post_id} (task {task.id})")
        return f"Retrying post {post_id}"
        
    except ObjectDoesNotExist:
        logger.error(f"Post {post_id} not found")
        raise


@shared_task
def cancel_scheduled_post(post_id: int):
    """
    Cancel a scheduled post
    
    Args:
        post_id: ScheduledPost ID
    """
    from apps.social.models import ScheduledPost
    from celery.result import AsyncResult
    
    try:
        post = ScheduledPost.objects.get(id=post_id)
        
        # Revoke Celery task if exists
        if post.celery_task_id:
            AsyncResult(post.celery_task_id).revoke(terminate=True)
            logger.info(f"Revoked Celery task {post.celery_task_id}")
        
        # Update status
        post.status = 'cancelled'
        post.save()
        
        logger.info(f"Cancelled post {post_id}")
        return f"Cancelled post {post_id}"
        
    except ObjectDoesNotExist:
        logger.error(f"Post {post_id} not found")
        raise


@shared_task
def update_post_analytics(post_id: int):
    """
    Fetch and update analytics for a published post
    
    Args:
        post_id: ScheduledPost ID
    """
    from apps.social.models import ScheduledPost, PublishedPostAnalytics
    
    try:
        post = ScheduledPost.objects.select_related('social_account').get(id=post_id)
        
        if post.status != 'published' or not post.platform_post_id:
            return f"Post {post_id} not published or missing platform ID"
        
        # Get or create analytics record
        analytics, created = PublishedPostAnalytics.objects.get_or_create(post=post)
        
        # Fetch analytics from platform
        # TODO: Implement platform-specific analytics fetchers
        # For now, this is a placeholder
        
        logger.info(f"Updated analytics for post {post_id}")
        return f"Updated analytics for post {post_id}"
        
    except ObjectDoesNotExist:
        logger.error(f"Post {post_id} not found")
        raise


@shared_task
def bulk_update_analytics():
    """
    Periodic task to update analytics for all published posts
    
    Should be run every hour via Celery Beat
    """
    from apps.social.models import ScheduledPost
    from django.utils import timezone
    
    # Get posts published in last 30 days
    since = timezone.now() - timezone.timedelta(days=30)
    published_posts = ScheduledPost.objects.filter(
        status='published',
        scheduled_time__gte=since
    ).values_list('id', flat=True)
    
    count = 0
    for post_id in published_posts:
        update_post_analytics.delay(post_id)
        count += 1
    
    logger.info(f"Queued {count} posts for analytics update")
    return f"Queued {count} posts for analytics update"

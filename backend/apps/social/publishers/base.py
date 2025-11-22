"""
Base Publisher Abstract Class
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional
import logging
from django.utils import timezone

logger = logging.getLogger(__name__)


class PublishError(Exception):
    """Custom exception for publishing errors"""
    pass


class BasePublisher(ABC):
    """Abstract base class for all social media publishers"""
    
    def __init__(self, social_account):
        """
        Initialize publisher with social account
        
        Args:
            social_account: SocialAccount model instance
        """
        self.social_account = social_account
        self.platform = social_account.platform
        self.access_token = social_account.access_token
        
    @abstractmethod
    def publish_text(self, content: str) -> Dict[str, str]:
        """
        Publish text-only post
        
        Args:
            content: Post content text
            
        Returns:
            dict: {'post_id': str, 'post_url': str}
            
        Raises:
            PublishError: If publishing fails
        """
        pass
    
    @abstractmethod
    def publish_with_image(self, content: str, image_urls: List[str]) -> Dict[str, str]:
        """
        Publish post with images
        
        Args:
            content: Post content text
            image_urls: List of image URLs to attach
            
        Returns:
            dict: {'post_id': str, 'post_url': str}
            
        Raises:
            PublishError: If publishing fails
        """
        pass
    
    @abstractmethod
    def publish_with_video(self, content: str, video_url: str) -> Dict[str, str]:
        """
        Publish post with video
        
        Args:
            content: Post content text
            video_url: Video URL to attach
            
        Returns:
            dict: {'post_id': str, 'post_url': str}
            
        Raises:
            PublishError: If publishing fails
        """
        pass
    
    def validate_content(self, content: str) -> bool:
        """
        Validate content meets platform requirements
        
        Args:
            content: Post content to validate
            
        Returns:
            bool: True if valid
            
        Raises:
            PublishError: If content is invalid
        """
        if not content or len(content.strip()) == 0:
            raise PublishError("Content cannot be empty")
        return True
    
    def refresh_token_if_needed(self) -> None:
        """
        Check if token is expired and refresh if needed
        """
        if not self.social_account.token_expires_at:
            return
            
        now = timezone.now()
        # Refresh if token expires in less than 1 hour
        if self.social_account.token_expires_at <= now + timezone.timedelta(hours=1):
            logger.info(f"Token expiring soon for {self.platform} account {self.social_account.id}, refreshing...")
            try:
                # Import here to avoid circular dependency
                from apps.social.views import SocialAccountViewSet
                # Refresh token logic handled in views
                logger.warning("Token refresh needed - implement via API endpoint")
            except Exception as e:
                logger.error(f"Token refresh failed: {e}")
                raise PublishError(f"Token expired and refresh failed: {str(e)}")
    
    def update_post_status(self, post, status: str, error_message: Optional[str] = None,
                          platform_post_id: Optional[str] = None, 
                          platform_post_url: Optional[str] = None) -> None:
        """
        Update scheduled post status after publishing
        
        Args:
            post: ScheduledPost model instance
            status: New status (published/failed)
            error_message: Error message if failed
            platform_post_id: ID returned by platform
            platform_post_url: URL to published post
        """
        post.status = status
        if error_message:
            post.error_message = error_message
        if platform_post_id:
            post.platform_post_id = platform_post_id
        if platform_post_url:
            post.platform_post_url = platform_post_url
        post.save()
        
        logger.info(f"Post {post.id} status updated to {status}")
    
    def log_publish_attempt(self, post, success: bool, error: Optional[str] = None) -> None:
        """
        Log publishing attempt for debugging
        
        Args:
            post: ScheduledPost model instance
            success: Whether publishing succeeded
            error: Error message if failed
        """
        log_data = {
            'post_id': post.id,
            'platform': self.platform,
            'account': self.social_account.account_username,
            'success': success,
            'timestamp': timezone.now().isoformat(),
        }
        
        if error:
            log_data['error'] = error
            logger.error(f"Publishing failed: {log_data}")
        else:
            logger.info(f"Publishing succeeded: {log_data}")

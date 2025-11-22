"""
Facebook Publisher
API Documentation: https://developers.facebook.com/docs/graph-api/reference/page/feed
"""
import requests
from typing import Dict, List
import logging
from .base import BasePublisher, PublishError

logger = logging.getLogger(__name__)


class FacebookPublisher(BasePublisher):
    """Publisher for Facebook posts"""
    
    API_BASE = 'https://graph.facebook.com/v18.0'
    MAX_CONTENT_LENGTH = 63206
    
    def __init__(self, social_account):
        super().__init__(social_account)
        # Get primary Facebook page from metadata
        self.page_id = None
        self.page_access_token = None
        
        if social_account.metadata and 'pages' in social_account.metadata:
            pages = social_account.metadata['pages']
            if pages and len(pages) > 0:
                # Use first page
                self.page_id = pages[0]['id']
                self.page_access_token = pages[0].get('access_token', self.access_token)
    
    def validate_content(self, content: str) -> bool:
        """Validate Facebook content length"""
        super().validate_content(content)
        if len(content) > self.MAX_CONTENT_LENGTH:
            raise PublishError(f"Facebook posts cannot exceed {self.MAX_CONTENT_LENGTH} characters")
        return True
    
    def publish_text(self, content: str) -> Dict[str, str]:
        """
        Publish text-only post to Facebook Page
        
        Returns:
            dict: {'post_id': str, 'post_url': str}
        """
        self.validate_content(content)
        self.refresh_token_if_needed()
        
        if not self.page_id:
            raise PublishError("No Facebook Page found in account metadata")
        
        try:
            params = {
                'message': content,
                'access_token': self.page_access_token or self.access_token,
            }
            
            response = requests.post(
                f'{self.API_BASE}/{self.page_id}/feed',
                params=params,
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            post_id = data['id']
            post_url = f"https://www.facebook.com/{post_id}"
            
            logger.info(f"Facebook post published successfully: {post_id}")
            
            return {
                'post_id': post_id,
                'post_url': post_url
            }
            
        except requests.RequestException as e:
            error_msg = f"Facebook API error: {str(e)}"
            if hasattr(e, 'response') and e.response is not None:
                error_msg += f" - {e.response.text}"
            logger.error(error_msg)
            raise PublishError(error_msg)
    
    def publish_with_image(self, content: str, image_urls: List[str]) -> Dict[str, str]:
        """
        Publish post with images to Facebook Page
        
        Note: Multiple images require creating a photo album
        """
        self.validate_content(content)
        self.refresh_token_if_needed()
        
        if not self.page_id:
            raise PublishError("No Facebook Page found in account metadata")
        
        try:
            if len(image_urls) == 1:
                # Single image - simple photo post
                params = {
                    'message': content,
                    'url': image_urls[0],
                    'access_token': self.page_access_token or self.access_token,
                }
                
                response = requests.post(
                    f'{self.API_BASE}/{self.page_id}/photos',
                    params=params,
                    timeout=30
                )
                response.raise_for_status()
                
                data = response.json()
                post_id = data['post_id'] if 'post_id' in data else data['id']
                
            else:
                # Multiple images - create album and add photos
                # First create unpublished photos
                attached_media = []
                for image_url in image_urls:
                    photo_params = {
                        'url': image_url,
                        'published': 'false',
                        'access_token': self.page_access_token or self.access_token,
                    }
                    
                    photo_response = requests.post(
                        f'{self.API_BASE}/{self.page_id}/photos',
                        params=photo_params,
                        timeout=30
                    )
                    photo_response.raise_for_status()
                    photo_data = photo_response.json()
                    attached_media.append({'media_fbid': photo_data['id']})
                
                # Create post with all photos
                params = {
                    'message': content,
                    'attached_media': str(attached_media),
                    'access_token': self.page_access_token or self.access_token,
                }
                
                response = requests.post(
                    f'{self.API_BASE}/{self.page_id}/feed',
                    params=params,
                    timeout=30
                )
                response.raise_for_status()
                
                data = response.json()
                post_id = data['id']
            
            post_url = f"https://www.facebook.com/{post_id}"
            
            logger.info(f"Facebook post with images published: {post_id}")
            
            return {
                'post_id': post_id,
                'post_url': post_url
            }
            
        except Exception as e:
            error_msg = f"Facebook image post error: {str(e)}"
            logger.error(error_msg)
            raise PublishError(error_msg)
    
    def publish_with_video(self, content: str, video_url: str) -> Dict[str, str]:
        """
        Publish post with video to Facebook Page
        """
        self.validate_content(content)
        self.refresh_token_if_needed()
        
        if not self.page_id:
            raise PublishError("No Facebook Page found in account metadata")
        
        try:
            params = {
                'description': content,
                'file_url': video_url,
                'access_token': self.page_access_token or self.access_token,
            }
            
            response = requests.post(
                f'{self.API_BASE}/{self.page_id}/videos',
                params=params,
                timeout=60
            )
            response.raise_for_status()
            
            data = response.json()
            post_id = data['id']
            post_url = f"https://www.facebook.com/{post_id}"
            
            logger.info(f"Facebook video post published: {post_id}")
            
            return {
                'post_id': post_id,
                'post_url': post_url
            }
            
        except requests.RequestException as e:
            error_msg = f"Facebook video post error: {str(e)}"
            if hasattr(e, 'response') and e.response is not None:
                error_msg += f" - {e.response.text}"
            logger.error(error_msg)
            raise PublishError(error_msg)

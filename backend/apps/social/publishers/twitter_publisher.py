"""
Twitter/X Publisher
API Documentation: https://developer.twitter.com/en/docs/twitter-api/tweets/manage-tweets/introduction
"""
import requests
from typing import Dict, List
import logging
from .base import BasePublisher, PublishError

logger = logging.getLogger(__name__)


class TwitterPublisher(BasePublisher):
    """Publisher for Twitter/X posts"""
    
    API_BASE = 'https://api.twitter.com/2'
    MAX_CONTENT_LENGTH = 280
    MAX_IMAGES = 4
    
    def validate_content(self, content: str) -> bool:
        """Validate Twitter content length"""
        super().validate_content(content)
        if len(content) > self.MAX_CONTENT_LENGTH:
            raise PublishError(f"Twitter posts cannot exceed {self.MAX_CONTENT_LENGTH} characters")
        return True
    
    def publish_text(self, content: str) -> Dict[str, str]:
        """
        Publish text-only tweet
        
        Returns:
            dict: {'post_id': str, 'post_url': str}
        """
        self.validate_content(content)
        self.refresh_token_if_needed()
        
        try:
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json',
            }
            
            payload = {
                'text': content
            }
            
            response = requests.post(
                f'{self.API_BASE}/tweets',
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            post_id = data['data']['id']
            post_url = f"https://twitter.com/i/web/status/{post_id}"
            
            logger.info(f"Twitter post published successfully: {post_id}")
            
            return {
                'post_id': post_id,
                'post_url': post_url
            }
            
        except requests.RequestException as e:
            error_msg = f"Twitter API error: {str(e)}"
            if hasattr(e, 'response') and e.response is not None:
                error_msg += f" - {e.response.text}"
            logger.error(error_msg)
            raise PublishError(error_msg)
    
    def publish_with_image(self, content: str, image_urls: List[str]) -> Dict[str, str]:
        """
        Publish tweet with images
        
        Twitter requires uploading images to media endpoint first
        """
        self.validate_content(content)
        self.refresh_token_if_needed()
        
        if len(image_urls) > self.MAX_IMAGES:
            raise PublishError(f"Twitter supports maximum {self.MAX_IMAGES} images per tweet")
        
        try:
            # Step 1: Upload images and get media IDs
            media_ids = []
            for image_url in image_urls:
                media_id = self._upload_image(image_url)
                media_ids.append(media_id)
            
            # Step 2: Create tweet with media
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json',
            }
            
            payload = {
                'text': content,
                'media': {
                    'media_ids': media_ids
                }
            }
            
            response = requests.post(
                f'{self.API_BASE}/tweets',
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            post_id = data['data']['id']
            post_url = f"https://twitter.com/i/web/status/{post_id}"
            
            logger.info(f"Twitter post with images published: {post_id}")
            
            return {
                'post_id': post_id,
                'post_url': post_url
            }
            
        except Exception as e:
            error_msg = f"Twitter image post error: {str(e)}"
            logger.error(error_msg)
            raise PublishError(error_msg)
    
    def _upload_image(self, image_url: str) -> str:
        """
        Upload image to Twitter media endpoint
        
        Returns:
            str: Media ID
        """
        # Download image
        image_response = requests.get(image_url, timeout=30)
        image_response.raise_for_status()
        
        # Upload to Twitter (v1.1 API for media upload)
        headers = {
            'Authorization': f'Bearer {self.access_token}',
        }
        
        files = {
            'media': image_response.content
        }
        
        response = requests.post(
            'https://upload.twitter.com/1.1/media/upload.json',
            headers=headers,
            files=files,
            timeout=60
        )
        response.raise_for_status()
        
        data = response.json()
        return str(data['media_id'])
    
    def publish_with_video(self, content: str, video_url: str) -> Dict[str, str]:
        """
        Publish tweet with video
        
        Note: Video upload requires chunked upload process
        """
        self.validate_content(content)
        raise PublishError("Twitter video publishing not yet implemented - requires chunked upload")

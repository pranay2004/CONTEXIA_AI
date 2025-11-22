"""
Instagram Publisher
API Documentation: https://developers.facebook.com/docs/instagram-api/guides/content-publishing
"""
import requests
from typing import Dict, List
import time
import logging
from .base import BasePublisher, PublishError

logger = logging.getLogger(__name__)


class InstagramPublisher(BasePublisher):
    """Publisher for Instagram Business posts"""
    
    API_BASE = 'https://graph.facebook.com/v18.0'
    MAX_CONTENT_LENGTH = 2200
    
    def __init__(self, social_account):
        super().__init__(social_account)
        # Get Instagram Business Account ID from metadata
        self.ig_account_id = social_account.account_id
    
    def validate_content(self, content: str) -> bool:
        """Validate Instagram content length"""
        super().validate_content(content)
        if len(content) > self.MAX_CONTENT_LENGTH:
            raise PublishError(f"Instagram captions cannot exceed {self.MAX_CONTENT_LENGTH} characters")
        return True
    
    def publish_text(self, content: str) -> Dict[str, str]:
        """
        Instagram requires images or videos - text-only not supported
        """
        raise PublishError("Instagram requires at least one image or video - text-only posts not supported")
    
    def publish_with_image(self, content: str, image_urls: List[str]) -> Dict[str, str]:
        """
        Publish post with images to Instagram
        
        Instagram publishing is a 2-step process:
        1. Create media container
        2. Publish container
        
        Returns:
            dict: {'post_id': str, 'post_url': str}
        """
        self.validate_content(content)
        self.refresh_token_if_needed()
        
        if len(image_urls) > 10:
            raise PublishError("Instagram supports maximum 10 images per carousel post")
        
        try:
            if len(image_urls) == 1:
                # Single image post
                container_id = self._create_single_image_container(image_urls[0], content)
            else:
                # Carousel post (multiple images)
                container_id = self._create_carousel_container(image_urls, content)
            
            # Step 2: Publish container
            post_id = self._publish_container(container_id)
            post_url = f"https://www.instagram.com/p/{post_id}/"
            
            logger.info(f"Instagram post published successfully: {post_id}")
            
            return {
                'post_id': post_id,
                'post_url': post_url
            }
            
        except Exception as e:
            error_msg = f"Instagram post error: {str(e)}"
            logger.error(error_msg)
            raise PublishError(error_msg)
    
    def _create_single_image_container(self, image_url: str, caption: str) -> str:
        """
        Create single image media container
        
        Returns:
            str: Container ID
        """
        params = {
            'image_url': image_url,
            'caption': caption,
            'access_token': self.access_token,
        }
        
        response = requests.post(
            f'{self.API_BASE}/{self.ig_account_id}/media',
            params=params,
            timeout=30
        )
        response.raise_for_status()
        
        data = response.json()
        return data['id']
    
    def _create_carousel_container(self, image_urls: List[str], caption: str) -> str:
        """
        Create carousel (multiple images) media container
        
        Returns:
            str: Container ID
        """
        # Step 1: Create containers for each image
        item_containers = []
        for image_url in image_urls:
            params = {
                'image_url': image_url,
                'is_carousel_item': 'true',
                'access_token': self.access_token,
            }
            
            response = requests.post(
                f'{self.API_BASE}/{self.ig_account_id}/media',
                params=params,
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            item_containers.append(data['id'])
        
        # Step 2: Create carousel container with all items
        params = {
            'media_type': 'CAROUSEL',
            'caption': caption,
            'children': ','.join(item_containers),
            'access_token': self.access_token,
        }
        
        response = requests.post(
            f'{self.API_BASE}/{self.ig_account_id}/media',
            params=params,
            timeout=30
        )
        response.raise_for_status()
        
        data = response.json()
        return data['id']
    
    def _publish_container(self, container_id: str) -> str:
        """
        Publish media container
        
        Note: Instagram may take a few seconds to process the media
        
        Returns:
            str: Published media ID
        """
        params = {
            'creation_id': container_id,
            'access_token': self.access_token,
        }
        
        # Retry logic for Instagram processing delay
        max_retries = 5
        for attempt in range(max_retries):
            response = requests.post(
                f'{self.API_BASE}/{self.ig_account_id}/media_publish',
                params=params,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return data['id']
            
            # If error is processing-related, wait and retry
            if attempt < max_retries - 1:
                logger.info(f"Instagram processing media, retry {attempt + 1}/{max_retries}")
                time.sleep(5)
            else:
                response.raise_for_status()
        
        raise PublishError("Instagram media publishing timed out")
    
    def publish_with_video(self, content: str, video_url: str) -> Dict[str, str]:
        """
        Publish video to Instagram
        
        Note: Instagram video requirements:
        - MP4 format
        - Max 60 seconds for feed, 15 for stories
        - Aspect ratio 4:5 (vertical) or 1:1 (square)
        """
        self.validate_content(content)
        self.refresh_token_if_needed()
        
        try:
            # Step 1: Create video container
            params = {
                'media_type': 'VIDEO',
                'video_url': video_url,
                'caption': content,
                'access_token': self.access_token,
            }
            
            response = requests.post(
                f'{self.API_BASE}/{self.ig_account_id}/media',
                params=params,
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            container_id = data['id']
            
            # Step 2: Wait for video processing
            time.sleep(10)  # Instagram needs time to process video
            
            # Step 3: Publish container
            post_id = self._publish_container(container_id)
            post_url = f"https://www.instagram.com/p/{post_id}/"
            
            logger.info(f"Instagram video published successfully: {post_id}")
            
            return {
                'post_id': post_id,
                'post_url': post_url
            }
            
        except requests.RequestException as e:
            error_msg = f"Instagram video post error: {str(e)}"
            if hasattr(e, 'response') and e.response is not None:
                error_msg += f" - {e.response.text}"
            logger.error(error_msg)
            raise PublishError(error_msg)

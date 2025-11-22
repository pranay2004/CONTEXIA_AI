"""
LinkedIn Publisher
API Documentation: https://learn.microsoft.com/en-us/linkedin/marketing/integrations/community-management/shares/share-api
"""
import requests
from typing import Dict, List
import logging
from .base import BasePublisher, PublishError

logger = logging.getLogger(__name__)


class LinkedInPublisher(BasePublisher):
    """Publisher for LinkedIn posts"""
    
    API_BASE = 'https://api.linkedin.com/v2'
    MAX_CONTENT_LENGTH = 3000
    
    def __init__(self, social_account):
        super().__init__(social_account)
        self.person_urn = f"urn:li:person:{social_account.account_id}"
    
    def validate_content(self, content: str) -> bool:
        """Validate LinkedIn content length"""
        super().validate_content(content)
        if len(content) > self.MAX_CONTENT_LENGTH:
            raise PublishError(f"LinkedIn posts cannot exceed {self.MAX_CONTENT_LENGTH} characters")
        return True
    
    def publish_text(self, content: str) -> Dict[str, str]:
        """
        Publish text-only post to LinkedIn
        
        Returns:
            dict: {'post_id': str, 'post_url': str}
        """
        self.validate_content(content)
        self.refresh_token_if_needed()
        
        try:
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json',
                'X-Restli-Protocol-Version': '2.0.0',
            }
            
            payload = {
                'author': self.person_urn,
                'lifecycleState': 'PUBLISHED',
                'specificContent': {
                    'com.linkedin.ugc.ShareContent': {
                        'shareCommentary': {
                            'text': content
                        },
                        'shareMediaCategory': 'NONE'
                    }
                },
                'visibility': {
                    'com.linkedin.ugc.MemberNetworkVisibility': 'PUBLIC'
                }
            }
            
            response = requests.post(
                f'{self.API_BASE}/ugcPosts',
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            post_id = response.headers.get('X-RestLi-Id', '')
            post_url = f"https://www.linkedin.com/feed/update/{post_id}/"
            
            logger.info(f"LinkedIn post published successfully: {post_id}")
            
            return {
                'post_id': post_id,
                'post_url': post_url
            }
            
        except requests.RequestException as e:
            error_msg = f"LinkedIn API error: {str(e)}"
            if hasattr(e, 'response') and e.response is not None:
                error_msg += f" - {e.response.text}"
            logger.error(error_msg)
            raise PublishError(error_msg)
    
    def publish_with_image(self, content: str, image_urls: List[str]) -> Dict[str, str]:
        """
        Publish post with images to LinkedIn
        
        Note: LinkedIn requires uploading images first, then creating post
        """
        self.validate_content(content)
        self.refresh_token_if_needed()
        
        if len(image_urls) > 9:
            raise PublishError("LinkedIn supports maximum 9 images per post")
        
        try:
            # Step 1: Register image uploads
            media_assets = []
            for image_url in image_urls:
                asset_id = self._register_and_upload_image(image_url)
                media_assets.append({
                    'status': 'READY',
                    'description': {
                        'text': content
                    },
                    'media': asset_id,
                    'title': {
                        'text': 'Image'
                    }
                })
            
            # Step 2: Create post with images
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json',
                'X-Restli-Protocol-Version': '2.0.0',
            }
            
            payload = {
                'author': self.person_urn,
                'lifecycleState': 'PUBLISHED',
                'specificContent': {
                    'com.linkedin.ugc.ShareContent': {
                        'shareCommentary': {
                            'text': content
                        },
                        'shareMediaCategory': 'IMAGE',
                        'media': media_assets
                    }
                },
                'visibility': {
                    'com.linkedin.ugc.MemberNetworkVisibility': 'PUBLIC'
                }
            }
            
            response = requests.post(
                f'{self.API_BASE}/ugcPosts',
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            post_id = response.headers.get('X-RestLi-Id', '')
            post_url = f"https://www.linkedin.com/feed/update/{post_id}/"
            
            logger.info(f"LinkedIn post with images published: {post_id}")
            
            return {
                'post_id': post_id,
                'post_url': post_url
            }
            
        except Exception as e:
            error_msg = f"LinkedIn image post error: {str(e)}"
            logger.error(error_msg)
            raise PublishError(error_msg)
    
    def _register_and_upload_image(self, image_url: str) -> str:
        """
        Register upload and upload image to LinkedIn
        
        Returns:
            str: Asset URN
        """
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json',
            'X-Restli-Protocol-Version': '2.0.0',
        }
        
        # Register upload
        register_payload = {
            'registerUploadRequest': {
                'recipes': ['urn:li:digitalmediaRecipe:feedshare-image'],
                'owner': self.person_urn,
                'serviceRelationships': [{
                    'relationshipType': 'OWNER',
                    'identifier': 'urn:li:userGeneratedContent'
                }]
            }
        }
        
        response = requests.post(
            f'{self.API_BASE}/assets?action=registerUpload',
            headers=headers,
            json=register_payload,
            timeout=30
        )
        response.raise_for_status()
        
        data = response.json()
        asset_id = data['value']['asset']
        upload_url = data['value']['uploadMechanism']['com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest']['uploadUrl']
        
        # Download image
        image_response = requests.get(image_url, timeout=30)
        image_response.raise_for_status()
        
        # Upload to LinkedIn
        upload_headers = {
            'Authorization': f'Bearer {self.access_token}',
        }
        
        upload_response = requests.put(
            upload_url,
            headers=upload_headers,
            data=image_response.content,
            timeout=60
        )
        upload_response.raise_for_status()
        
        return asset_id
    
    def publish_with_video(self, content: str, video_url: str) -> Dict[str, str]:
        """
        Publish post with video to LinkedIn
        
        Note: Video upload requires multi-step process
        """
        self.validate_content(content)
        raise PublishError("LinkedIn video publishing not yet implemented - requires multi-part upload")

"""
Instagram OAuth 2.0 Integration (via Facebook Graph API)
API Documentation: https://developers.facebook.com/docs/instagram-api/getting-started
Note: Instagram Business accounts require connection through Facebook Pages
"""
import requests
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


class InstagramOAuth:
    """Instagram Graph API OAuth 2.0 Handler"""
    
    # Instagram uses Facebook's OAuth flow
    AUTHORIZATION_URL = 'https://www.facebook.com/v18.0/dialog/oauth'
    TOKEN_URL = 'https://graph.facebook.com/v18.0/oauth/access_token'
    USER_INFO_URL = 'https://graph.facebook.com/v18.0/me'
    EXCHANGE_TOKEN_URL = 'https://graph.facebook.com/v18.0/oauth/access_token'
    
    SCOPES = [
        'instagram_basic',
        'instagram_content_publish',
        'pages_show_list',
        'pages_read_engagement',
    ]
    
    def __init__(self):
        self.app_id = settings.INSTAGRAM_APP_ID
        self.app_secret = settings.INSTAGRAM_APP_SECRET
        self.redirect_uri = settings.INSTAGRAM_REDIRECT_URI
    
    def get_authorization_url(self, state=None):
        """
        Generate Instagram authorization URL (via Facebook)
        
        Args:
            state: CSRF token for security
        
        Returns:
            Authorization URL string
        """
        params = {
            'client_id': self.app_id,
            'redirect_uri': self.redirect_uri,
            'scope': ','.join(self.SCOPES),
            'response_type': 'code',
        }
        
        if state:
            params['state'] = state
        
        query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
        return f"{self.AUTHORIZATION_URL}?{query_string}"
    
    def exchange_code_for_token(self, code):
        """
        Exchange authorization code for access token
        
        Args:
            code: Authorization code from callback
        
        Returns:
            dict: Token data with access_token, expires_in
        """
        try:
            params = {
                'client_id': self.app_id,
                'client_secret': self.app_secret,
                'redirect_uri': self.redirect_uri,
                'code': code,
            }
            
            response = requests.get(self.TOKEN_URL, params=params, timeout=10)
            response.raise_for_status()
            
            token_data = response.json()
            
            # Calculate expiration time
            expires_in = token_data.get('expires_in', 5184000)  # Default 60 days
            token_data['expires_at'] = timezone.now() + timedelta(seconds=expires_in)
            
            logger.info("Instagram short-lived token obtained")
            
            # Exchange for long-lived token (60 days)
            long_lived_token = self._exchange_for_long_lived_token(token_data['access_token'])
            
            return long_lived_token
            
        except requests.RequestException as e:
            logger.error(f"Instagram token exchange failed: {e}")
            raise Exception(f"Failed to exchange code for token: {str(e)}")
    
    def _exchange_for_long_lived_token(self, short_lived_token):
        """
        Exchange short-lived token for long-lived token (60 days)
        
        Args:
            short_lived_token: Short-lived access token
        
        Returns:
            dict: Long-lived token data
        """
        try:
            params = {
                'grant_type': 'ig_exchange_token',
                'client_secret': self.app_secret,
                'access_token': short_lived_token,
            }
            
            response = requests.get(
                'https://graph.instagram.com/access_token',
                params=params,
                timeout=10
            )
            response.raise_for_status()
            
            token_data = response.json()
            expires_in = token_data.get('expires_in', 5184000)
            token_data['expires_at'] = timezone.now() + timedelta(seconds=expires_in)
            
            logger.info("Instagram long-lived token obtained (60 days)")
            return token_data
            
        except requests.RequestException as e:
            logger.error(f"Instagram long-lived token exchange failed: {e}")
            raise Exception(f"Failed to get long-lived token: {str(e)}")
    
    def get_user_pages_with_instagram(self, access_token):
        """
        Fetch Facebook pages connected to Instagram Business accounts
        
        Args:
            access_token: Valid access token
        
        Returns:
            list: List of pages with Instagram business accounts
        """
        try:
            params = {
                'fields': 'id,name,instagram_business_account{id,username,profile_picture_url}',
                'access_token': access_token,
            }
            
            response = requests.get(
                f"{self.USER_INFO_URL}/accounts",
                params=params,
                timeout=10
            )
            response.raise_for_status()
            
            pages_data = response.json()
            
            # Filter only pages with Instagram business accounts
            instagram_pages = [
                page for page in pages_data.get('data', [])
                if 'instagram_business_account' in page
            ]
            
            logger.info(f"Instagram business accounts fetched: {len(instagram_pages)}")
            return instagram_pages
            
        except requests.RequestException as e:
            logger.error(f"Instagram pages fetch failed: {e}")
            raise Exception(f"Failed to fetch Instagram accounts: {str(e)}")
    
    def get_instagram_account_info(self, instagram_account_id, access_token):
        """
        Fetch Instagram business account details
        
        Args:
            instagram_account_id: Instagram business account ID
            access_token: Valid access token
        
        Returns:
            dict: Instagram account data
        """
        try:
            params = {
                'fields': 'id,username,name,profile_picture_url,followers_count,follows_count,media_count',
                'access_token': access_token,
            }
            
            response = requests.get(
                f"https://graph.facebook.com/v18.0/{instagram_account_id}",
                params=params,
                timeout=10
            )
            response.raise_for_status()
            
            account_data = response.json()
            
            logger.info(f"Instagram account info fetched: @{account_data.get('username', 'Unknown')}")
            return account_data
            
        except requests.RequestException as e:
            logger.error(f"Instagram account info fetch failed: {e}")
            raise Exception(f"Failed to fetch account info: {str(e)}")
    
    def refresh_access_token(self, current_token):
        """
        Refresh long-lived Instagram token
        
        Args:
            current_token: Current long-lived token
        
        Returns:
            dict: New token data
        """
        try:
            params = {
                'grant_type': 'ig_refresh_token',
                'access_token': current_token,
            }
            
            response = requests.get(
                'https://graph.instagram.com/refresh_access_token',
                params=params,
                timeout=10
            )
            response.raise_for_status()
            
            token_data = response.json()
            expires_in = token_data.get('expires_in', 5184000)
            token_data['expires_at'] = timezone.now() + timedelta(seconds=expires_in)
            
            logger.info("Instagram token refreshed successfully")
            return token_data
            
        except requests.RequestException as e:
            logger.error(f"Instagram token refresh failed: {e}")
            raise Exception(f"Failed to refresh token: {str(e)}")
    
    def revoke_token(self, access_token):
        """
        Revoke access token (disconnect account)
        
        Args:
            access_token: Token to revoke
        
        Returns:
            bool: Success status
        """
        try:
            params = {
                'access_token': access_token,
            }
            
            response = requests.delete(
                f"{self.USER_INFO_URL}/permissions",
                params=params,
                timeout=10
            )
            response.raise_for_status()
            
            logger.info("Instagram token revoked successfully")
            return True
            
        except requests.RequestException as e:
            logger.error(f"Instagram token revocation failed: {e}")
            return False

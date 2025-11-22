"""
Facebook OAuth 2.0 Integration
API Documentation: https://developers.facebook.com/docs/facebook-login/guides/advanced/manual-flow
"""
import requests
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


class FacebookOAuth:
    """Facebook Graph API OAuth 2.0 Handler"""
    
    AUTHORIZATION_URL = 'https://www.facebook.com/v18.0/dialog/oauth'
    TOKEN_URL = 'https://graph.facebook.com/v18.0/oauth/access_token'
    USER_INFO_URL = 'https://graph.facebook.com/v18.0/me'
    DEBUG_TOKEN_URL = 'https://graph.facebook.com/v18.0/debug_token'
    EXCHANGE_TOKEN_URL = 'https://graph.facebook.com/v18.0/oauth/access_token'
    
    SCOPES = [
        'public_profile',
        'email',
        'pages_show_list',
        'pages_read_engagement',
        'pages_manage_posts',  # Post to pages
        'publish_to_groups',   # Post to groups
    ]
    
    def __init__(self):
        self.app_id = settings.FACEBOOK_APP_ID
        self.app_secret = settings.FACEBOOK_APP_SECRET
        self.redirect_uri = settings.FACEBOOK_REDIRECT_URI
    
    def get_authorization_url(self, state=None):
        """
        Generate Facebook authorization URL
        
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
        Exchange authorization code for short-lived access token
        
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
            
            logger.info("Facebook short-lived token obtained")
            
            # Exchange for long-lived token (60 days)
            long_lived_token = self._exchange_for_long_lived_token(token_data['access_token'])
            
            return long_lived_token
            
        except requests.RequestException as e:
            logger.error(f"Facebook token exchange failed: {e}")
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
                'grant_type': 'fb_exchange_token',
                'client_id': self.app_id,
                'client_secret': self.app_secret,
                'fb_exchange_token': short_lived_token,
            }
            
            response = requests.get(self.EXCHANGE_TOKEN_URL, params=params, timeout=10)
            response.raise_for_status()
            
            token_data = response.json()
            expires_in = token_data.get('expires_in', 5184000)
            token_data['expires_at'] = timezone.now() + timedelta(seconds=expires_in)
            
            logger.info("Facebook long-lived token obtained (60 days)")
            return token_data
            
        except requests.RequestException as e:
            logger.error(f"Facebook long-lived token exchange failed: {e}")
            raise Exception(f"Failed to get long-lived token: {str(e)}")
    
    def get_user_info(self, access_token):
        """
        Fetch user profile information
        
        Args:
            access_token: Valid access token
        
        Returns:
            dict: User profile data
        """
        try:
            params = {
                'fields': 'id,name,email,picture.width(200).height(200)',
                'access_token': access_token,
            }
            
            response = requests.get(self.USER_INFO_URL, params=params, timeout=10)
            response.raise_for_status()
            
            user_data = response.json()
            
            logger.info(f"Facebook user info fetched: {user_data.get('name', 'Unknown')}")
            return user_data
            
        except requests.RequestException as e:
            logger.error(f"Facebook user info fetch failed: {e}")
            raise Exception(f"Failed to fetch user info: {str(e)}")
    
    def get_user_pages(self, access_token):
        """
        Fetch user's Facebook pages
        
        Args:
            access_token: Valid access token
        
        Returns:
            list: List of page data
        """
        try:
            params = {
                'fields': 'id,name,access_token,picture.width(200).height(200),category,fan_count',
                'access_token': access_token,
            }
            
            response = requests.get(
                f"{self.USER_INFO_URL}/accounts",
                params=params,
                timeout=10
            )
            response.raise_for_status()
            
            pages_data = response.json()
            
            logger.info(f"Facebook pages fetched: {len(pages_data.get('data', []))} pages")
            return pages_data.get('data', [])
            
        except requests.RequestException as e:
            logger.error(f"Facebook pages fetch failed: {e}")
            raise Exception(f"Failed to fetch pages: {str(e)}")
    
    def debug_token(self, access_token):
        """
        Debug token to check validity and expiration
        
        Args:
            access_token: Token to debug
        
        Returns:
            dict: Token debug information
        """
        try:
            params = {
                'input_token': access_token,
                'access_token': f"{self.app_id}|{self.app_secret}",
            }
            
            response = requests.get(self.DEBUG_TOKEN_URL, params=params, timeout=10)
            response.raise_for_status()
            
            debug_data = response.json()
            
            logger.info("Facebook token debugged successfully")
            return debug_data.get('data', {})
            
        except requests.RequestException as e:
            logger.error(f"Facebook token debug failed: {e}")
            raise Exception(f"Failed to debug token: {str(e)}")
    
    def refresh_access_token(self, current_token):
        """
        Refresh long-lived token (extend validity)
        Facebook long-lived tokens are valid for 60 days and can be refreshed
        
        Args:
            current_token: Current long-lived token
        
        Returns:
            dict: New token data
        """
        try:
            # Check if token is still valid
            debug_info = self.debug_token(current_token)
            
            if not debug_info.get('is_valid'):
                raise Exception("Token is no longer valid")
            
            # Exchange for new long-lived token
            return self._exchange_for_long_lived_token(current_token)
            
        except Exception as e:
            logger.error(f"Facebook token refresh failed: {e}")
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
            
            logger.info("Facebook token revoked successfully")
            return True
            
        except requests.RequestException as e:
            logger.error(f"Facebook token revocation failed: {e}")
            return False

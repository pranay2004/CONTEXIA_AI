"""
LinkedIn OAuth 2.0 Integration
API Documentation: https://learn.microsoft.com/en-us/linkedin/shared/authentication/authentication
"""
import requests
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from urllib.parse import urlencode
import logging

logger = logging.getLogger(__name__)


class LinkedInOAuth:
    """LinkedIn OAuth 2.0 Handler"""
    
    AUTHORIZATION_URL = 'https://www.linkedin.com/oauth/v2/authorization'
    TOKEN_URL = 'https://www.linkedin.com/oauth/v2/accessToken'
    USER_INFO_URL = 'https://api.linkedin.com/v2/userinfo'
    
    SCOPES = [
        'profile',
        'openid',
        'email',
        'w_member_social',  # Post on behalf of user
    ]
    
    def __init__(self):
        self.client_id = settings.LINKEDIN_CLIENT_ID
        self.client_secret = settings.LINKEDIN_CLIENT_SECRET
        self.redirect_uri = settings.LINKEDIN_REDIRECT_URI
    
    def get_authorization_url(self, state=None):
        """
        Generate LinkedIn authorization URL
        
        Args:
            state: CSRF token for security
        
        Returns:
            Authorization URL string
        """
        params = {
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'scope': ' '.join(self.SCOPES),
        }
        
        if state:
            params['state'] = state
        
        # Use urlencode to properly encode the parameters
        query_string = urlencode(params)
        return f"{self.AUTHORIZATION_URL}?{query_string}"
    
    def exchange_code_for_token(self, code):
        """
        Exchange authorization code for access token
        
        Args:
            code: Authorization code from callback
        
        Returns:
            dict: Token data with access_token, expires_in, etc.
        """
        try:
            # LinkedIn requires form-encoded data, not JSON
            data = {
                'grant_type': 'authorization_code',
                'code': code,
                'redirect_uri': self.redirect_uri,
                'client_id': self.client_id,
                'client_secret': self.client_secret,
            }
            
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
            }
            
            logger.info(f"LinkedIn token exchange request - redirect_uri: {self.redirect_uri}")
            logger.info(f"LinkedIn token exchange request - client_id: {self.client_id}")
            
            response = requests.post(self.TOKEN_URL, data=data, headers=headers, timeout=10)
            
            # Log the response for debugging
            logger.info(f"LinkedIn token exchange status: {response.status_code}")
            if response.status_code != 200:
                logger.error(f"LinkedIn token error response: {response.text}")
                # Return more detailed error
                raise Exception(f"LinkedIn API error ({response.status_code}): {response.text}")
            
            response.raise_for_status()
            
            token_data = response.json()
            
            # Calculate expiration time
            expires_in = token_data.get('expires_in', 5184000)  # Default 60 days
            token_data['expires_at'] = timezone.now() + timedelta(seconds=expires_in)
            
            logger.info("LinkedIn token exchanged successfully")
            return token_data
            
        except requests.RequestException as e:
            logger.error(f"LinkedIn token exchange failed: {e}")
            raise Exception(f"Failed to exchange code for token: {str(e)}")
    
    def get_user_info(self, access_token):
        """
        Fetch user profile information
        
        Args:
            access_token: Valid access token
        
        Returns:
            dict: User profile data
        """
        try:
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json',
            }
            
            response = requests.get(self.USER_INFO_URL, headers=headers, timeout=10)
            response.raise_for_status()
            
            user_data = response.json()
            
            logger.info(f"LinkedIn user info fetched: {user_data.get('name', 'Unknown')}")
            return user_data
            
        except requests.RequestException as e:
            logger.error(f"LinkedIn user info fetch failed: {e}")
            raise Exception(f"Failed to fetch user info: {str(e)}")
    
    def refresh_access_token(self, refresh_token):
        """
        Refresh expired access token
        
        Args:
            refresh_token: Valid refresh token
        
        Returns:
            dict: New token data
        """
        try:
            data = {
                'grant_type': 'refresh_token',
                'refresh_token': refresh_token,
                'client_id': self.client_id,
                'client_secret': self.client_secret,
            }
            
            response = requests.post(self.TOKEN_URL, data=data, timeout=10)
            response.raise_for_status()
            
            token_data = response.json()
            expires_in = token_data.get('expires_in', 5184000)
            token_data['expires_at'] = timezone.now() + timedelta(seconds=expires_in)
            
            logger.info("LinkedIn token refreshed successfully")
            return token_data
            
        except requests.RequestException as e:
            logger.error(f"LinkedIn token refresh failed: {e}")
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
            # LinkedIn doesn't have a dedicated revoke endpoint
            # Token will expire naturally
            logger.info("LinkedIn token marked for expiration")
            return True
            
        except Exception as e:
            logger.error(f"LinkedIn token revocation failed: {e}")
            return False

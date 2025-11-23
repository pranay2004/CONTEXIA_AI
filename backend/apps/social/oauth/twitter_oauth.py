"""
Twitter/X OAuth 2.0 Integration
API Documentation: https://developer.twitter.com/en/docs/authentication/oauth-2-0
"""
import requests
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from urllib.parse import urlencode
import logging
import base64

logger = logging.getLogger(__name__)
class TwitterOAuth:
    """Twitter/X OAuth 2.0 Handler with PKCE"""
    
    AUTHORIZATION_URL = 'https://twitter.com/i/oauth2/authorize'
    TOKEN_URL = 'https://api.twitter.com/2/oauth2/token'
    USER_INFO_URL = 'https://api.twitter.com/2/users/me'
    REVOKE_URL = 'https://api.twitter.com/2/oauth2/revoke'
    
    SCOPES = [
        'tweet.read',
        'tweet.write',
        'users.read',
        'offline.access',  # For refresh tokens
    ]
    
    def __init__(self):
        self.client_id = settings.TWITTER_CLIENT_ID
        self.client_secret = settings.TWITTER_CLIENT_SECRET
        self.redirect_uri = settings.TWITTER_REDIRECT_URI
    
    def get_authorization_url(self, code_challenge, state=None):
        """
        Generate Twitter authorization URL with PKCE
        
        Args:
            code_challenge: PKCE code challenge (SHA256 hash of code_verifier)
            state: CSRF token for security
        
        Returns:
            Authorization URL string
        """
        params = {
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'scope': ' '.join(self.SCOPES),
            'code_challenge': code_challenge,
            'code_challenge_method': 'S256',
        }
        
        if state:
            params['state'] = state
        
        # Use urlencode to properly encode the parameters
        query_string = urlencode(params)
        return f"{self.AUTHORIZATION_URL}?{query_string}"
    
    def exchange_code_for_token(self, code, code_verifier):
        """
        Exchange authorization code for access token with PKCE
        
        Args:
            code: Authorization code from callback
            code_verifier: PKCE code verifier (plaintext)
        
        Returns:
            dict: Token data with access_token, refresh_token, expires_in
        """
        try:
            # Twitter requires Basic Auth
            credentials = base64.b64encode(
                f"{self.client_id}:{self.client_secret}".encode()
            ).decode()
            
            headers = {
                'Authorization': f'Basic {credentials}',
                'Content-Type': 'application/x-www-form-urlencoded',
            }
            
            data = {
                'grant_type': 'authorization_code',
                'code': code,
                'redirect_uri': self.redirect_uri,
                'code_verifier': code_verifier,
            }
            
            response = requests.post(self.TOKEN_URL, headers=headers, data=data, timeout=10)
            response.raise_for_status()
            
            token_data = response.json()
            
            # Calculate expiration time
            expires_in = token_data.get('expires_in', 7200)  # Default 2 hours
            token_data['expires_at'] = timezone.now() + timedelta(seconds=expires_in)
            
            logger.info("Twitter token exchanged successfully")
            return token_data
            
        except requests.RequestException as e:
            logger.error(f"Twitter token exchange failed: {e}")
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
            }
            
            params = {
                'user.fields': 'id,name,username,profile_image_url,description,public_metrics',
            }
            
            response = requests.get(
                self.USER_INFO_URL,
                headers=headers,
                params=params,
                timeout=10
            )
            response.raise_for_status()
            
            user_data = response.json()
            
            logger.info(f"Twitter user info fetched: @{user_data.get('data', {}).get('username', 'Unknown')}")
            return user_data
            
        except requests.RequestException as e:
            logger.error(f"Twitter user info fetch failed: {e}")
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
            credentials = base64.b64encode(
                f"{self.client_id}:{self.client_secret}".encode()
            ).decode()
            
            headers = {
                'Authorization': f'Basic {credentials}',
                'Content-Type': 'application/x-www-form-urlencoded',
            }
            
            data = {
                'grant_type': 'refresh_token',
                'refresh_token': refresh_token,
            }
            
            response = requests.post(self.TOKEN_URL, headers=headers, data=data, timeout=10)
            response.raise_for_status()
            
            token_data = response.json()
            expires_in = token_data.get('expires_in', 7200)
            token_data['expires_at'] = timezone.now() + timedelta(seconds=expires_in)
            
            logger.info("Twitter token refreshed successfully")
            return token_data
            
        except requests.RequestException as e:
            logger.error(f"Twitter token refresh failed: {e}")
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
            credentials = base64.b64encode(
                f"{self.client_id}:{self.client_secret}".encode()
            ).decode()
            
            headers = {
                'Authorization': f'Basic {credentials}',
                'Content-Type': 'application/x-www-form-urlencoded',
            }
            
            data = {
                'token': access_token,
                'token_type_hint': 'access_token',
            }
            
            response = requests.post(self.REVOKE_URL, headers=headers, data=data, timeout=10)
            response.raise_for_status()
            
            logger.info("Twitter token revoked successfully")
            return True
            
        except requests.RequestException as e:
            logger.error(f"Twitter token revocation failed: {e}")
            return False

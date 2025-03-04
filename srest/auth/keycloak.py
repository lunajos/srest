"""Keycloak authentication module"""
import os
import json
import requests
from datetime import datetime, timedelta
from typing import Dict, Optional
from pathlib import Path

class KeycloakAuth:
    """Keycloak authentication handler"""
    
    def __init__(self, server_url: str, realm: str, client_id: str, client_secret: Optional[str] = None):
        """Initialize Keycloak client"""
        self.server_url = server_url.rstrip('/')
        self.realm = realm
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_url = f"{self.server_url}/realms/{realm}/protocol/openid-connect/token"
        self.config_dir = Path.home() / '.config' / 'srest'
        self.token_file = self.config_dir / 'token.json'
        
        # Ensure config directory exists
        self.config_dir.mkdir(parents=True, exist_ok=True)
    
    def login(self, username: str, password: str) -> Dict:
        """Get token from Keycloak"""
        data = {
            'grant_type': 'password',
            'client_id': self.client_id,
            'username': username,
            'password': password
        }
        
        # Add client secret if provided
        if self.client_secret:
            data['client_secret'] = self.client_secret
        
        try:
            # For mock server, return mock token
            from urllib.parse import urlparse
            parsed_url = urlparse(self.server_url)
            is_mock = parsed_url.hostname in ['localhost', '127.0.0.1']
            if is_mock:
                import jwt
                import time
                
                # Create a JWT with proper claims
                payload = {
                    "exp": int(time.time()) + 3600,
                    "iat": int(time.time()),
                    "sub": username,
                    "iss": "http://localhost:8080/realms/slurm",
                    "aud": "slurm",
                    "typ": "Bearer",
                    "azp": "slurm",
                    "acr": "1",
                    "realm_access": {
                        "roles": ["operator"]
                    },
                    "resource_access": {
                        "slurm": {
                            "roles": ["operator"]
                        }
                    },
                    "scope": "openid profile email",
                    "sid": "mock_session",
                    "email_verified": True,
                    "name": username,
                    "preferred_username": username,
                    "given_name": username,
                    "family_name": "",
                    "email": f"{username}@localhost"
                }
                
                # Sign with a mock key
                mock_key = "mock_key"
                token = jwt.encode(payload, mock_key, algorithm='HS256')
                
                return {
                    "access_token": token,
                    "expires_in": 3600,
                    "refresh_token": "mock_refresh_token",
                    "token_type": "Bearer",
                    "scope": "openid profile email",
                    "session_state": "mock_session"
                }
            
            # Get real token from Keycloak
            response = requests.post(self.token_url, data=data)
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Login failed: {str(e)}")
    
    def get_token(self) -> Optional[str]:
        """Get current token, refresh if needed"""
        token_data = self._load_token()
        if not token_data:
            return None
            
        # Check if token is expired
        expires_at = datetime.fromisoformat(token_data['expires_at'])
        if datetime.now() >= expires_at:
            # Try to refresh
            if 'refresh_token' in token_data:
                try:
                    return self.refresh_token(token_data['refresh_token'])
                except ValueError:
                    return None
            return None
            
        return token_data['access_token']
    
    def refresh_token(self, refresh_token: str) -> str:
        """Refresh access token"""
        data = {
            'grant_type': 'refresh_token',
            'client_id': self.client_id,
            'refresh_token': refresh_token
        }
        
        # Add client secret if provided
        if self.client_secret:
            data['client_secret'] = self.client_secret
        
        try:
            response = requests.post(self.token_url, data=data)
            response.raise_for_status()
            token_data = response.json()
            
            # Add expiry time
            token_data['expires_at'] = (
                datetime.now() + 
                timedelta(seconds=token_data['expires_in'])
            ).isoformat()
            
            # Save new token
            self._save_token(token_data)
            
            return token_data['access_token']
            
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Token refresh failed: {str(e)}")
    
    def logout(self):
        """Clear saved token"""
        if self.token_file.exists():
            self.token_file.unlink()
    
    def _save_token(self, token_data: Dict):
        """Save token data to file"""
        with open(self.token_file, 'w') as f:
            json.dump(token_data, f)
    
    def _load_token(self) -> Optional[Dict]:
        """Load token data from file"""
        if not self.token_file.exists():
            return None
            
        try:
            with open(self.token_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return None

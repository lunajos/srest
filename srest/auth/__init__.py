"""Authentication module"""
import os
import json
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import jwt
from ..config import Config

TOKEN_DIR = os.path.expanduser("~/.config/srest")
TOKEN_FILE = os.path.join(TOKEN_DIR, "token.json")

def login(username: str, password: str) -> Dict[str, Any]:
    """Login and save token. Returns token information dictionary."""
    config = Config()
    
    # Get auth server URL
    server_url = config.get('auth.server_url')
    if not server_url:
        raise ValueError("Auth server URL not configured. Run 'srest config set auth.server_url <url>'")
    
    # Check if we're in mock mode (only localhost or 127.0.0.1)
    from urllib.parse import urlparse
    parsed_url = urlparse(server_url)
    is_mock = parsed_url.hostname in ['localhost', '127.0.0.1']
    if is_mock:
        # In mock mode, any password works
        token = {
            "access_token": "mock_token",
            "expires_in": 3600,
            "refresh_token": "mock_refresh_token",
            "token_type": "Bearer",
            "scope": "openid profile email",
            "session_state": "mock_session",
            "expires_at": (datetime.now() + timedelta(seconds=3600)).isoformat()
        }
    else:
        # Get real token from Keycloak
        from .keycloak import KeycloakAuth
        
        # Get client secret from config
        client_secret = config.get('auth.client_secret')
        if not client_secret:
            raise ValueError("Keycloak client secret not configured. Run 'srest config set auth.client_secret <secret>'")
            
        auth = KeycloakAuth(
            server_url=server_url,
            realm=config.get('auth.realm', 'slurm-realm'),
            client_id=config.get('auth.client_id', 'slurm'),
            client_secret=client_secret
        )
        token = auth.login(username, password)
        token['expires_at'] = (datetime.now() + timedelta(seconds=token['expires_in'])).isoformat()
    
    # Save token
    os.makedirs(TOKEN_DIR, exist_ok=True)
    with open(TOKEN_FILE, 'w') as f:
        json.dump(token, f, indent=2)
        
    return {
        "token": token['access_token'],
        "expires": token['expires_at'],
        "claims": jwt.decode(token['access_token'], options={"verify_signature": False})
    }

def logout():
    """Logout and clear token"""
    if os.path.exists(TOKEN_FILE):
        os.remove(TOKEN_FILE)

def get_token_info() -> Dict[str, Any]:
    """Get current token info"""
    if not os.path.exists(TOKEN_FILE):
        raise ValueError("Not logged in. Run 'srest auth login' first")
    
    with open(TOKEN_FILE, 'r') as f:
        token = json.load(f)
    
    # Parse JWT claims if not already decoded
    try:
        claims = jwt.decode(token['access_token'], options={"verify_signature": False})
    except jwt.InvalidTokenError:
        claims = {}
    
    return {
        "token": token['access_token'],
        "expires": token.get('expires_at', token.get('expires_in')),
        "claims": claims
    }

__all__ = ['login', 'logout', 'get_token_info']

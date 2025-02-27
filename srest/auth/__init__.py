"""Authentication module"""
import os
import json
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import jwt
from ..config import Config

TOKEN_DIR = os.path.expanduser("~/.config/srest")
TOKEN_FILE = os.path.join(TOKEN_DIR, "token.json")

def login(username: str, password: str):
    """Login and save token"""
    config = Config()
    
    # Get auth server URL
    server_url = config.get('auth.server_url')
    if not server_url:
        raise ValueError("Auth server URL not configured. Run 'srest config set auth.server_url <url>'")
    
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
    
    # Save token
    os.makedirs(TOKEN_DIR, exist_ok=True)
    with open(TOKEN_FILE, 'w') as f:
        json.dump(token, f, indent=2)

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
    
    # Parse JWT claims
    try:
        claims = jwt.decode(token['access_token'], options={"verify_signature": False})
    except jwt.InvalidTokenError:
        claims = {}
    
    return {
        "token": token['access_token'],
        "expires": token['expires_in'],
        "claims": claims
    }

__all__ = ['login', 'logout', 'get_token_info']

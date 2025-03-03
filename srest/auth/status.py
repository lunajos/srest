"""Auth status management for srest."""
import os
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict

class AuthStatus:
    """Manages authentication status and token information."""
    
    def __init__(self):
        self.status_file = Path.home() / ".config" / "srest" / "auth_status.json"
        self._ensure_status_file()
        
    def _ensure_status_file(self):
        """Ensure the status file exists."""
        self.status_file.parent.mkdir(parents=True, exist_ok=True)
        if not self.status_file.exists():
            self._save_status({})
            
    def _save_status(self, status: Dict):
        """Save status information to file."""
        with open(self.status_file, 'w') as f:
            json.dump(status, f)
            
    def _load_status(self) -> Dict:
        """Load status information from file."""
        try:
            with open(self.status_file) as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}
            
    def update_login(self, token: str, expires_at: datetime):
        """Update login status with new token information."""
        status = self._load_status()
        status.update({
            'token': token,
            'expires_at': expires_at.isoformat(),
            'last_login': datetime.now().isoformat()
        })
        self._save_status(status)
        
    def clear_login(self):
        """Clear login status."""
        self._save_status({})
        
    def is_logged_in(self) -> bool:
        """Check if user is currently logged in with valid token."""
        status = self._load_status()
        if not status:
            return False
            
        try:
            expires_at = datetime.fromisoformat(status['expires_at'])
            return datetime.now() < expires_at
        except (KeyError, ValueError):
            return False
            
    def get_token(self) -> Optional[str]:
        """Get current auth token if logged in."""
        if not self.is_logged_in():
            return None
        return self._load_status().get('token')

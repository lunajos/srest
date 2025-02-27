"""Configuration management"""
import os
import json
from typing import Dict, Any, Optional

CONFIG_DIR = os.path.expanduser("~/.config/srest")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

class Config:
    """Configuration manager"""
    
    def __init__(self):
        """Initialize configuration"""
        self._config = {}
        self._load()
    
    def _load(self):
        """Load configuration from file"""
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    self._config = json.load(f)
            except json.JSONDecodeError:
                self._config = {}
    
    def save(self):
        """Save configuration to file"""
        os.makedirs(CONFIG_DIR, exist_ok=True)
        with open(CONFIG_FILE, 'w') as f:
            json.dump(self._config, f, indent=2)
    
    def set(self, key: str, value: str):
        """Set configuration value"""
        # Handle nested keys (e.g. 'slurm.url')
        parts = key.split('.')
        current = self._config
        
        # Create nested dictionaries
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]
        
        # Set the value
        current[parts[-1]] = value
        
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        # Handle nested keys (e.g. 'slurm.url')
        parts = key.split('.')
        current = self._config
        
        # Navigate through nested dictionaries
        for part in parts:
            if not isinstance(current, dict):
                return default
            if part not in current:
                return default
            current = current[part]
        
        return current
    
    def delete(self, key: str):
        """Delete configuration value"""
        # Handle nested keys (e.g. 'slurm.url')
        parts = key.split('.')
        current = self._config
        
        # Navigate through nested dictionaries
        for part in parts[:-1]:
            if not isinstance(current, dict) or part not in current:
                return
            current = current[part]
        
        # Delete the key if it exists
        if isinstance(current, dict) and parts[-1] in current:
            del current[parts[-1]]
    
    def get_all(self) -> Dict[str, Any]:
        """Get all configuration values"""
        return self._config.copy()

__all__ = ['Config']

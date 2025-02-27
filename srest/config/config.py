"""Configuration management"""
import os
import yaml
from pathlib import Path
from typing import Dict, Optional

class Config:
    """Configuration manager"""
    
    def __init__(self):
        """Initialize configuration"""
        self.config_dir = Path.home() / '.config' / 'srest'
        self.config_file = self.config_dir / 'config.yaml'
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Default configuration
        self.defaults = {
            'slurm': {
                'url': os.environ.get('SLURM_REST_URL', ''),
            },
            'auth': {
                'type': 'keycloak',
                'server_url': '',
                'realm': 'slurm',
                'client_id': 'slurm-rest',
            }
        }
        
        # Load configuration
        self.config = self._load_config()
    
    def get(self, key: str, default: Optional[str] = None) -> str:
        """Get configuration value"""
        # Check environment first
        env_key = f"SLURM_REST_{key.upper()}"
        if env_key in os.environ:
            return os.environ[env_key]
            
        # Then check config file
        parts = key.split('.')
        value = self.config
        for part in parts:
            if not isinstance(value, dict) or part not in value:
                return default or self.get_default(key)
            value = value[part]
        return value
    
    def set(self, key: str, value: str):
        """Set configuration value"""
        parts = key.split('.')
        config = self.config
        for part in parts[:-1]:
            if part not in config:
                config[part] = {}
            config = config[part]
        config[parts[-1]] = value
        self._save_config()
    
    def get_default(self, key: str) -> str:
        """Get default configuration value"""
        parts = key.split('.')
        value = self.defaults
        for part in parts:
            if not isinstance(value, dict) or part not in value:
                return ''
            value = value[part]
        return value
    
    def _load_config(self) -> Dict:
        """Load configuration from file"""
        if not self.config_file.exists():
            return self.defaults.copy()
            
        try:
            with open(self.config_file, 'r') as f:
                config = yaml.safe_load(f) or {}
                
            # Merge with defaults
            merged = self.defaults.copy()
            self._merge_dicts(merged, config)
            return merged
            
        except Exception:
            return self.defaults.copy()
    
    def _save_config(self):
        """Save configuration to file"""
        with open(self.config_file, 'w') as f:
            yaml.dump(self.config, f)
    
    def _merge_dicts(self, dict1: Dict, dict2: Dict):
        """Recursively merge dictionaries"""
        for key in dict2:
            if key in dict1 and isinstance(dict1[key], dict) and isinstance(dict2[key], dict):
                self._merge_dicts(dict1[key], dict2[key])
            else:
                dict1[key] = dict2[key]

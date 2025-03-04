"""Base client for Slurm REST API v3"""

import os
from typing import Optional, Dict, Any, Union
from swagger_client import Configuration, ApiClient
from swagger_client.api import SlurmApi

class BaseClient:
    """Base client class wrapping swagger-generated client"""
    
    def __init__(
        self,
        url: Optional[str] = None,
        token: Optional[str] = None,
        username: Optional[str] = None,
        ssl_verify: bool = True,
        debug: bool = False
    ):
        """Initialize base client
        
        Args:
            url: Slurm REST API URL (default: SREST_URL env var)
            token: Authentication token (default: SREST_TOKEN env var)
            username: Username for token auth (default: SREST_USER env var)
            ssl_verify: Whether to verify SSL certificates
            debug: Enable debug logging
        """
        self.url = url or os.environ.get('SREST_URL')
        if not self.url:
            raise ValueError("URL must be provided or SREST_URL env var set")
            
        self.token = token or os.environ.get('SREST_TOKEN')
        self.username = username or os.environ.get('SREST_USER')
        
        if not self.token:
            raise ValueError("Token must be provided or SREST_TOKEN env var set")
            
        # Configure swagger client
        config = Configuration()
        config.host = self.url
        config.verify_ssl = ssl_verify
        config.debug = debug
        
        # Create API client
        self.api_client = ApiClient(config)
        
        # Add auth headers
        if self.username:
            # User token auth
            self.api_client.default_headers['X-SLURM-USER-NAME'] = self.username
            self.api_client.default_headers['X-SLURM-USER-TOKEN'] = self.token
        elif self.token.startswith('ey'):
            # JWT auth
            self.api_client.default_headers['Authorization'] = f'Bearer {self.token}'
        else:
            # Token-only auth
            self.api_client.default_headers['X-SLURM-USER-TOKEN'] = self.token
            
        # Create Slurm API instance
        self.slurm_api = SlurmApi(self.api_client)

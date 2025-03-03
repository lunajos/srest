"""License client"""
from typing import Dict, Any, Optional, Union, List
from .base import BaseClient
from .models import SlurmResponse
from dataclasses import dataclass

@dataclass
class LicenseResponse(SlurmResponse):
    """Response for license queries"""
    licenses: List[Dict[str, Any]] = None
    
    def __init__(self, **data):
        # Initialize parent
        super().__init__(**data)
        
        # Set licenses
        self.licenses = data.get('licenses', [])

class LicenseClient(BaseClient):
    """Client for license operations"""
    
    def get_licenses(self, return_curl: bool = False) -> Union[LicenseResponse, str]:
        """Get license information"""
        return self._make_request(
            method='GET',
            endpoint='/licenses',
            response_type=LicenseResponse,
            return_curl=return_curl
        )

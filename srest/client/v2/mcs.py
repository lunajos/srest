"""MCS client"""
from typing import Dict, Any, Optional, Union, List
from .base import BaseClient
from .models import SlurmResponse
from dataclasses import dataclass

@dataclass
class McsResponse(SlurmResponse):
    """Response for MCS queries"""
    mcs_labels: List[Dict[str, Any]] = None
    
    def __init__(self, **data):
        # Initialize parent
        super().__init__(**data)
        
        # Set MCS labels
        self.mcs_labels = data.get('mcs_labels', [])

class McsClient(BaseClient):
    """Client for MCS operations"""
    
    def get_mcs_labels(self, type: Optional[str] = None, return_curl: bool = False) -> Union[McsResponse, str]:
        """Get MCS labels"""
        params = {}
        if type:
            params['type'] = type
        return self._make_request(
            method='GET',
            endpoint='/mcs',  # Version prefix is added by BaseClient
            response_type=McsResponse,
            params=params,
            return_curl=return_curl
        )

    def get_mcs_label(self, label: str, return_curl: bool = False) -> Union[McsResponse, str]:
        """Get MCS label details"""
        return self._make_request(
            method='GET',
            endpoint=f'/mcs/{label}',  # Version prefix is added by BaseClient
            response_type=McsResponse,
            return_curl=return_curl
        )

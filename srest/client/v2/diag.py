"""Diagnostic client"""
from typing import Dict, Any, Optional, Union, List
from .base import BaseClient
from .models import SlurmResponse
from dataclasses import dataclass

@dataclass
class DiagInfo:
    """Diagnostic information"""
    def __init__(self, **data):
        # Store all fields dynamically
        for key, value in data.items():
            # Convert time objects to their numeric values
            if isinstance(value, dict) and 'set' in value and 'number' in value:
                value = value.get('number')
            # Store the value
            setattr(self, key, value)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert diagnostic info to dictionary"""
        return {key: value for key, value in self.__dict__.items() if value is not None}

@dataclass
class MetaInfo:
    """Metadata information"""
    plugin: Dict[str, str] = None
    client: Dict[str, str] = None
    command: List[str] = None
    slurm: Dict[str, Any] = None
    errors: List[str] = None
    warnings: List[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata info to dictionary"""
        result = {}
        for field in self.__dataclass_fields__:
            value = getattr(self, field)
            if value is not None:
                result[field] = value
        return result

@dataclass
class DiagResponse(SlurmResponse):
    """Response for diagnostic queries"""
    statistics: DiagInfo = None  # Make statistics optional to match parent class pattern
    meta: MetaInfo = None  # Add metadata field
    
    def __init__(self, **data):
        # Initialize parent
        super().__init__(**data)
        
        # Extract statistics from the response
        stats_data = None
        if 'statistics' in data:
            stats_data = data['statistics']
        elif 'diag' in data:
            stats_data = data['diag']
        
        # Convert statistics if present
        if stats_data:
            # Handle all fields dynamically
            stats_dict = {}
            for key, value in stats_data.items():
                if isinstance(value, dict) and 'set' in value and 'number' in value:
                    # Handle time fields that come as objects
                    stats_dict[key] = value.get('number')
                else:
                    stats_dict[key] = value
            self.statistics = DiagInfo(**stats_dict)
        
        # Extract metadata from the response
        meta_data = data.get('meta')
        if meta_data:
            self.meta = MetaInfo(**meta_data)

@dataclass
class PingResponse(SlurmResponse):
    """Response for ping queries"""
    ping: Dict[str, Any] = None  # Make ping optional to match parent class pattern

class DiagClient(BaseClient):
    """Client for diagnostic operations"""
    
    def get_diagnostics(self, return_curl: bool = False) -> Union[DiagResponse, str]:
        """Get diagnostic information"""
        return self._make_request(
            method='GET',
            endpoint='diag',
            response_type=DiagResponse,
            return_curl=return_curl
        )
    
    def ping(self, return_curl: bool = False) -> Union[PingResponse, str]:
        """Ping the Slurm controller"""
        return self._make_request(
            method='GET',
            endpoint='ping',
            response_type=PingResponse,
            return_curl=return_curl
        )

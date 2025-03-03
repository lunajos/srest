"""Diagnostic client"""
from typing import Dict, Any, Optional, Union, List
from .base import BaseClient
from .models import SlurmResponse
from dataclasses import dataclass

@dataclass
class DiagInfo:
    """Diagnostic information"""
    controller: str
    version: str
    rpc_version: int
    last_update: int
    up_time: int
    server_thread_count: int
    agent_queue_size: int
    dbd_agent_queue_size: int
    jobs_submitted: int
    jobs_started: int
    jobs_completed: int
    jobs_canceled: int
    jobs_failed: int

@dataclass
class DiagResponse(SlurmResponse):
    """Response for diagnostic queries"""
    statistics: DiagInfo = None  # Make statistics optional to match parent class pattern
    
    def __init__(self, **data):
        # Extract statistics before passing to parent
        stats_data = data.pop('statistics', None)
        super().__init__(**data)
        # Convert statistics if present
        if stats_data:
            self.statistics = DiagInfo(**stats_data)

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
            endpoint='/diag',
            response_type=DiagResponse,
            return_curl=return_curl
        )
    
    def ping(self, return_curl: bool = False) -> Union[PingResponse, str]:
        """Ping the Slurm controller"""
        return self._make_request(
            method='GET',
            endpoint='/ping',
            response_type=PingResponse,
            return_curl=return_curl
        )

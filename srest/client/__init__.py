"""Slurm REST API client based on OpenAPI 3.0.3 specification"""
from typing import Optional, Dict, Any
from dataclasses import dataclass

from .v3.jobs import JobClient
from .v3.nodes import NodeClient
from .v3.partitions import PartitionClient
from swagger_client.models import (
    V0036JobSubmissionResponse,
    V0036JobsResponse,
    V0036NodesResponse,
    V0036PartitionsResponse,
    V0036Diag
)

@dataclass
class SlurmRESTClient:
    """Unified client for CLI compatibility"""
    job: JobClient
    node: NodeClient
    partition: PartitionClient
    
    def submit_job(self, script_content: str, params: Dict[str, Any], return_curl: bool = False) -> Dict[str, Any]:
        """Submit a job to Slurm"""
        response = self.job.submit_job(
            script=script_content,
            params=params,
            return_curl=return_curl
        )
        if isinstance(response, str):
            return {'curl_command': response}
        return response.to_dict()
    
    def list_jobs(self, user: Optional[str] = None, return_curl: bool = False) -> Dict[str, Any]:
        """List jobs"""
        response = self.job.get_jobs(user=user, return_curl=return_curl)
        if isinstance(response, str):
            return {'curl_command': response}
        return response.to_dict()
    
    def get_job(self, job_id: str, return_curl: bool = False) -> Dict[str, Any]:
        """Get job details"""
        response = self.job.get_job(job_id=job_id, return_curl=return_curl)
        if isinstance(response, str):
            return {'curl_command': response}
        return response.to_dict()
    
    def list_nodes(self, **filters) -> Dict[str, Any]:
        """List compute nodes"""
        response = self.node.get_nodes(return_curl=False, **filters)
        if isinstance(response, str):
            return {'curl_command': response}
        return response.to_dict()
        

    
    def list_partitions(self, **filters) -> Dict[str, Any]:
        """List partitions"""
        response = self.partition.get_partitions(return_curl=False)
        if isinstance(response, str):
            return {'curl_command': response}
        return response.to_dict()
    
    def cancel_job(self, job_id: str, return_curl: bool = False) -> None:
        """Cancel a job"""
        self.job.cancel_job(job_id=job_id, return_curl=return_curl)

def get_client() -> SlurmRESTClient:
    """Get configured client instance with version checking."""
    from ..config import Config
    from ..auth.status import AuthStatus
    
    config = Config()
    auth_status = AuthStatus()
    
    # Check login status
    if not auth_status.is_logged_in():
        raise ValueError("Not logged in. Run 'srest auth login' first")
    
    # Get base URL and token
    base_url = config.get('slurm.url')
    if not base_url:
        raise ValueError("Slurm REST API URL not configured. Run 'srest config set slurm.url <url>'")
    
    token = auth_status.get_token()
    username = auth_status.get_username()
    
    # Create unified client
    return SlurmRESTClient(
        job=JobClient(url=base_url, token=token, username=username),
        node=NodeClient(url=base_url, token=token, username=username),
        partition=PartitionClient(url=base_url, token=token, username=username)
    )

__all__ = [
    'get_client',
    'SlurmRESTClient',
    'JobClient',
    'NodeClient',
    'PartitionClient'
]
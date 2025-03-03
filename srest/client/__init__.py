"""Slurm REST API client based on OpenAPI 3.0.3 specification"""
from typing import Optional, Dict, Any
from dataclasses import dataclass

from .v2 import (
    ClientConfig,
    JobClient,
    NodeClient,
    PartitionClient,
    ReservationClient,
    DiagClient,
    AccountClient,
    SlurmError,
    JobSubmitResponse,
    JobResponse
)

@dataclass
class SlurmRESTClient:
    """Unified client for CLI compatibility"""
    job: JobClient
    node: NodeClient
    partition: PartitionClient
    reservation: ReservationClient
    diag: DiagClient
    account: AccountClient
    
    def submit_job(self, script_content: str, params: Dict[str, Any], return_curl: bool = False) -> Dict[str, Any]:
        """Submit a job to Slurm"""
        response = self.job.submit_job(
            script=script_content,
            params=params,
            return_curl=return_curl
        )
        if isinstance(response, str):
            return {'curl_command': response}
        return response.__dict__
    
    def list_jobs(self, user: Optional[str] = None, return_curl: bool = False) -> Dict[str, Any]:
        """List jobs"""
        response = self.job.get_jobs(user=user, return_curl=return_curl)
        if isinstance(response, str):
            return {'curl_command': response}
        return response.__dict__
    
    def get_job(self, job_id: str, return_curl: bool = False) -> Dict[str, Any]:
        """Get job details"""
        response = self.job.get_job(job_id=job_id, return_curl=return_curl)
        if isinstance(response, str):
            return {'curl_command': response}
        return response.__dict__
    
    def list_nodes(self, **filters) -> Dict[str, Any]:
        """List compute nodes"""
        response = self.node.get_nodes(return_curl=False, **filters)
        if isinstance(response, str):
            return {'curl_command': response}
        return {'nodes': [n.__dict__ for n in response.nodes]}
        
    def get_diag(self, return_curl: bool = False) -> Dict[str, Any]:
        """Get diagnostic information"""
        response = self.diag.get_diagnostics(return_curl=return_curl)
        if isinstance(response, str):
            return {'curl_command': response}
        return response.__dict__
    
    def list_partitions(self, **filters) -> Dict[str, Any]:
        """List partitions"""
        response = self.partition.get_partitions(return_curl=False)
        if isinstance(response, str):
            return {'curl_command': response}
        return response.__dict__
    
    def cancel_job(self, job_id: str, return_curl: bool = False) -> Dict[str, Any]:
        """Cancel a job"""
        response = self.job.cancel_job(job_id=job_id, return_curl=return_curl)
        if isinstance(response, str):
            return {'curl_command': response}
        return response.__dict__

def get_client() -> SlurmRESTClient:
    """Get configured client instance with version checking."""
    from ..config import Config
    from ..auth.status import AuthStatus
    import subprocess
    from ..utils.version import parse_slurm_version, get_compatible_api_version, verify_api_endpoint
    
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
    
    # Get and verify API version
    try:
        result = subprocess.run(['sinfo', '--version'], 
                              capture_output=True, 
                              text=True, 
                              check=True)
        slurm_version = parse_slurm_version(result.stdout.strip())
    except (subprocess.SubprocessError, ValueError) as e:
        raise RuntimeError(f"Failed to get Slurm version: {e}")
    
    api_version = config.get('slurm.api_version')
    
    if not api_version:
        api_version = get_compatible_api_version(slurm_version)
        config.set('slurm.api_version', api_version)
    
    # Verify API endpoint
    if not verify_api_endpoint(base_url, api_version):
        raise ValueError(f"API endpoint not accessible with version {api_version}")
    
    # Create client config
    client_config = ClientConfig(
        base_url=base_url,
        api_version=api_version,
        token=token
    )
    
    # Create unified client
    return SlurmRESTClient(
        job=JobClient(client_config),
        node=NodeClient(client_config),
        partition=PartitionClient(client_config),
        reservation=ReservationClient(client_config),
        diag=DiagClient(client_config),
        account=AccountClient(client_config)
    )

__all__ = [
    'get_client',
    'SlurmRESTClient',
    'ClientConfig',
    'JobClient',
    'NodeClient',
    'PartitionClient',
    'ReservationClient',
    'DiagClient',
    'AccountClient',
    'SlurmError'
]
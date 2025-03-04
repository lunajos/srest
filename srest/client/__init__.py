"""Slurm REST API client based on OpenAPI 3.0.3 specification"""
from typing import Optional, Dict, Any
from dataclasses import dataclass

from .v2.base import ClientConfig
from .v2.jobs import JobClient
from .v2.nodes import NodeClient
from .v2.partitions import PartitionClient
from .v2.diag import DiagClient
from .v2.licenses import LicenseClient

from .v2.db import DbClient

@dataclass
class SlurmRESTClient:
    """Unified client for CLI compatibility"""
    job: JobClient
    node: NodeClient
    partition: PartitionClient
    diag: DiagClient
    license: LicenseClient

    db: DbClient
    
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

    def get_diag(self, return_curl: bool = False) -> Dict[str, Any]:
        """Get diagnostic information"""
        response = self.diag.get_diagnostics(return_curl=return_curl)
        if isinstance(response, str):
            return {'curl_command': response}
        return response.to_dict()

    def list_licenses(self, return_curl: bool = False) -> Dict[str, Any]:
        """List licenses"""
        response = self.license.get_licenses(return_curl=return_curl)
        if isinstance(response, str):
            return {'curl_command': response}
        return response.to_dict()

    def list_accounts(self, user: Optional[str] = None, return_curl: bool = False) -> Dict[str, Any]:
        """List accounts"""
        response = self.db.get_accounts(user=user, return_curl=return_curl)
        if isinstance(response, str):
            return {'curl_command': response}
        return response.to_dict()

    def list_mcs_labels(self, type: Optional[str] = None, return_curl: bool = False) -> Dict[str, Any]:
        """List MCS labels"""
        response = self.mcs.get_mcs_labels(type=type, return_curl=return_curl)
        if isinstance(response, str):
            return {'curl_command': response}
        return response.to_dict()

    def get_mcs_label(self, label: str, return_curl: bool = False) -> Dict[str, Any]:
        """Get MCS label details"""
        response = self.mcs.get_mcs_label(label, return_curl=return_curl)
        if isinstance(response, str):
            return {'curl_command': response}
        return response.to_dict()

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
    config = ClientConfig(
        base_url=base_url,
        token=token,
        username=username
    )
    
    return SlurmRESTClient(
        job=JobClient(config),
        node=NodeClient(config),
        partition=PartitionClient(config),
        diag=DiagClient(config),
        license=LicenseClient(config),

        db=DbClient(config)
    )

__all__ = [
    'get_client',
    'SlurmRESTClient',
    'JobClient',
    'NodeClient',
    'PartitionClient',
    'DiagClient',
    'LicenseClient',
    'DbClient'
]
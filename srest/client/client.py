import os
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass
import warnings
import urllib3
import requests
from .endpoints import SlurmEndpoints
from ..config import Config
from ..auth.keycloak import KeycloakAuth

# Disable urllib3 warnings about LibreSSL
warnings.filterwarnings('ignore', category=urllib3.exceptions.NotOpenSSLWarning)

@dataclass
class SlurmError(Exception):
    """Slurm API error"""
    message: str
    error_code: Optional[int] = None

def get_client() -> 'SlurmClient':
    """Get configured client instance"""
    config = Config()
    
    # Get base URL
    base_url = config.get('slurm.url')
    if not base_url:
        raise ValueError("Slurm REST API URL not configured. Run 'srest config set slurm.url <url>'")
    
    # Get auth token from file
    token_file = os.path.expanduser("~/.config/srest/token.json")
    if not os.path.exists(token_file):
        raise ValueError("Not logged in. Run 'srest auth login' first")
        
    with open(token_file, 'r') as f:
        import json
        token_data = json.load(f)
        
    return SlurmClient(base_url=base_url, token=token_data['access_token'])
    
class SlurmClient:
    """Client for interacting with Slurm REST API"""
    
    def __init__(self, base_url: Optional[str] = None, token: Optional[str] = None):
        """Initialize Slurm REST client"""
        self.base_url = base_url
        if not self.base_url:
            raise ValueError("base_url is required")
            
        self.token = token
        if not self.token:
            raise ValueError("token is required")
            
        self.endpoints = SlurmEndpoints(self.base_url)
        self.session = requests.Session()
        self.session.headers.update({
            'X-SLURM-USER-TOKEN': self.token,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request to Slurm REST API"""
        try:
            response = self.session.request(method, endpoint, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if e.response is not None:
                try:
                    error_data = e.response.json()
                    error_msg = error_data.get('error', {}).get('message', str(e))
                    error_code = error_data.get('error', {}).get('error_code')
                    raise SlurmError(error_msg, error_code) from e
                except (ValueError, KeyError):
                    raise SlurmError(str(e)) from e
            raise SlurmError(str(e)) from e
        except requests.exceptions.RequestException as e:
            raise SlurmError(f"Request failed: {str(e)}") from e
    
    def submit_job(self, script_content: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Submit a job to Slurm"""
        # Handle array jobs
        if 'array' in params:
            array_spec = params['array']
            # Validate array spec format (e.g., "1-10:2")
            if not self._validate_array_spec(array_spec):
                raise ValueError(f"Invalid array specification: {array_spec}")
        
        # Handle dependencies
        if 'dependency' in params:
            dep_spec = params['dependency']
            # Validate and format dependency spec
            params['dependency'] = self._format_dependency_spec(dep_spec)
            
        # Convert mcs-label to mcs_label if present
        if 'mcs-label' in params:
            params['mcs_label'] = params.pop('mcs-label')
        
        payload = {
            "script": script_content,
            **params
        }
        return self._make_request('POST', self.endpoints.jobs, json=payload)
    
    def list_jobs(self, **params) -> Dict[str, Any]:
        """List jobs with optional filters"""
        return self._make_request('GET', self.endpoints.jobs, params=params)
    
    def get_job(self, job_id: str) -> Dict[str, Any]:
        """Get information about a specific job"""
        return self._make_request('GET', f"{self.endpoints.jobs}/{job_id}")
    
    def cancel_job(self, job_id: str, signal: str = "SIGTERM") -> Dict[str, Any]:
        """Cancel a specific job"""
        return self._make_request('DELETE', f"{self.endpoints.jobs}/{job_id}", 
                                params={"signal": signal})
    
    def list_nodes(self, **params) -> Dict[str, Any]:
        """List compute nodes with optional filters"""
        return self._make_request('GET', self.endpoints.nodes, params=params)
    
    def get_node(self, node_name: str) -> Dict[str, Any]:
        """Get information about a specific node"""
        return self._make_request('GET', f"{self.endpoints.nodes}/{node_name}")
    
    def list_partitions(self, **params) -> Dict[str, Any]:
        """List partitions with optional filters"""
        return self._make_request('GET', self.endpoints.partitions, params=params)
        
    def list_reservations(self, **params) -> Dict[str, Any]:
        """List reservations with optional filters"""
        return self._make_request('GET', self.endpoints.reservations, params=params)
    
    def create_reservation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a reservation"""
        return self._make_request('POST', self.endpoints.reservations, json=params)
    
    def delete_reservation(self, name: str) -> Dict[str, Any]:
        """Delete a reservation"""
        return self._make_request('DELETE', f"{self.endpoints.reservations}/{name}")
    
    def list_licenses(self) -> Dict[str, Any]:
        """List license information"""
        return self._make_request('GET', self.endpoints.licenses)
    
    def get_diag(self) -> Dict[str, Any]:
        """Get diagnostic information"""
        return self._make_request('GET', self.endpoints.diag)
    
    def ping(self) -> Dict[str, Any]:
        """Ping the Slurm controller"""
        return self._make_request('GET', self.endpoints.ping)
    
    def list_accounts(self, **params) -> Dict[str, Any]:
        """List accounts"""
        return self._make_request('GET', self.endpoints.accounts, params=params)
        
    def get_account(self, name: str) -> Dict[str, Any]:
        """Get account details"""
        return self._make_request('GET', f"{self.endpoints.accounts}/{name}")
        
    def list_associations(self, **params) -> Dict[str, Any]:
        """List user-account associations"""
        return self._make_request('GET', self.endpoints.associations, params=params)
        
    def list_mcs_labels(self, **params) -> Dict[str, Any]:
        """List MCS labels"""
        return self._make_request('GET', self.endpoints.mcs, params=params)
        
    def get_mcs_label(self, name: str) -> Dict[str, Any]:
        """Get MCS label details"""
        return self._make_request('GET', f"{self.endpoints.mcs}/{name}")
    
    def _validate_array_spec(self, array_spec: str) -> bool:
        """Validate job array specification"""
        import re
        # Valid formats:
        # - "N" (single task)
        # - "N-M" (range)
        # - "N-M:X" (range with step)
        # - "N,M,O" (task list)
        # - "N-M,O-P" (multiple ranges)
        pattern = r'^(\d+(-\d+)?)(:\d+)?([,]\d+(-\d+)?(:\d+)?)*$'
        return bool(re.match(pattern, array_spec))
    
    def _format_dependency_spec(self, dep_spec: Union[str, List[str]]) -> str:
        """Format job dependency specification"""
        if isinstance(dep_spec, list):
            deps = []
            for dep in dep_spec:
                if ':' not in dep:
                    # Assume afterok if no type specified
                    deps.append(f"afterok:{dep}")
                else:
                    deps.append(dep)
            return ','.join(deps)
        
        if ':' not in dep_spec:
            return f"afterok:{dep_spec}"
        return dep_spec
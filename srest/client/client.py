import os
import subprocess
from typing import Dict, Any, Optional, List, Union, Tuple
from dataclasses import dataclass
import warnings
import urllib3
import requests
from .endpoints import SlurmEndpoints
from .v2.reservations import ReservationClient
from ..config import Config
from ..auth.keycloak import KeycloakAuth
from ..auth.status import AuthStatus
from ..utils.version import parse_slurm_version, get_compatible_api_version, verify_api_endpoint

# Disable urllib3 warnings about LibreSSL
warnings.filterwarnings('ignore', category=urllib3.exceptions.NotOpenSSLWarning)

@dataclass
class SlurmError(Exception):
    """Slurm API error"""
    message: str
    error_code: Optional[int] = None

def get_slurm_version() -> Tuple[int, int, int]:
    """Get installed Slurm version."""
    try:
        result = subprocess.run(['sinfo', '--version'], 
                              capture_output=True, 
                              text=True, 
                              check=True)
        return parse_slurm_version(result.stdout.strip())
    except (subprocess.SubprocessError, ValueError) as e:
        raise RuntimeError(f"Failed to get Slurm version: {e}")

def get_client() -> 'SlurmClient':
    """Get configured client instance with version checking."""
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
    slurm_version = get_slurm_version()
    api_version = config.get('slurm.api_version')
    
    if not api_version:
        api_version = get_compatible_api_version(slurm_version)
        config.set('slurm.api_version', api_version)
    
    # Verify API endpoint
    if not verify_api_endpoint(base_url, api_version):
        raise ValueError(f"API endpoint not accessible with version {api_version}")
    
    return SlurmClient(base_url=base_url, token=token, api_version=api_version)
    
class SlurmClient:
    """Client for interacting with Slurm REST API"""
    
    def __init__(self, base_url: str, token: str, api_version: str):
        self._reservation_client = None
        """Initialize Slurm REST client with version support"""
        self.base_url = base_url
        self.token = token
        self.api_version = api_version
        
        if not all([self.base_url, self.token, self.api_version]):
            raise ValueError("base_url, token, and api_version are required")
            
        # Validate API version format
        if not self.api_version.startswith('v'):
            raise ValueError(f"Invalid API version format: {self.api_version}")
            
        self.endpoints = SlurmEndpoints(self.base_url, self.api_version)
        self.session = requests.Session()
        self.session.headers.update({
            'X-SLURM-USER-TOKEN': self.token,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    @property
    def reservation(self) -> ReservationClient:
        """Get reservation client"""
        if self._reservation_client is None:
            self._reservation_client = ReservationClient(self)
        return self._reservation_client

    def _make_request(self, method: str, endpoint: str, return_curl: bool = False, **kwargs) -> Union[Dict[str, Any], str]:
        """Make HTTP request to Slurm REST API"""
        # Generate curl command if requested
        if return_curl:
            curl_parts = [f"curl -X {method}"]
            
            # Add headers
            for header, value in self.session.headers.items():
                curl_parts.append(f"-H '{header}: {value}'")
            
            # Add request body if present
            if 'json' in kwargs:
                curl_parts.append(f"-d '{json.dumps(kwargs['json'])}'")
            
            # Add URL
            curl_parts.append(f"'{endpoint}'")
            
            return ' \
  '.join(curl_parts)
        
        try:
            response = self.session.request(method, endpoint, **kwargs)
            response.raise_for_status()
            if response.content:  # Only try to parse JSON if there's content
                return response.json()
            return {}
        except requests.exceptions.HTTPError as e:
            if e.response is not None:
                try:
                    if e.response.content:  # Only try to parse JSON if there's content
                        error_data = e.response.json()
                        error_msg = error_data.get('error', {}).get('message', str(e))
                        error_code = error_data.get('error', {}).get('error_code')
                        raise SlurmError(error_msg, error_code) from e
                except (ValueError, KeyError):
                    # Handle case where response isn't JSON
                    error_text = e.response.text if e.response.text else str(e)
                    raise SlurmError(error_text) from e
            raise SlurmError(str(e)) from e
        except requests.exceptions.RequestException as e:
            raise SlurmError(f"Request failed: {str(e)}") from e
    
    def submit_job(self, script_content: str, params: Dict[str, Any], return_curl: bool = False) -> Union[Dict[str, Any], str]:
        """Submit a job to Slurm"""
        # Clean and validate parameters
        clean_params = {}
        
        # Handle array jobs
        if 'array' in params:
            array_spec = params['array']
            if self._validate_array_spec(array_spec):
                clean_params['array'] = array_spec
        
        # Handle dependencies
        if 'dependency' in params:
            dep_spec = params['dependency']
            clean_params['dependency'] = self._format_dependency_spec(dep_spec)
        
        # Handle time format
        if 'time' in params:
            time_val = params['time']
            if isinstance(time_val, str) and '-' in time_val:
                # Convert days-hours:minutes:seconds to minutes
                parts = time_val.split('-')
                days = int(parts[0])
                time_parts = parts[1].split(':')
                hours = int(time_parts[0])
                minutes = int(time_parts[1]) if len(time_parts) > 1 else 0
                clean_params['time_limit'] = days * 24 * 60 + hours * 60 + minutes
            else:
                clean_params['time_limit'] = int(time_val)
        
        # Map parameter names to Slurm REST API expected names
        param_mapping = {
            'name': 'job_name',
            'nodes': 'nodes',
            'ntasks': 'tasks',
            'cpus-per-task': 'cpus_per_task',
            'mem': 'memory',
            'partition': 'partition',
            'account': 'account',
            'qos': 'qos',
            'mcs-label': 'mcs_label'
        }
        
        # Copy validated parameters
        for key, value in params.items():
            if key in param_mapping and value is not None:
                clean_params[param_mapping[key]] = value
        
        # Prepare the job submission payload
        payload = {
            "script": script_content,
        }
        
        if clean_params:
            payload['job'] = clean_params
        
        try:
            return self._make_request('POST', self.endpoints.job_submit, json=payload, return_curl=return_curl)
        except requests.exceptions.HTTPError as e:
            if e.response is not None:
                try:
                    error_data = e.response.json()
                    error_msg = error_data.get('error', {}).get('message', str(e))
                    error_code = error_data.get('error', {}).get('error_code')
                    raise SlurmError(f"Job submission failed: {error_msg}", error_code) from e
                except (ValueError, KeyError):
                    # Handle case where response isn't JSON
                    error_text = e.response.text if e.response.text else str(e)
                    raise SlurmError(f"Job submission failed: {error_text}") from e
            raise SlurmError(f"Job submission failed: {str(e)}") from e
        except requests.exceptions.RequestException as e:
            raise SlurmError(f"Request failed: {str(e)}") from e
    
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
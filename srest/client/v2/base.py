"""Base client for Slurm REST API"""
import json
import os
from typing import Dict, Any, Optional, Union, Type, TypeVar
from dataclasses import dataclass
import requests
from urllib.parse import urljoin
import urllib3
from urllib3.exceptions import InsecureRequestWarning
from urllib3.util import response

from .models import SlurmError, SlurmResponse

# Patch urllib3's header parsing to be more lenient
def _patched_assert_header_parsing(headers):
    return headers

response.assert_header_parsing = _patched_assert_header_parsing

# Disable urllib3 warnings
urllib3.disable_warnings(InsecureRequestWarning)

T = TypeVar('T', bound=SlurmResponse)

@dataclass
class ClientConfig:
    """Client configuration"""
    base_url: str
    api_version: str = 'v0.0.42'
    username: Optional[str] = None
    token: Optional[str] = None
    bearer_token: Optional[str] = None
    verify_ssl: bool = True

class BaseClient:
    """Base client with authentication and request handling"""
    
    def __init__(self, config: ClientConfig):
        """Initialize client with configuration"""
        self.config = config
        self.session = self._create_session()
        
    def _create_session(self) -> requests.Session:
        """Create and configure requests session"""
        session = requests.Session()
        session.verify = self.config.verify_ssl
        
        # Add retry strategy
        adapter = requests.adapters.HTTPAdapter(
            max_retries=urllib3.util.Retry(
                total=3,
                backoff_factor=0.1,
                status_forcelist=[500, 502, 503, 504]
            )
        )
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        
        # Set headers based on authentication method
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Connection': 'close',  # Use close to avoid keep-alive issues
        }
        
        # Get token from auth status
        from ...auth.status import AuthStatus
        auth_status = AuthStatus()
        if auth_status.is_logged_in():
            token = auth_status.get_token()
            if token:
                # Always use Bearer auth for JWT tokens
                headers['Authorization'] = f'Bearer {token}'
        
        if self.config.username and self.config.token:
            # Method 1: Username + Token
            # Always use Bearer auth for tokens
            headers['Authorization'] = f'Bearer {self.config.token}'
        elif self.config.token:
            # Method 2: Token only
            # Always use Bearer auth for tokens
            headers['Authorization'] = f'Bearer {self.config.token}'
        elif self.config.bearer_token:
            # Method 3: Bearer token
            headers['Authorization'] = f'Bearer {self.config.bearer_token}'
            
        session.headers.update(headers)
        return session
    
    def _get_url(self, endpoint: str) -> str:
        """Get full URL for endpoint"""
        # Normalize URL parts
        base_url = self.config.base_url.rstrip('/')
        endpoint = endpoint.lstrip('/')
        
        # Construct full URL ensuring no double slashes
        return f"{base_url}/{endpoint}"
    
    def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        response_type: Type[T],
        return_curl: bool = False,
        **kwargs
    ) -> Union[T, str]:
        """Make HTTP request to Slurm REST API
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            response_type: Expected response type
            return_curl: If True, return curl command instead of making request
            **kwargs: Additional arguments for requests
            
        Returns:
            Response object of specified type or curl command if return_curl=True
        """
        url = self._get_url(endpoint)
        
        # Generate curl command if requested
        if return_curl:
            curl_parts = [f"curl -X {method}"]
            
            # Add essential headers only
            essential_headers = {
                'Content-Type': 'application/json',
                'Authorization': self.session.headers.get('Authorization', ''),
                'X-SLURM-USER-TOKEN': self.session.headers.get('X-SLURM-USER-TOKEN', ''),
                'X-SLURM-USER-NAME': self.session.headers.get('X-SLURM-USER-NAME', '')
            }
            for header, value in essential_headers.items():
                if value:  # Only add if value is not empty
                    curl_parts.append(f"-H '{header}: {value}'")
            
            # Add request body if present
            if 'json' in kwargs:
                curl_parts.append(f"-d '{json.dumps(kwargs['json'])}'")
            
            # Add URL
            curl_parts.append(f"'{url}'")
            
            return ' '.join(curl_parts)
        
        try:
            response = self.session.request(
                method, 
                url, 
                timeout=30,
                **kwargs
            )
            
            # Handle empty responses
            if not response.content and response.status_code == 200:
                return response_type()
            
            # Try to parse response as JSON
            try:
                data = response.json()
            except ValueError:
                # If not JSON and status is error, raise error
                if response.status_code >= 400:
                    raise SlurmError(
                        error_code=response.status_code,
                        message=response.text or f"HTTP {response.status_code}"
                    )
                # If not JSON but status is ok, return empty response
                return response_type()
            
            # Check for API-level errors in JSON response
            if response.status_code >= 400:
                # Ignore TRES errors as they are not critical
                if response.status_code == 511 and any(e.get('source') == 'slurmdb_tres_get' for e in data.get('errors', [])):
                    pass
                else:
                    error_msg = data.get('error', {}).get('message', response.text)
                    raise SlurmError(
                        error_code=response.status_code,
                        message=error_msg
                    )
            
            # Create response object
            try:
                return response_type(**data)
            except (TypeError, KeyError) as e:
                # Return empty response if we got a 200 but invalid data
                if response.status_code == 200:
                    return response_type()
                raise SlurmError(
                    error_code=None,
                    message=f"Invalid response format: {str(e)}"
                )
                
        except requests.exceptions.Timeout:
            raise SlurmError(
                error_code=None,
                message="Request timed out"
            )
            
        except requests.exceptions.ConnectionError as e:
            raise SlurmError(
                error_code=None,
                message=f"Connection failed: {str(e)}"
            )
            
        except requests.exceptions.RequestException as e:
            raise SlurmError(
                error_code=None,
                message=f"Request failed: {str(e)}"
            )

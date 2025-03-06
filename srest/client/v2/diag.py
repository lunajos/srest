"""Diagnostic client"""
from typing import Dict, Any, Optional, Union, List
import requests
from .base import BaseClient
from .models import SlurmResponse, SlurmError
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

@dataclass
class OpenAPIVersionsResponse(SlurmResponse):
    """Response for OpenAPI versions query"""
    versions: List[str] = None

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
        
    def _extract_versions(self, spec: Dict[str, Any]) -> List[str]:
        """Extract all API versions from OpenAPI spec paths
        
        Args:
            spec: OpenAPI specification dictionary
            
        Returns:
            List of API versions (e.g., ['v0.0.40', 'v0.0.41', 'v0.0.42'])
            sorted in ascending order
            
        Raises:
            SlurmError: If no API versions found in spec
        """
        versions = set()
        for path in spec.get('paths', {}).keys():
            if path.startswith('/slurm/v'):
                version = path.split('/')[2]  # Get version part
                versions.add(version)
        
        if not versions:
            raise SlurmError(
                error_code=None,
                message="No API versions found in OpenAPI spec"
            )
        
        return sorted(versions)
        
    def _extract_latest_version(self, spec: Dict[str, Any]) -> str:
        """Extract the latest API version from OpenAPI spec paths
        
        Args:
            spec: OpenAPI specification dictionary
            
        Returns:
            Latest API version (e.g., 'v0.0.42')
            
        Raises:
            SlurmError: If no API versions found in spec
        """
        return self._extract_versions(spec)[-1]  # Last version is latest
    
    def get_versions(self, return_curl: bool = False, all_versions: bool = False) -> Union[str, List[str], Dict[str, Any]]:
        """Get slurmrestd API version(s) from OpenAPI spec
        
        Args:
            return_curl: If True, returns curl command string instead of making request
            all_versions: If True, returns list of all supported versions instead of just latest
        
        Returns:
            If return_curl is True, returns curl command string
            If all_versions is True, returns sorted list of versions (e.g., ['v0.0.40', 'v0.0.41', 'v0.0.42'])
            Otherwise returns the latest API version (e.g., 'v0.0.42')
        
        The version(s) are extracted from the API paths in the OpenAPI spec.
        """
        # OpenAPI spec is at the root URL /openapi/v3
        try:
            base_url = self.config.base_url.split('/slurm/')[0]  # Get base URL without version
        except IndexError:
            # If URL doesn't contain '/slurm/', use the whole URL as base
            base_url = self.config.base_url.rstrip('/')
        url = f"{base_url}/openapi/v3"
        
        if return_curl:
            curl_parts = ["curl -X GET"]
            if not self.config.verify_ssl:
                curl_parts.append("-k")
            
            # Add essential headers from session
            essential_headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Authorization': self.session.headers.get('Authorization', '')
            }
            for header, value in essential_headers.items():
                if value:  # Only add if value is not empty
                    curl_parts.append(f"-H '{header}: {value}'")
            
            curl_parts.append(f"'{url}'")
            return ' '.join(curl_parts)
            
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return self._extract_versions(response.json()) if all_versions else self._extract_latest_version(response.json())
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                # Try the older endpoint at /openapi.json
                try:
                    url = f"{base_url}/openapi.json"
                    response = self.session.get(url, timeout=30)
                    response.raise_for_status()
                    return self._extract_versions(response.json()) if all_versions else self._extract_latest_version(response.json())
                except Exception as inner_e:
                    raise SlurmError(
                        error_code=None,
                        message=f"Failed to get OpenAPI spec from both /openapi/v3 and /openapi.json: {str(e)} and {str(inner_e)}"
                    )
            raise SlurmError(
                error_code=None,
                message=f"Failed to get OpenAPI spec: {str(e)}"
            )
        except Exception as e:
            raise SlurmError(
                error_code=None,
                message=f"Failed to get OpenAPI spec: {str(e)}"
            )

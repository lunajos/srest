"""Account management client"""
from typing import Dict, Any, Optional, Union, List
from dataclasses import dataclass
from .base import BaseClient
from .models import SlurmMeta

@dataclass
class AccountInfo:
    """Account information"""
    name: str
    description: Optional[str] = None
    organization: Optional[str] = None
    coordinators: Optional[List[str]] = None
    allowed_partitions: Optional[List[str]] = None
    allowed_qos: Optional[List[str]] = None
    default_qos: Optional[str] = None

@dataclass
class AccountResponse:
    """Response for account queries"""
    meta: SlurmMeta
    accounts: List[AccountInfo]
    errors: Optional[List[Dict[str, Any]]] = None
    warnings: Optional[List[Dict[str, Any]]] = None

@dataclass
class AssociationInfo:
    """User-account association information"""
    account: str
    user: str
    partition: Optional[str] = None
    max_jobs: Optional[int] = None
    max_nodes: Optional[int] = None
    max_wall_duration: Optional[int] = None
    qos: Optional[List[str]] = None

@dataclass
class AssociationResponse:
    """Response for association queries"""
    meta: SlurmMeta
    associations: List[AssociationInfo]
    errors: Optional[List[Dict[str, Any]]] = None
    warnings: Optional[List[Dict[str, Any]]] = None

class AccountClient(BaseClient):
    """Client for account-related operations"""
    
    def get_accounts(self, return_curl: bool = False) -> Union[AccountResponse, str]:
        """Get list of accounts"""
        return self._make_request(
            method='GET',
            endpoint='/accounts',
            response_type=AccountResponse,
            return_curl=return_curl
        )
    
    def get_account(self, name: str, return_curl: bool = False) -> Union[AccountResponse, str]:
        """Get information about a specific account"""
        return self._make_request(
            method='GET',
            endpoint=f'/account/{name}',
            response_type=AccountResponse,
            return_curl=return_curl
        )
    
    def get_associations(
        self,
        account: Optional[str] = None,
        user: Optional[str] = None,
        return_curl: bool = False
    ) -> Union[AssociationResponse, str]:
        """Get user-account associations"""
        params = {}
        if account:
            params['account'] = account
        if user:
            params['user'] = user
            
        return self._make_request(
            method='GET',
            endpoint='/associations',
            params=params,
            response_type=AssociationResponse,
            return_curl=return_curl
        )

"""Database client for Slurm accounting data"""
from typing import Dict, Any, Optional, Union, List
from datetime import datetime
from .base import BaseClient
from .models import SlurmResponse
from dataclasses import dataclass

@dataclass
class JobAccountingResponse(SlurmResponse):
    """Response for job accounting queries"""
    jobs: List[Dict[str, Any]] = None
    
    def __init__(self, **data):
        # Initialize parent
        super().__init__(**data)
        
        # Set jobs
        self.jobs = data.get('jobs', [])

@dataclass
class AccountResponse(SlurmResponse):
    """Response for account queries"""
    accounts: List[Dict[str, Any]] = None
    
    def __init__(self, **data):
        # Initialize parent
        super().__init__(**data)
        
        # Set accounts
        self.accounts = data.get('accounts', [])

class DbClient(BaseClient):
    """Client for Slurm database operations"""
    
    def get_jobs(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        user: Optional[str] = None,
        account: Optional[str] = None,
        job_id: Optional[str] = None,
        return_curl: bool = False
    ) -> Union[JobAccountingResponse, str]:
        """Get job accounting records
        
        Args:
            start_time: Filter jobs after this time
            end_time: Filter jobs before this time
            user: Filter by username
            account: Filter by account
            job_id: Filter by job ID
            return_curl: If True, return curl command instead of executing
            
        Returns:
            JobAccountingResponse or curl command if return_curl=True
        """
        params = {}
        
        # Convert times to Unix timestamps
        if start_time:
            params['start_time'] = int(start_time.timestamp())
        if end_time:
            params['end_time'] = int(end_time.timestamp())
            
        # Add other filters
        if user:
            params['user'] = user
        if account:
            params['account'] = account
        if job_id:
            params['job_id'] = job_id
            
        return self._make_request(
            method='GET',
            endpoint='/slurmdb/v0.0.36/jobs',
            response_type=JobAccountingResponse,
            params=params,
            return_curl=return_curl
        )
        
    def get_accounts(
        self,
        user: Optional[str] = None,
        return_curl: bool = False
    ) -> Union[AccountResponse, str]:
        """Get account information
        
        Args:
            return_curl: If True, return curl command instead of executing
            
        Returns:
            AccountResponse or curl command if return_curl=True
        """
        return self._make_request(
            method='GET',
            endpoint='/slurmdb/v0.0.36/accounts',
            response_type=AccountResponse,
            params={'user': user} if user else None,
            return_curl=return_curl
        )

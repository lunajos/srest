"""Job submission and management client"""
from typing import Dict, Any, Optional, Union, List
from .base import BaseClient
from .models import (
    JobSubmitRequest,
    JobSubmitResponse,
    JobResponse,
    JobInfo
)

class JobClient(BaseClient):
    """Client for job-related operations"""
    
    def submit_job(
        self,
        script: str,
        params: Optional[Dict[str, Any]] = None,
        return_curl: bool = False
    ) -> Union[JobSubmitResponse, str]:
        """Submit a job to Slurm
        
        Args:
            script: Job script content
            params: Optional job parameters
            return_curl: If True, return curl command instead of submitting
            
        Returns:
            JobSubmitResponse or curl command if return_curl=True
        """
        payload = JobSubmitRequest(
            script=script,
            job=params
        )
        
        return self._make_request(
            method='POST',
            endpoint='/job/submit',
            response_type=JobSubmitResponse,
            json=payload.__dict__,
            return_curl=return_curl
        )
    
    def get_jobs(
        self,
        user: Optional[str] = None,
        return_curl: bool = False
    ) -> Union[JobResponse, str]:
        """Get list of jobs
        
        Args:
            user: Optional username to filter jobs
            return_curl: If True, return curl command instead of fetching
            
        Returns:
            JobResponse or curl command if return_curl=True
        """
        params = {}
        if user:
            params['user'] = user
            
        return self._make_request(
            method='GET',
            endpoint='/job',
            response_type=JobResponse,
            params=params,
            return_curl=return_curl
        )
    
    def get_job(
        self,
        job_id: str,
        return_curl: bool = False
    ) -> Union[JobResponse, str]:
        """Get information about a specific job
        
        Args:
            job_id: Job ID to query
            return_curl: If True, return curl command instead of fetching
            
        Returns:
            JobResponse or curl command if return_curl=True
        """
        return self._make_request(
            method='GET',
            endpoint=f'/job/{job_id}',
            response_type=JobResponse,
            return_curl=return_curl
        )
    
    def cancel_job(
        self,
        job_id: str,
        signal: str = 'SIGTERM',
        return_curl: bool = False
    ) -> Union[JobResponse, str]:
        """Cancel a job
        
        Args:
            job_id: Job ID to cancel
            signal: Signal to send (default: SIGTERM)
            return_curl: If True, return curl command instead of cancelling
            
        Returns:
            JobResponse or curl command if return_curl=True
        """
        return self._make_request(
            method='DELETE',
            endpoint=f'/job/{job_id}',
            response_type=JobResponse,
            params={'signal': signal},
            return_curl=return_curl
        )

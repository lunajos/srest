"""Job submission and management client"""
import json
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
        # Create job submission request
        job_params = params or {}
        
        # Parse SBATCH directives from script
        script_lines = []
        for line in script.split('\n'):
            if line.startswith('#SBATCH'):
                try:
                    # Extract directive and value
                    parts = line.split(None, 2)
                    if len(parts) < 2:
                        continue
                        
                    flag = parts[1].strip()
                    value = parts[2].strip() if len(parts) > 2 else None
                    
                    # Convert known parameters
                    if flag == '-J':
                        job_params['name'] = value
                    elif flag == '-N':
                        job_params['nodes'] = value
                    elif flag == '-n':
                        job_params['ntasks'] = int(value)
                    elif flag == '-p':
                        job_params['partition'] = value
                    elif flag == '--mcs-label':
                        job_params['mcs_label'] = value
                    else:
                        # Handle any other flag by removing leading dashes and using as key
                        key = flag.lstrip('-').replace('-', '_')
                        job_params[key] = value
                except Exception as e:
                    print(f'Warning: Failed to parse directive {line}: {e}')
            script_lines.append(line)
        
        # Convert mail_type from string to list of valid flags
        if 'mail_type' in job_params:
            if job_params['mail_type'] == ['ALL']:
                job_params['mail_type'] = ['begin', 'end', 'fail', 'requeue']
            else:
                # Convert to lowercase and remove MAIL_ prefix
                job_params['mail_type'] = [flag.lower().replace('mail_', '') for flag in job_params['mail_type']]
                
        # Working directory priority:
        # 1. API params (passed in from CLI)
        # 2. Script directive (--chdir/-D)
        # 3. Current working directory
        if not params or 'current_working_directory' not in params:
            if 'current_working_directory' not in job_params:
                import os
                job_params['current_working_directory'] = os.getcwd()
        
        # Handle node specifications
        if 'req_nodes' in job_params:
            # Keep as original string format
            job_params['nodes'] = job_params.pop('req_nodes')
        if 'exc_nodes' in job_params:
            # Keep as original string format for excluded nodes
            job_params['exclude_nodes'] = job_params.pop('exc_nodes')
            
        # Remove problematic parameters
        job_params.pop('tres_per_job', None)
            
        # Ensure Unix line endings
        script_content = '\n'.join(line.rstrip('\r') for line in script_lines)
        
        payload = {
            'job': job_params,
            'script': script_content
        }
        
        # Debug log
        #print("Job submission payload:")
        #print(json.dumps(payload, indent=2))
            
        return self._make_request(
            method='POST',
            endpoint='/slurm/v0.0.42/job/submit',
            response_type=JobSubmitResponse,
            json=payload,
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
            endpoint='/slurm/v0.0.42/jobs',
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
            endpoint=f'/slurm/v0.0.42/job/{job_id}',
            response_type=JobResponse,
            return_curl=return_curl
        )
    
    def cancel_job(
        self,
        job_id: str,
        return_curl: bool = False
    ) -> Union[JobResponse, str]:
        """Cancel a job
        
        Args:
            job_id: Job ID to cancel
            return_curl: If True, return curl command instead of cancelling
            
        Returns:
            JobResponse or curl command if return_curl=True
        """
        return self._make_request(
            method='DELETE',
            endpoint=f'/slurm/v0.0.42/job/{job_id}',
            response_type=JobResponse,
            params={'signal': 'SIGTERM'},
            return_curl=return_curl
        )

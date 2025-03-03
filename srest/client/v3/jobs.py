"""Job submission and management client using swagger-generated models"""

import os
from typing import Dict, Any, Optional, Union, List
from swagger_client.models import (
    V0036JobSubmission,
    V0036JobProperties,
    V0036JobSubmissionResponse,
    V0036JobsResponse,
    V0036Signal
)
from .base import BaseClient

class JobClient(BaseClient):
    """Client for job-related operations"""
    
    def submit_job(
        self,
        script: str,
        params: Optional[Dict[str, Any]] = None,
        return_curl: bool = False
    ) -> Union[V0036JobSubmissionResponse, str]:
        """Submit a job to Slurm
        
        Args:
            script: Job script content
            params: Optional job parameters
            return_curl: If True, return curl command instead of submitting
            
        Returns:
            V0036JobSubmissionResponse or curl command if return_curl=True
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
                    if flag == '-J' or flag == '--job-name':
                        job_params['name'] = value
                    elif flag == '-N' or flag == '--nodes':
                        job_params['nodes'] = value
                    elif flag == '-n' or flag == '--ntasks':
                        job_params['ntasks'] = int(value)
                    elif flag == '-p' or flag == '--partition':
                        job_params['partition'] = value
                    elif flag == '--array':
                        job_params['array'] = value
                    elif flag == '--mail-type':
                        if value == 'ALL':
                            job_params['mail_type'] = ['MAIL_BEGIN', 'MAIL_END', 'MAIL_FAIL', 'MAIL_REQUEUE']
                        else:
                            job_params['mail_type'] = [f'MAIL_{t.upper()}' for t in value.split(',')]
                    elif flag == '--mail-user':
                        job_params['mail_user'] = value
                    elif flag == '--time':
                        job_params['time_limit'] = value
                    elif flag == '--mem':
                        job_params['memory'] = value
                    elif flag == '--cpus-per-task':
                        job_params['cpus_per_task'] = int(value)
                    elif flag == '--gres':
                        job_params['gres'] = value
                    elif flag == '--constraint':
                        job_params['constraints'] = value
                    elif flag == '--nodelist':
                        job_params['req_nodes'] = value
                    elif flag == '--exclude':
                        job_params['exc_nodes'] = value
                except Exception as e:
                    print(f'Warning: Failed to parse directive {line}: {e}')
            script_lines.append(line)
            
        # Ensure Unix line endings
        script_content = '\n'.join(line.rstrip('\r') for line in script_lines)
        
        # Remove TRES parameters that are not part of V0036JobProperties
        job_params_clean = {k: v for k, v in job_params.items() 
                          if k not in ['tres_per_job', 'tres_per_node', 'tres_per_socket', 'tres_per_task']}
        
        # Set current working directory if not specified
        if 'current_working_directory' not in job_params_clean:
            job_params_clean['current_working_directory'] = os.getcwd()
        
        # Create job properties
        job_props = V0036JobProperties(**job_params_clean)
        
        # Create job submission
        job_submission = V0036JobSubmission(
            script=script_content,
            job=job_props
        )
        
        if return_curl:
            # TODO: Implement curl command generation
            raise NotImplementedError("Curl command generation not yet implemented")
            
        # Submit job
        return self.slurm_api.slurmctld_submit_job(job_submission)
    
    def get_jobs(
        self,
        return_curl: bool = False
    ) -> Union[V0036JobsResponse, str]:
        """Get list of jobs
        
        Args:
            return_curl: If True, return curl command instead of fetching
            
        Returns:
            V0036JobsResponse or curl command if return_curl=True
        """
        if return_curl:
            # TODO: Implement curl command generation
            raise NotImplementedError("Curl command generation not yet implemented")
            
        return self.slurm_api.slurmctld_get_jobs()
    
    def get_job(
        self,
        job_id: str,
        return_curl: bool = False
    ) -> Union[V0036JobsResponse, str]:
        """Get information about a specific job
        
        Args:
            job_id: Job ID to query
            return_curl: If True, return curl command instead of fetching
            
        Returns:
            V0036JobsResponse or curl command if return_curl=True
        """
        if return_curl:
            # TODO: Implement curl command generation
            raise NotImplementedError("Curl command generation not yet implemented")
            
        return self.slurm_api.slurmctld_get_job(job_id)
    
    def cancel_job(
        self,
        job_id: str,
        signal: str = 'SIGTERM',
        return_curl: bool = False
    ) -> None:
        """Cancel a job
        
        Args:
            job_id: Job ID to cancel
            signal: Signal to send (default: SIGTERM)
            return_curl: If True, return curl command instead of cancelling
            
        Returns:
            None
        """
        if return_curl:
            # TODO: Implement curl command generation
            raise NotImplementedError("Curl command generation not yet implemented")
            
        # Convert signal to enum
        signal_enum = V0036Signal(signal)
            
        return self.slurm_api.slurmctld_cancel_job(job_id, signal=signal_enum)

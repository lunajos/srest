"""Partition information and management client using swagger-generated models"""

from typing import Optional, Union
from swagger_client.models import V0036PartitionsResponse
from .base import BaseClient

class PartitionClient(BaseClient):
    """Client for partition-related operations"""
    
    def get_partitions(
        self,
        partition_name: Optional[str] = None,
        return_curl: bool = False
    ) -> Union[V0036PartitionsResponse, str]:
        """Get partition information
        
        Args:
            partition_name: Optional partition name to filter
            return_curl: If True, return curl command instead of fetching
            
        Returns:
            V0036PartitionsResponse or curl command if return_curl=True
        """
        if return_curl:
            # TODO: Implement curl command generation
            raise NotImplementedError("Curl command generation not yet implemented")
            
        return self.slurm_api.slurm_v0036_partitions_get(partition_name)
        
    def get_partition(
        self,
        partition_name: str,
        return_curl: bool = False
    ) -> Union[V0036PartitionsResponse, str]:
        """Get information about a specific partition
        
        Args:
            partition_name: Partition name to query
            return_curl: If True, return curl command instead of fetching
            
        Returns:
            V0036PartitionsResponse or curl command if return_curl=True
        """
        if return_curl:
            # TODO: Implement curl command generation
            raise NotImplementedError("Curl command generation not yet implemented")
            
        return self.slurm_api.slurm_v0036_partition_get(partition_name)

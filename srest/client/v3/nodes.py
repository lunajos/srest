"""Node information and management client using swagger-generated models"""

from typing import Optional, Union
from swagger_client.models import V0036NodesResponse
from .base import BaseClient

class NodeClient(BaseClient):
    """Client for node-related operations"""
    
    def get_nodes(
        self,
        node_name: Optional[str] = None,
        return_curl: bool = False
    ) -> Union[V0036NodesResponse, str]:
        """Get node information
        
        Args:
            node_name: Optional node name to filter
            return_curl: If True, return curl command instead of fetching
            
        Returns:
            V0036NodesResponse or curl command if return_curl=True
        """
        if return_curl:
            # TODO: Implement curl command generation
            raise NotImplementedError("Curl command generation not yet implemented")
            
        return self.slurm_api.slurmctld_get_nodes()
        
    def get_node(
        self,
        node_name: str,
        return_curl: bool = False
    ) -> Union[V0036NodesResponse, str]:
        """Get information about a specific node
        
        Args:
            node_name: Node name to query
            return_curl: If True, return curl command instead of fetching
            
        Returns:
            V0036NodesResponse or curl command if return_curl=True
        """
        if return_curl:
            # TODO: Implement curl command generation
            raise NotImplementedError("Curl command generation not yet implemented")
            
        return self.slurm_api.slurmctld_get_node(node_name)

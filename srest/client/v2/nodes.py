"""Node management client"""
from typing import Dict, Any, Optional, Union, List
from dataclasses import dataclass
from .base import BaseClient
from .models import SlurmMeta, SlurmResponse

@dataclass
class NodeInfo:
    """Node information"""
    name: str
    state: List[str]  # API returns state as a list
    partitions: List[str]
    # Required fields with defaults
    address: str = ''
    architecture: str = ''
    boards: int = 0
    cpus: int = 0
    hostname: str = ''
    port: int = 0
    real_memory: int = 0
    tres: str = ''
    version: str = ''
    # Optional fields
    alloc_cpus: int = 0
    alloc_idle_cpus: int = 0
    alloc_memory: int = 0
    boot_time: Optional[Dict[str, Any]] = None
    comment: str = ''
    cpu_load: int = 0
    features: List[str] = None
    gres: str = ''
    gres_used: str = ''
    last_busy: Optional[Dict[str, Any]] = None
    operating_system: str = ''
    reason: str = ''
    slurmd_start_time: Optional[Dict[str, Any]] = None
    
    def __init__(self, **data):
        # Convert lists
        self.state = data.pop('state', [])
        self.partitions = data.pop('partitions', [])
        self.features = data.pop('features', [])
        
        # Set all other fields
        for field in self.__dataclass_fields__:
            if field not in ['state', 'partitions', 'features']:
                setattr(self, field, data.get(field, self.__dataclass_fields__[field].default))

@dataclass
class NodeResponse(SlurmResponse):
    """Response for node queries"""
    nodes: List[NodeInfo] = None  # Make nodes optional to match parent class pattern
    
    def __init__(self, **data):
        # Extract nodes before passing to parent
        nodes_data = data.pop('nodes', [])
        super().__init__(**data)
        # Convert raw node data to NodeInfo objects
        self.nodes = [NodeInfo(**node) for node in nodes_data]

class NodeClient(BaseClient):
    """Client for node-related operations"""
    
    def get_nodes(self, return_curl: bool = False) -> Union[NodeResponse, str]:
        """Get list of nodes"""
        return self._make_request(
            method='GET',
            endpoint='slurm/v0.0.42/nodes',
            response_type=NodeResponse,
            return_curl=return_curl
        )
    
    def get_node(self, node_name: str, return_curl: bool = False) -> Union[NodeResponse, str]:
        """Get information about a specific node"""
        return self._make_request(
            method='GET',
            endpoint=f'slurm/v0.0.42/node/{node_name}',
            response_type=NodeResponse,
            return_curl=return_curl
        )

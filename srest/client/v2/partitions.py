"""Partition management client"""
from typing import Dict, Any, Optional, Union, List
from dataclasses import dataclass
from .base import BaseClient
from .models import SlurmMeta, SlurmResponse

@dataclass
class PartitionInfo:
    """Partition information"""
    name: str
    nodes: Optional[Dict[str, Any]] = None
    flags: Optional[Dict[str, Any]] = None
    defaults: Optional[Dict[str, Any]] = None
    maximums: Optional[Dict[str, Any]] = None
    minimums: Optional[Dict[str, Any]] = None
    cpus: Optional[Dict[str, Any]] = None
    tres: Optional[Dict[str, Any]] = None
    accounts: Optional[Dict[str, Any]] = None
    groups: Optional[Dict[str, Any]] = None
    qos: Optional[Dict[str, Any]] = None
    timeouts: Optional[Dict[str, Any]] = None
    priority: Optional[Dict[str, Any]] = None
    cluster: Optional[str] = None
    alternate: Optional[str] = None
    node_sets: Optional[str] = None
    grace_time: Optional[int] = None
    
    def __init__(self, **data):
        # Initialize with default values
        for field in self.__dataclass_fields__:
            setattr(self, field, None)
        # Update with provided data
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)
                
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            field: getattr(self, field)
            for field in self.__dataclass_fields__
            if getattr(self, field) is not None
        }

@dataclass
class PartitionResponse(SlurmResponse):
    """Response for partition queries"""
    partitions: List[PartitionInfo] = None
    last_update: Optional[int] = None
    
    def __init__(self, **data):
        # Initialize parent
        super().__init__(**data)
        
        # Convert partition data to PartitionInfo objects
        partitions_data = data.get('partitions', [])
        self.partitions = [PartitionInfo(**p) for p in partitions_data]
        self.last_update = data.get('last_update')
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        result = super().to_dict()
        result.update({
            'partitions': [p.to_dict() for p in self.partitions] if self.partitions else [],
            'last_update': self.last_update
        })
        return result

class PartitionClient(BaseClient):
    """Client for partition-related operations"""
    
    def get_partitions(self, return_curl: bool = False) -> Union[PartitionResponse, str]:
        """Get list of partitions"""
        return self._make_request(
            method='GET',
            endpoint='/slurm/v0.0.42/partitions',
            response_type=PartitionResponse,
            return_curl=return_curl
        )
    
    def get_partition(self, partition_name: str, return_curl: bool = False) -> Union[PartitionResponse, str]:
        """Get information about a specific partition"""
        return self._make_request(
            method='GET',
            endpoint=f'/slurm/v0.0.42/partition/{partition_name}',
            response_type=PartitionResponse,
            return_curl=return_curl
        )

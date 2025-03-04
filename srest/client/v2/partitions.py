"""Partition management client"""
from typing import Dict, Any, Optional, Union, List
from dataclasses import dataclass
from .base import BaseClient
from .models import SlurmMeta

@dataclass
class PartitionInfo:
    """Partition information"""
    name: str
    nodes: Dict[str, Any]
    partition: Dict[str, Any]
    defaults: Dict[str, Any]
    maximums: Dict[str, Any]
    minimums: Dict[str, Any]
    cpus: Dict[str, Any]
    tres: Dict[str, Any]
    accounts: Dict[str, Any] = None
    groups: Dict[str, Any] = None
    qos: Dict[str, Any] = None
    timeouts: Dict[str, Any] = None
    priority: Dict[str, Any] = None
    cluster: str = ''
    alternate: str = ''
    node_sets: str = ''
    grace_time: int = 0
    
    def __init__(self, **data):
        # Set all fields from data
        for field in self.__dataclass_fields__:
            setattr(self, field, data.get(field))

@dataclass
class PartitionResponse:
    """Response for partition queries"""
    meta: SlurmMeta
    partitions: List[PartitionInfo]
    errors: Optional[List[Dict[str, Any]]] = None
    warnings: Optional[List[Dict[str, Any]]] = None

class PartitionClient(BaseClient):
    """Client for partition-related operations"""
    
    def get_partitions(self, return_curl: bool = False) -> Union[PartitionResponse, str]:
        """Get list of partitions"""
        return self._make_request(
            method='GET',
            endpoint='/partitions',
            response_type=PartitionResponse,
            return_curl=return_curl
        )
    
    def get_partition(self, partition_name: str, return_curl: bool = False) -> Union[PartitionResponse, str]:
        """Get information about a specific partition"""
        return self._make_request(
            method='GET',
            endpoint=f'/partition/{partition_name}',
            response_type=PartitionResponse,
            return_curl=return_curl
        )

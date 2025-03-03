"""Partition management client"""
from typing import Dict, Any, Optional, Union, List
from dataclasses import dataclass
from .base import BaseClient
from .models import SlurmMeta

@dataclass
class PartitionInfo:
    """Partition information"""
    name: str
    nodes: str
    total_nodes: int
    total_cpus: int
    default_time_limit: Optional[int] = None
    max_time_limit: Optional[int] = None
    default_memory_per_node: Optional[int] = None
    max_memory_per_node: Optional[int] = None
    allowed_accounts: Optional[List[str]] = None
    allowed_qos: Optional[List[str]] = None
    qos_char: Optional[str] = None
    state: Optional[str] = None
    flags: Optional[List[str]] = None

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

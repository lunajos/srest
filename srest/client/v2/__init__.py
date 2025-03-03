"""Slurm REST API client v2 based on OpenAPI 3.0.3 specification"""
from .base import BaseClient, ClientConfig
from .jobs import JobClient
from .nodes import NodeClient
from .partitions import PartitionClient
from .reservations import ReservationClient
from .diag import DiagClient
from .accounts import AccountClient

from .models import (
    SlurmError,
    SlurmMeta,
    SlurmResponse,
    # Job models
    JobSubmitRequest,
    JobSubmitResponse,
    JobInfo,
    JobResponse,
    JobState,
)

from .nodes import NodeInfo, NodeResponse
from .partitions import PartitionInfo, PartitionResponse
from .reservations import (
    ReservationInfo,
    ReservationResponse,
    ReservationCreateRequest
)
from .diag import DiagInfo, DiagResponse, PingResponse
from .accounts import (
    AccountInfo,
    AccountResponse,
    AssociationInfo,
    AssociationResponse
)

__all__ = [
    # Base
    'BaseClient',
    'ClientConfig',
    'SlurmError',
    'SlurmMeta',
    'SlurmResponse',
    
    # Clients
    'JobClient',
    'NodeClient',
    'PartitionClient',
    'ReservationClient',
    'DiagClient',
    'AccountClient',
    
    # Job models
    'JobSubmitRequest',
    'JobSubmitResponse',
    'JobInfo',
    'JobResponse',
    'JobState',
    
    # Node models
    'NodeInfo',
    'NodeResponse',
    
    # Partition models
    'PartitionInfo',
    'PartitionResponse',
    
    # Reservation models
    'ReservationInfo',
    'ReservationResponse',
    'ReservationCreateRequest',
    
    # Diagnostic models
    'DiagInfo',
    'DiagResponse',
    'PingResponse',
    
    # Account models
    'AccountInfo',
    'AccountResponse',
    'AssociationInfo',
    'AssociationResponse'
]

"""Slurm REST API models based on OpenAPI 3.0.3 specification"""
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from enum import Enum

@dataclass
class SlurmError(Exception):
    """Error response from Slurm API"""
    error_code: Optional[int]
    message: str
    
    def __str__(self) -> str:
        return f"{self.message} (code={self.error_code})"

@dataclass
class SlurmMeta:
    """Metadata included in Slurm responses"""
    plugin: Dict[str, str] = None
    Slurm: str = None
    version: str = None
    
    def __init__(self, **data):
        # Set known fields
        self.plugin = data.get('plugin')
        self.Slurm = data.get('Slurm')
        self.version = data.get('version')
        # Ignore unknown fields

@dataclass
class SlurmResponse:
    """Base response structure for Slurm API endpoints"""
    errors: Optional[List[Dict[str, Any]]] = None
    warnings: Optional[List[Dict[str, Any]]] = None
    meta: Optional[SlurmMeta] = None
    
    def __init__(self, **data):
        # Convert meta if present
        meta_data = data.pop('meta', None)
        if meta_data:
            self.meta = SlurmMeta(**meta_data)
        
        # Set errors and warnings
        self.errors = data.pop('errors', None)
        self.warnings = data.pop('warnings', None)
        
        # Ignore any other fields

@dataclass
class JobSubmitRequest:
    """Job submission request structure"""
    script: str
    job: Optional[Dict[str, Any]] = None

@dataclass
class JobSubmitResponse:
    """Response structure for job submission"""
    meta: SlurmMeta
    job_id: int
    step_id: Optional[str] = None
    job_submit_user_msg: Optional[str] = None
    errors: Optional[List[Dict[str, Any]]] = None
    warnings: Optional[List[Dict[str, Any]]] = None

@dataclass
class JobInfo:
    """Information about a specific job"""
    account: Optional[str] = None
    comment: Optional[str] = None
    job_id: Optional[int] = None
    job_state: Optional[str] = None
    name: Optional[str] = None
    partition: Optional[str] = None
    time_limit: Optional[int] = None
    time_submit: Optional[int] = None
    working_directory: Optional[str] = None

@dataclass
class JobResponse:
    """Response structure for job queries"""
    meta: SlurmMeta
    jobs: List[JobInfo]
    errors: Optional[List[Dict[str, Any]]] = None
    warnings: Optional[List[Dict[str, Any]]] = None

class JobState(Enum):
    """Possible job states"""
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUSPENDED = "SUSPENDED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    FAILED = "FAILED"
    TIMEOUT = "TIMEOUT"
    NODE_FAIL = "NODE_FAIL"
    PREEMPTED = "PREEMPTED"
    BOOT_FAIL = "BOOT_FAIL"
    DEADLINE = "DEADLINE"
    OUT_OF_MEMORY = "OUT_OF_MEMORY"

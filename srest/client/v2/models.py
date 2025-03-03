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

    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary"""
        result = {}
        for field in self.__dataclass_fields__:
            value = getattr(self, field)
            if value is not None:
                result[field] = value
        return result

@dataclass
class SlurmResponse:
    """Base response structure for Slurm API endpoints"""
    errors: Optional[List[Dict[str, Any]]] = None
    warnings: Optional[List[Dict[str, Any]]] = None
    meta: Optional[SlurmMeta] = None
    
    def __init__(self, **data):
        # Convert meta if present
        meta_data = data.get('meta')
        if meta_data:
            self.meta = SlurmMeta(**meta_data)
        
        # Set errors and warnings
        self.errors = data.get('errors')
        self.warnings = data.get('warnings')
        
        # Ignore any other fields

    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary"""
        result = {}
        for field in self.__dataclass_fields__:
            value = getattr(self, field)
            if value is not None:
                if hasattr(value, 'to_dict'):
                    result[field] = value.to_dict()
                elif isinstance(value, list):
                    result[field] = [v.to_dict() if hasattr(v, 'to_dict') else v for v in value]
                else:
                    result[field] = value
        return result

@dataclass
class JobSubmitRequest:
    """Job submission request structure"""
    script: str
    job: Optional[Dict[str, Any]] = None

@dataclass
class JobSubmitResponse:
    """Response structure for job submission"""
    meta: Optional[SlurmMeta] = None
    job_id: Optional[int] = None
    step_id: Optional[str] = None
    job_submit_user_msg: Optional[str] = None
    errors: Optional[List[Dict[str, Any]]] = None
    warnings: Optional[List[Dict[str, Any]]] = None
    
    def __init__(self, **data):
        # Convert meta if present
        meta_data = data.pop('meta', None)
        if meta_data:
            self.meta = SlurmMeta(**meta_data)
        
        # Set other fields
        self.job_id = data.get('job_id')
        self.step_id = data.get('step_id')
        self.job_submit_user_msg = data.get('job_submit_user_msg')
        self.errors = data.get('errors')
        self.warnings = data.get('warnings')

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
class JobResponse(SlurmResponse):
    """Response structure for job queries"""
    jobs: List[Dict[str, Any]] = None
    
    def __init__(self, **data):
        # Initialize parent
        super().__init__(**data)
        
        # Set jobs
        self.jobs = data.get('jobs', [])

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

@dataclass
class LastUpdate:
    """Last update information"""
    set: bool
    infinite: bool
    number: int

@dataclass
class PartitionResponse(SlurmResponse):
    """Response structure for partition queries"""
    partitions: List[Dict[str, Any]] = None
    
    def __init__(self, **data):
        # Initialize parent
        super().__init__(**data)
        
        # Set partitions
        self.partitions = data.get('partitions', [])
        
        # Ignore last_update and other fields

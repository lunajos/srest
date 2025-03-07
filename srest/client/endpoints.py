from dataclasses import dataclass
from typing import Optional

@dataclass
class SlurmEndpoints:
    """Slurm REST API endpoint URLs following OpenAPI 3.0.3 specification"""
    
    base_url: str
    api_version: str
    
    def __post_init__(self):
        """Post-initialization processing"""
        self.base_url = self.base_url.rstrip('/')
    
    @property
    def base_api_url(self) -> str:
        """Get base API URL with version"""
        return f"{self.base_url}/slurm/{self.api_version}"
    
    # Job endpoints
    @property
    def jobs(self) -> str:
        """Jobs endpoint for listing and submitting jobs"""
        return f"{self.base_api_url}/jobs"
    
    def job(self, job_id: Optional[str] = None) -> str:
        """Job endpoint for specific job operations"""
        base = f"{self.base_api_url}/job"
        return f"{base}/{job_id}" if job_id else base
    
    @property
    def job_submit(self) -> str:
        """Job submission endpoint"""
        return f"{self.base_api_url}/jobs/submit"
    
    # Node endpoints
    @property
    def nodes(self) -> str:
        """Nodes endpoint for listing nodes"""
        return f"{self.base_api_url}/nodes"
    
    def node(self, node_name: str) -> str:
        """Node endpoint for specific node operations"""
        return f"{self.base_api_url}/node/{node_name}"
    
    # Partition endpoints
    @property
    def partitions(self) -> str:
        """Partitions endpoint for listing partitions"""
        return f"{self.base_api_url}/partitions"
    
    def partition(self, partition_name: str) -> str:
        """Partition endpoint for specific partition operations"""
        return f"{self.base_api_url}/partition/{partition_name}"
    
    # Reservation endpoints
    @property
    def reservations(self) -> str:
        """Reservations endpoint for listing reservations"""
        return f"{self.base_api_url}/reservations"
    
    def reservation(self, reservation_name: str) -> str:
        """Reservation endpoint for specific reservation operations"""
        return f"{self.base_api_url}/reservation/{reservation_name}"
    
    # Account endpoints
    @property
    def accounts(self) -> str:
        """Accounts endpoint for listing accounts"""
        return f"{self.base_api_url}/accounts"
    
    def account(self, account_name: str) -> str:
        """Account endpoint for specific account operations"""
        return f"{self.base_api_url}/account/{account_name}"
    
    # Association endpoints
    @property
    def associations(self) -> str:
        """Associations endpoint for listing user-account associations"""
        return f"{self.base_api_url}/associations"
    
    # Diagnostic endpoints
    @property
    def diag(self) -> str:
        """Diagnostics endpoint"""
        return f"{self.base_api_url}/diag"
    
    @property
    def ping(self) -> str:
        """Ping endpoint for controller status"""
        return f"{self.base_api_url}/ping"
    
    # License endpoints
    @property
    def licenses(self) -> str:
        """Licenses endpoint"""
        return f"{self.base_api_url}/licenses"
    
    # Share/fairshare endpoints
    @property
    def shares(self) -> str:
        """Shares endpoint for fairshare information"""
        return f"{self.base_api_url}/shares"
    
    # QOS endpoints
    @property
    def qos(self) -> str:
        """QOS endpoint for listing quality of service"""
        return f"{self.base_api_url}/qos"
        
    @property
    def accounts(self) -> str:
        """Accounts endpoint"""
        return f"{self.base_api_url}/accounts"
        
    @property
    def associations(self) -> str:
        """Associations endpoint"""
        return f"{self.base_api_url}/associations"
        
    @property
    def mcs(self) -> str:
        """MCS labels endpoint"""
        return f"{self.base_api_url}/mcs"

class SlurmEndpoints:
    """Slurm REST API endpoint URLs"""
    
    def __init__(self, base_url: str, api_version: str = 'v0.0.42'):
        """Initialize endpoints with base URL and API version"""
        self.base_url = base_url.rstrip('/')
        self.api_version = api_version
        
    @property
    def base_api_url(self) -> str:
        """Get base API URL with version"""
        return f"{self.base_url}/slurm/{self.api_version}"
    
    @property
    def jobs(self) -> str:
        """Jobs endpoint"""
        return f"{self.base_api_url}/jobs"
    
    @property
    def job_submit(self) -> str:
        """Job submission endpoint"""
        return f"{self.base_api_url}/job/submit"
    
    @property
    def nodes(self) -> str:
        """Nodes endpoint"""
        return f"{self.base_api_url}/nodes"
    
    @property
    def partitions(self) -> str:
        """Partitions endpoint"""
        return f"{self.base_api_url}/partitions"
    
    @property
    def reservations(self) -> str:
        """Reservations endpoint"""
        return f"{self.base_api_url}/reservations"
    
    @property
    def diag(self) -> str:
        """Diagnostics endpoint"""
        return f"{self.base_api_url}/diag"
        
    @property
    def licenses(self) -> str:
        """Licenses endpoint"""
        return f"{self.base_api_url}/licenses"
    
    @property
    def ping(self) -> str:
        """Ping endpoint"""
        return f"{self.base_api_url}/ping"
        
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

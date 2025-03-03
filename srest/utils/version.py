"""Version management utilities for srest."""
import re
import requests
from typing import Tuple, Optional

def parse_slurm_version(version_str: str) -> Tuple[int, int, int]:
    """Parse Slurm version string into components."""
    match = re.match(r'slurm (\d+)\.(\d+)\.(\d+)', version_str)
    if not match:
        raise ValueError(f"Invalid Slurm version string: {version_str}")
    return tuple(map(int, match.groups()))

def get_compatible_api_version(slurm_version: Tuple[int, int, int]) -> str:
    """Get compatible API version for Slurm version."""
    # Map Slurm versions to API versions
    version_map = {
        (24, 11): "v0.0.42",
        (23, 11): "v0.0.39",
        (23, 2): "v0.0.38",
        # Add more mappings as needed
    }
    
    for (major, minor), api_version in version_map.items():
        if (slurm_version[0], slurm_version[1]) == (major, minor):
            return api_version
    
    raise ValueError(f"No known API version for Slurm {'.'.join(map(str, slurm_version))}")

def verify_api_endpoint(url: str, api_version: str) -> bool:
    """Verify if the API endpoint is accessible with the given version."""
    try:
        response = requests.head(f"{url}/slurm/{api_version}/nodes")
        return response.status_code != 404
    except requests.RequestException:
        return False

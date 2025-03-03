"""V3 Client package for Slurm REST API

This version uses the swagger-generated client for more accurate API representation.
"""

from .jobs import JobClient
from .base import BaseClient

__all__ = ['JobClient', 'BaseClient']

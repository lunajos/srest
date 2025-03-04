"""Slurm REST API Client"""
from .client import SlurmRESTClient, get_client
from .auth.status import AuthStatus

__version__ = '0.1.0'
__all__ = ['SlurmRESTClient', 'get_client', 'AuthStatus']
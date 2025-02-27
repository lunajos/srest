"""Slurm REST API client"""
from .client import get_client, SlurmClient, SlurmError

__all__ = ['get_client', 'SlurmClient', 'SlurmError']
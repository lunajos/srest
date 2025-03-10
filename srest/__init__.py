"""Slurm REST API Client"""
from .client import SlurmRESTClient, get_client
from .auth.status import AuthStatus
from .cli import cli

__version__ = '0.1.0'
__all__ = ['SlurmRESTClient', 'get_client', 'AuthStatus', 'cli']

def main():
    """Entry point for the CLI"""
    cli()
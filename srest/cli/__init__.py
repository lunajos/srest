"""Command-line interface for Slurm REST API client"""
import click
from .commands.auth import auth_group
from .commands.config import config_group
from .commands.job import jobs_group
from .commands.nodes import nodes_group
from .commands.partitions import partitions_group
from .commands.diag import diag_group
from .commands.licenses import licenses_group

@click.group()
def cli():
    """Slurm REST API client"""
    pass

def init_cli():
    """Initialize CLI with all commands"""
    cli.add_command(auth_group)
    cli.add_command(config_group)
    cli.add_command(jobs_group)
    cli.add_command(nodes_group)
    cli.add_command(partitions_group)
    cli.add_command(diag_group)
    cli.add_command(licenses_group)

    
    return cli

__all__ = ['cli', 'init_cli']

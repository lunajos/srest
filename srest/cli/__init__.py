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
@click.version_option()
def cli():
    """Slurm REST API client for v0.0.42"""
    pass

# Register commands that match the Slurm REST API structure
cli.add_command(auth_group)      # Authentication (JWT, token, user)
cli.add_command(config_group)    # Configuration management
cli.add_command(jobs_group)      # Job submission and control
cli.add_command(nodes_group)     # Node information
cli.add_command(partitions_group)  # Partition information
cli.add_command(diag_group)      # Diagnostics
cli.add_command(licenses_group)   # License information

if __name__ == '__main__':
    cli()

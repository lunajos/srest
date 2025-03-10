"""CLI commands package for Slurm REST API v0.0.42"""
import click
from .auth import auth_group     # Authentication (JWT, token, user)
from .config import config_group # Configuration management
from .job import jobs_group      # Job submission and control (POST /slurm/v0.0.42/job/submit)
from .nodes import nodes_group   # Node information (GET /slurm/v0.0.42/nodes)
from .partitions import partitions_group  # Partition info (GET /slurm/v0.0.42/partitions)
from .diag import diag_group    # Diagnostics (GET /slurm/v0.0.42/diag)
from .licenses import licenses_group  # License info (GET /slurm/v0.0.42/licenses)
from .reservations import reservations_group
from .version import version_group

@click.group()
@click.version_option()
def cli():
    """Slurm REST API client for v0.0.42

    Provides CLI access to Slurm's REST API endpoints including:
    - Job submission and management
    - Node and partition information
    - Authentication and configuration
    - System diagnostics and licenses
    """
    pass

# Register command groups that map to API endpoints
cli.add_command(auth_group)
cli.add_command(config_group)
cli.add_command(jobs_group)
cli.add_command(nodes_group)
cli.add_command(partitions_group)
cli.add_command(diag_group)
cli.add_command(licenses_group)
cli.add_command(reservations_group)
cli.add_command(version_group)

def main():
    """Entry point for the CLI"""
    cli()

"""Main CLI entry point"""
import click
from .commands import (
    jobs_group,
    nodes_group,
    partitions_group,
    reservations_group,
    licenses_group,
    diag_group,
    accounts_group,
    mcs_group,
    config_group,
    auth_group
)

@click.group()
def cli():
    """Slurm REST API client"""
    pass

# Add command groups
cli.add_command(jobs_group)
cli.add_command(nodes_group)
cli.add_command(partitions_group)
cli.add_command(reservations_group)
cli.add_command(licenses_group)
cli.add_command(diag_group)
cli.add_command(accounts_group)
cli.add_command(mcs_group)
cli.add_command(config_group)
cli.add_command(auth_group)

if __name__ == '__main__':
    cli()

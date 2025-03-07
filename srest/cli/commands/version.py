"""Version management commands"""
import click
from ...config import Config

AVAILABLE_VERSIONS = [
    'v0.0.36',  # Slurm 21.08
    'v0.0.37',  # Slurm 22.05
    'v0.0.38',  # Slurm 22.05.2
    'v0.0.39',  # Slurm 22.05.3
    'v0.0.40',  # Slurm 23.02
    'v0.0.41',  # Slurm 23.11
    'v0.0.42',  # Slurm 24.11.2
]

@click.group(name='version')
def version_group():
    """API version management commands"""
    pass

@version_group.command('list')
def list_versions():
    """List available API versions"""
    config = Config()
    current = config.get('api.version', 'v0.0.42')
    
    click.echo("Available API versions:")
    for version in AVAILABLE_VERSIONS:
        if version == current:
            click.echo(f"* {version} (current)")
        else:
            click.echo(f"  {version}")

@version_group.command('show')
def show_version():
    """Show current API version"""
    config = Config()
    version = config.get('api.version', 'v0.0.42')
    click.echo(f"Current API version: {version}")

@version_group.command('set')
@click.argument('version')
def set_version(version: str):
    """Set API version to use"""
    if version not in AVAILABLE_VERSIONS:
        versions_str = '\n'.join(f"  {v}" for v in AVAILABLE_VERSIONS)
        raise click.BadParameter(
            f"Invalid version. Available versions:\n{versions_str}"
        )
    
    config = Config()
    config.set('api.version', version)
    config.save()
    click.echo(f"API version set to: {version}")

"""Configuration management commands"""
import click
import json
from ...config import Config
from ...parsers.submit import OutputFormat

@click.group(name='config')
def config_group():
    """Configuration management commands"""
    pass

@config_group.command('set')
@click.argument('key')
@click.argument('value')
def set_config(key: str, value: str):
    """Set configuration value"""
    config = Config()
    config.set(key, value)
    config.save()
    click.echo(f"Set {key} = {value}")

@config_group.command('get')
@click.argument('key')
@click.option('--format', type=click.Choice([f.value for f in OutputFormat]),
              default=OutputFormat.BASIC.value, help='Output format')
def get_config(key: str, format: str):
    """Get configuration value"""
    config = Config()
    value = config.get(key)
    
    if format == OutputFormat.JSON.value:
        click.echo(json.dumps({key: value}, indent=2))
    else:
        click.echo(f"{key} = {value}")

@config_group.command('list')
@click.option('--format', type=click.Choice([f.value for f in OutputFormat]),
              default=OutputFormat.BASIC.value, help='Output format')
def list_config(format: str):
    """List all configuration values"""
    config = Config()
    values = config.get_all()
    
    if format == OutputFormat.JSON.value:
        click.echo(json.dumps(values, indent=2))
    else:
        for key, value in values.items():
            click.echo(f"{key} = {value}")

@config_group.command('delete')
@click.argument('key')
def delete_config(key: str):
    """Delete configuration value"""
    config = Config()
    config.delete(key)
    config.save()
    click.echo(f"Deleted {key}")

@config_group.command('list-api-versions')
@click.option('--format', type=click.Choice([f.value for f in OutputFormat]),
              default=OutputFormat.BASIC.value, help='Output format')
def list_api_versions(format: str):
    """List all supported API versions from server.
    
    Queries the OpenAPI spec from the server to determine all supported
    API versions (e.g., v0.0.40, v0.0.41, v0.0.42). The versions are
    extracted from the API paths in the OpenAPI spec.
    """
    from ...client import get_client
    
    try:
        client = get_client()
        versions = client.diag.get_versions(all_versions=True)
        
        if not versions:
            raise click.ClickException("No API versions detected")
            
        if format == OutputFormat.JSON.value:
            click.echo(json.dumps({"versions": versions}, indent=2))
        else:
            click.echo("Supported API versions:")
            for version in versions:
                click.echo(f"  {version}")
    except Exception as e:
        raise click.ClickException(str(e))

@config_group.command('detect-api-version')
@click.option('--set/--no-set', default=True, help='Set detected version in config')
def detect_api_version(set: bool):
    """Detect API version from server and optionally set it in config.
    
    Queries the OpenAPI spec from the server to determine the latest supported
    API version (e.g., v0.0.42). The version is extracted from the API paths
    in the OpenAPI spec.
    
    If --set is specified (default), the detected version will be saved to
    the config as slurm.api_version.
    """
    from ...client import get_client
    
    try:
        client = get_client()
        version = client.diag.get_versions()
        
        if not version:
            raise click.ClickException("No API version detected")
            
        click.echo(f"Detected API version: {version}")
        
        if set:
            config = Config()
            config.set('slurm.api_version', version)
            click.echo(f"Set slurm.api_version = {version}")
    except Exception as e:
        raise click.ClickException(str(e))

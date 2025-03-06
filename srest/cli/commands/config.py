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

@config_group.command('detect-api-version')
@click.option('--set/--no-set', default=True, help='Set detected version in config')
def detect_api_version(set: bool):
    """Detect API version from server and optionally set it in config"""
    from ...client import get_client
    
    try:
        client = get_client()
        spec = client.diag.get_versions()
        
        if not isinstance(spec, dict):
            raise click.ClickException("Invalid OpenAPI specification format")
            
        info = spec.get('info', {})
        version = info.get('version')
        
        if not version:
            raise click.ClickException("No version found in OpenAPI specification")
            
        click.echo(f"Detected API version: {version}")
        
        if set:
            config = Config()
            config.set('slurm.api_version', version)
            click.echo(f"Set slurm.api_version = {version}")
    except Exception as e:
        raise click.ClickException(str(e))

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

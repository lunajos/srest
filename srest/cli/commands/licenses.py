import click
import json
from ...client import get_client
from ...parsers.submit import OutputFormat
from ..utils import print_table

@click.group(name='licenses')
def licenses_group():
    """License management commands"""
    pass

@licenses_group.command('list')
@click.option('--format', type=click.Choice([f.value for f in OutputFormat]),
              default=OutputFormat.BASIC.value, help='Output format')
def list_licenses(format: str):
    """List license information"""
    client = get_client()
    
    try:
        result = client.list_licenses()
        if format == OutputFormat.JSON.value:
            click.echo(json.dumps(result, indent=2))
        else:
            licenses = result.get('licenses', [])
            if not licenses:
                click.echo("No licenses found")
                return
                
            headers = ['NAME', 'TOTAL', 'USED', 'FREE', 'REMOTE']
            rows = []
            
            for lic in licenses:
                rows.append([
                    lic.get('name', ''),
                    str(lic.get('total', 0)),
                    str(lic.get('used', 0)),
                    str(lic.get('total', 0) - lic.get('used', 0)),
                    'yes' if lic.get('remote', False) else 'no'
                ])
            
            print_table(headers, rows)
    except Exception as e:
        raise click.ClickException(str(e))

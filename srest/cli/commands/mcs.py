"""MCS label management commands"""
import click
import json
from ...client import get_client
from ...parsers.submit import OutputFormat
from ..utils import print_table

@click.group(name='mcs')
def mcs_group():
    """MCS label management commands"""
    pass

@mcs_group.command('list')
@click.option('--format', type=click.Choice([f.value for f in OutputFormat]),
              default=OutputFormat.BASIC.value, help='Output format')
@click.option('--type', help='Filter by label type')
@click.option('--curl', is_flag=True, help='Show curl command instead of executing')
def list_labels(format: str, type: str, curl: bool):
    """List MCS labels"""
    client = get_client()
    
    try:
        result = client.list_mcs_labels(type=type, return_curl=curl)
        if curl:
            click.echo(result['curl_command'])
            return
        if format == OutputFormat.JSON.value:
            click.echo(json.dumps(result, indent=2))
        else:
            labels = result.get('labels', [])
            if not labels:
                click.echo("No MCS labels found")
                return
                
            headers = ['NAME', 'TYPE', 'PRIORITY', 'ALLOWED_ACCOUNTS']
            rows = []
            
            for label in labels:
                rows.append([
                    label.get('name', ''),
                    label.get('type', ''),
                    str(label.get('priority', 0)),
                    ','.join(label.get('allowed_accounts', []))
                ])
            
            print_table(headers, rows)
    except Exception as e:
        raise click.ClickException(str(e))

@mcs_group.command('show')
@click.argument('label')
@click.option('--format', type=click.Choice([f.value for f in OutputFormat]),
              default=OutputFormat.BASIC.value, help='Output format')
@click.option('--curl', is_flag=True, help='Show curl command instead of executing')
def show_label(label: str, format: str, curl: bool):
    """Show MCS label details"""
    client = get_client()
    
    try:
        result = client.get_mcs_label(label, return_curl=curl)
        if curl:
            click.echo(result['curl_command'])
            return
        if format == OutputFormat.JSON.value:
            click.echo(json.dumps(result, indent=2))
        else:
            label_info = result.get('label', {})
            if not label_info:
                raise click.ClickException(f"MCS label not found: {label}")
            
            click.echo(f"Label: {label_info['name']}")
            click.echo(f"Type: {label_info.get('type', 'N/A')}")
            click.echo(f"Priority: {label_info.get('priority', 0)}")
            click.echo("\nAllowed Accounts:")
            for account in label_info.get('allowed_accounts', []):
                click.echo(f"  - {account}")
            click.echo("\nAllowed Users:")
            for user in label_info.get('allowed_users', []):
                click.echo(f"  - {user}")
    except Exception as e:
        raise click.ClickException(str(e))

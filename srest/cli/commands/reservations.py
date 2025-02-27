import click
import json
from typing import Optional
from ...client import get_client
from ...parsers.submit import OutputFormat
from ..utils import print_table, format_time

@click.group(name='reservations')
def reservations_group():
    """Reservation management commands"""
    pass

@reservations_group.command('list')
@click.option('--format', type=click.Choice([f.value for f in OutputFormat]),
              default=OutputFormat.BASIC.value, help='Output format')
def list_reservations(format: str):
    """List reservations"""
    client = get_client()
    
    try:
        result = client.list_reservations()
        if format == OutputFormat.JSON.value:
            click.echo(json.dumps(result, indent=2))
        else:
            reservations = result.get('reservations', [])
            if not reservations:
                click.echo("No reservations found")
                return
                
            headers = ['NAME', 'START', 'END', 'DURATION', 'NODES', 'STATE', 'FLAGS']
            rows = []
            
            for res in reservations:
                rows.append([
                    res.get('name', ''),
                    res.get('start_time', ''),
                    res.get('end_time', ''),
                    format_time(res.get('duration_minutes', 0)),
                    res.get('node_list', ''),
                    res.get('state', ''),
                    ','.join(res.get('flags', []))
                ])
            
            print_table(headers, rows)
    except Exception as e:
        raise click.ClickException(str(e))

@reservations_group.command('create')
@click.option('--name', required=True, help='Reservation name')
@click.option('--start-time', help='Start time (YYYY-MM-DD[THH:MM:SS])')
@click.option('--duration', help='Duration in minutes')
@click.option('--nodes', help='Node list or count')
@click.option('--users', help='Comma-separated list of users')
@click.option('--accounts', help='Comma-separated list of accounts')
@click.option('--flags', help='Comma-separated list of flags')
def create_reservation(name: str, start_time: Optional[str], duration: Optional[str],
                      nodes: Optional[str], users: Optional[str], accounts: Optional[str],
                      flags: Optional[str]):
    """Create a reservation"""
    client = get_client()
    
    params = {'name': name}
    if start_time:
        params['start_time'] = start_time
    if duration:
        params['duration'] = int(duration)
    if nodes:
        params['nodes'] = nodes
    if users:
        params['users'] = users.split(',')
    if accounts:
        params['accounts'] = accounts.split(',')
    if flags:
        params['flags'] = flags.split(',')
    
    try:
        result = client.create_reservation(params)
        click.echo(f"Created reservation: {result['name']}")
    except Exception as e:
        raise click.ClickException(str(e))

@reservations_group.command('delete')
@click.argument('name')
def delete_reservation(name: str):
    """Delete a reservation"""
    client = get_client()
    try:
        client.delete_reservation(name)
        click.echo(f"Deleted reservation: {name}")
    except Exception as e:
        raise click.ClickException(str(e))

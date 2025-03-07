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
@click.option('--curl', is_flag=True, help='Output curl command with JWT and headers')
def list_reservations(format: str, curl: bool = False):
    """List reservations"""
    try:
        client = get_client().reservation
    except ValueError as e:
        if "Not logged in" in str(e):
            click.echo("Session expired. Please run 'srest auth login' to log in again.")
            return
        raise click.ClickException(str(e))

    try:
        if curl:
            curl_command = client.get_reservations(return_curl=True)
            click.echo('# Run this command to list reservations using curl:')
            click.echo(curl_command)
            return
            
        result = client.get_reservations()
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
@click.option('--curl', is_flag=True, help='Output curl command with JWT and headers')
def create_reservation(name: str, start_time: Optional[str], duration: Optional[str],
                      nodes: Optional[str], users: Optional[str], accounts: Optional[str],
                      flags: Optional[str], curl: bool = False):
    """Create a reservation"""
    try:
        client = get_client().reservation
    except ValueError as e:
        if "Not logged in" in str(e):
            click.echo("Session expired. Please run 'srest auth login' to log in again.")
            return
        raise click.ClickException(str(e))

    # Create reservation request
    from ...client.v2.reservations import ReservationCreateRequest
    
    request = ReservationCreateRequest(
        name=name,
        start_time=start_time or 'now',  # Default to now if not specified
        duration=duration or '60',  # Default to 60 minutes if not specified
        nodes=nodes,
        users=users.split(',') if users else None,
        accounts=accounts.split(',') if accounts else None,
        flags=flags.split(',') if flags else None
    )
    
    try:
        if curl:
            curl_command = client.create_reservation(request, return_curl=True)
            click.echo('# Run this command to create reservation using curl:')
            click.echo(curl_command)
            return
            
        result = client.create_reservation(request)
        click.echo(f"Created reservation: {result['name']}")
    except Exception as e:
        raise click.ClickException(str(e))

@reservations_group.command('delete')
@click.argument('name')
@click.option('--curl', is_flag=True, help='Output curl command with JWT and headers')
def delete_reservation(name: str, curl: bool = False):
    """Delete a reservation"""
    try:
        client = get_client().reservation
    except ValueError as e:
        if "Not logged in" in str(e):
            click.echo("Session expired. Please run 'srest auth login' to log in again.")
            return
        raise click.ClickException(str(e))

    try:
        if curl:
            curl_command = client.delete_reservation(name, return_curl=True)
            click.echo('# Run this command to delete reservation using curl:')
            click.echo(curl_command)
            return
            
        client.delete_reservation(name)
        click.echo(f"Deleted reservation: {name}")
    except Exception as e:
        raise click.ClickException(str(e))

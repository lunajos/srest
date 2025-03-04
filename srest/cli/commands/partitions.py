import click
import json
from ...client import get_client
from ...parsers.submit import OutputFormat
from ..utils import print_table, format_time, format_memory

@click.group(name='partitions')
def partitions_group():
    """Partition management commands"""
    pass

@partitions_group.command('list')
@click.option('--format', type=click.Choice([f.value for f in OutputFormat]),
              default=OutputFormat.BASIC.value, help='Output format')
def list_partitions(format: str):
    """List partitions"""
    try:
        try:
            client = get_client().partition
        except ValueError as e:
            if "Not logged in" in str(e):
                click.echo("Session expired. Please run 'srest auth login' to log in again.")
                return
            raise click.ClickException(str(e))
            
        result = client.get_partitions()
        if format == OutputFormat.JSON.value:
            click.echo(json.dumps(result.to_dict(), indent=2))
        else:
            partitions = result.partitions or []
            if not partitions:
                click.echo("No partitions found")
                return
                
            headers = ['NAME', 'STATE', 'NODES', 'DEFAULT']
            rows = []
            
            for partition in partitions:
                state = partition.partition.state[0] if partition.partition and partition.partition.state else ''
                rows.append([
                    partition.name or '',
                    state,
                    str(partition.nodes.total if partition.nodes else 0),
                    'yes' if partition.defaults and partition.defaults.job else 'no'
                ])
            
            print_table(headers, rows)
    except Exception as e:
        if hasattr(e, 'status') and e.status in [401, 511]:
            click.echo("Session expired. Please run 'srest auth login' to log in again.")
            return
        raise click.ClickException(str(e))
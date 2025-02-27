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
    client = get_client()
    
    try:
        result = client.list_partitions()
        if format == OutputFormat.JSON.value:
            click.echo(json.dumps(result, indent=2))
        else:
            partitions = result.get('partitions', [])
            if not partitions:
                click.echo("No partitions found")
                return
                
            headers = ['NAME', 'STATE', 'NODES', 'TIMELIMIT', 'MEMORY', 'DEFAULT']
            rows = []
            
            for partition in partitions:
                rows.append([
                    partition.get('name', ''),
                    partition.get('state', ''),
                    str(partition.get('total_nodes', '')),
                    format_time(partition.get('max_time_minutes', 0)),
                    format_memory(partition.get('max_memory_per_node', 0)),
                    'yes' if partition.get('flags', {}).get('default', False) else 'no'
                ])
            
            print_table(headers, rows)
    except Exception as e:
        raise click.ClickException(str(e))
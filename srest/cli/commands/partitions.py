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
@click.option('--curl', is_flag=True, help='Output curl command with JWT and headers')
def list_partitions(format: str, curl: bool):
    """List partitions"""
    try:
        try:
            client = get_client().partition
        except ValueError as e:
            if "Not logged in" in str(e):
                click.echo("Session expired. Please run 'srest auth login' to log in again.")
                return
            raise click.ClickException(str(e))
            
        if curl:
            curl_command = client.get_partitions(return_curl=True)
            click.echo('# Run this command to list partitions using curl:')
            click.echo(curl_command)
            return
            
        result = client.get_partitions()
        if format == OutputFormat.JSON.value:
            click.echo(json.dumps(result.to_dict(), indent=2))
            return

        partitions = result.partitions or []
        if not partitions:
            click.echo("No partitions found")
            return
            
        headers = ['NAME', 'STATE', 'NODES', 'DEFAULT']
        rows = []
        
        for partition in partitions:
            try:
                name = partition.name if partition.name else ''
                # Get partition state
                state = partition.flags.get('state', [''])[0] if partition.flags else 'UP'
                # Get node count from nodes.total
                nodes_count = partition.nodes.get('total', 0) if partition.nodes else 0
                # Check if this is the default partition
                is_default = 'yes' if partition.defaults and partition.defaults.get('job') else 'no'
                
                rows.append([
                    name,
                    state,
                    str(nodes_count),
                    is_default
                ])
            except AttributeError as e:
                click.echo(f"Warning: Partition {name} has invalid format: {str(e)}")
                continue
            except Exception as e:
                click.echo(f"Warning: Error processing partition {name}: {str(e)}")
                continue
            
        print_table(headers, rows)
    except Exception as e:
        if hasattr(e, 'status') and e.status in [401, 511]:
            click.echo("Session expired. Please run 'srest auth login' to log in again.")
            return
        raise click.ClickException(str(e))
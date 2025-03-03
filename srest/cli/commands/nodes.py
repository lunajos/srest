import click
import json
from ...client import get_client
from ...parsers.submit import OutputFormat
from ..utils import print_table, format_memory

@click.group(name='nodes')
def nodes_group():
    """Node management commands"""
    pass

@nodes_group.command('list')
@click.option('--state', help='Filter by state')
@click.option('--partition', help='Filter by partition')
@click.option('--format', type=click.Choice([f.value for f in OutputFormat]),
              default=OutputFormat.BASIC.value, help='Output format')
def list_nodes(state: str, partition: str, format: str):
    """List compute nodes"""
    # Client initialization moved to try block
    
    # Build filters
    filters = {}
    if state:
        filters['state'] = state
    if partition:
        filters['partition'] = partition
    
    try:
        try:
            client = get_client().node
        except ValueError as e:
            if "Not logged in" in str(e):
                click.echo("Session expired. Please run 'srest auth login' to log in again.")
                return
            raise click.ClickException(str(e))

        result = client.get_nodes()
        if format == OutputFormat.JSON.value:
            click.echo(json.dumps(result.to_dict(), indent=2))
        else:
            nodes = result.nodes or []
            if not nodes:
                click.echo("No nodes found")
                return
                
            headers = ['NODENAME', 'STATE', 'CPUS', 'MEMORY']
            rows = []
            
            for node in nodes:
                rows.append([
                    node.name or '',
                    node.state or '',
                    str(node.cpus or 0),
                    format_memory((node.real_memory or 0) * 1024 * 1024)  # Convert MB to bytes
                ])
            
            print_table(headers, rows)
    except Exception as e:
        if hasattr(e, 'status') and e.status == 401:
            click.echo("Session expired. Please run 'srest auth login' to log in again.")
            return
        raise click.ClickException(str(e))
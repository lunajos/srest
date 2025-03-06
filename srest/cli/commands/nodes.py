import click
import json
from ...client import get_client
from ...parsers.submit import OutputFormat
from ..utils import print_table, format_memory, format_time

@click.group(name='nodes')
def nodes_group():
    """Node management commands"""
    pass

@nodes_group.command('list')
@click.option('--state', help='Filter by state')
@click.option('--partition', help='Filter by partition')
@click.option('--format', type=click.Choice([f.value for f in OutputFormat]),
              default=OutputFormat.BASIC.value, help='Output format')
@click.option('--curl', is_flag=True, help='Output curl command with JWT and headers')
def list_nodes(state: str, partition: str, format: str, curl: bool):
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

        if curl:
            curl_command = client.get_nodes(return_curl=True)
            click.echo('# Run this command to list nodes using curl:')
            click.echo(curl_command)
            return

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

@nodes_group.command('info')
@click.argument('node_name')
@click.option('--format', type=click.Choice([f.value for f in OutputFormat]),
              default=OutputFormat.BASIC.value, help='Output format')
@click.option('--curl', is_flag=True, help='Output curl command with JWT and headers')
def node_info(node_name: str, format: str, curl: bool):
    """Show detailed information about a specific node"""
    try:
        try:
            client = get_client().node
        except ValueError as e:
            if "Not logged in" in str(e):
                click.echo("Session expired. Please run 'srest auth login' to log in again.")
                return
            raise click.ClickException(str(e))

        if curl:
            curl_command = client.get_node(node_name, return_curl=True)
            click.echo('# Run this command to get node information using curl:')
            click.echo(curl_command)
            return

        result = client.get_node(node_name)
        if format == OutputFormat.JSON.value:
            click.echo(json.dumps(result.to_dict(), indent=2))
            return

        if not result.nodes:
            click.echo(f"Node {node_name} not found")
            return

        node = result.nodes[0]
        click.echo(f"Node: {node.name}")
        click.echo(f"State: {', '.join(node.state)}")
        click.echo(f"Partitions: {', '.join(node.partitions)}")
        click.echo(f"CPUs: {node.cpus} (Allocated: {node.alloc_cpus}, Idle: {node.alloc_idle_cpus})")
        click.echo(f"Memory: {format_memory(node.real_memory * 1024 * 1024)} (Allocated: {format_memory(node.alloc_memory * 1024 * 1024)})")
        if node.cpu_load:
            click.echo(f"CPU Load: {node.cpu_load}")
        if node.features:
            click.echo(f"Features: {', '.join(node.features)}")
        if node.gres:
            click.echo(f"GRES: {node.gres}")
        if node.gres_used:
            click.echo(f"GRES Used: {node.gres_used}")
        if node.boot_time:
            click.echo(f"Boot Time: {format_time(node.boot_time['number'])}")
        if node.slurmd_start_time:
            click.echo(f"Slurmd Start Time: {format_time(node.slurmd_start_time['number'])}")
        if node.last_busy:
            click.echo(f"Last Busy: {format_time(node.last_busy['number'])}")
        if node.version:
            click.echo(f"Version: {node.version}")
        if node.operating_system:
            click.echo(f"OS: {node.operating_system}")
        if node.address:
            click.echo(f"Address: {node.address}")
        if node.hostname:
            click.echo(f"Hostname: {node.hostname}")
        if node.architecture:
            click.echo(f"Architecture: {node.architecture}")
        if node.tres:
            click.echo(f"TRES: {node.tres}")
        if node.comment:
            click.echo(f"Comment: {node.comment}")
        if node.reason:
            click.echo(f"Reason: {node.reason}")
    except Exception as e:
        if hasattr(e, 'status') and e.status == 401:
            click.echo("Session expired. Please run 'srest auth login' to log in again.")
            return
        raise click.ClickException(str(e))
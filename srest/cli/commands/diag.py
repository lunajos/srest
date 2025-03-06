import click
import json
from ...client import get_client
from ...parsers.submit import OutputFormat
from ..utils import print_table, format_time

@click.group(name='diag')
def diag_group():
    """Diagnostic commands"""
    pass

@diag_group.command('version')
@click.option('--format', type=click.Choice([f.value for f in OutputFormat]),
              default=OutputFormat.BASIC.value, help='Output format')
@click.option('--curl', is_flag=True, help='Show curl command instead of executing')
def show_version(format: str, curl: bool):
    """Show slurmrestd API version"""
    client = get_client()
    
    try:
        result = client.diag.get_versions(return_curl=curl)
        if curl:
            click.echo(result)
            return
            
        if format == OutputFormat.JSON.value:
            click.echo(json.dumps(result, indent=2))
        else:
            if not isinstance(result, dict):
                click.echo("Invalid OpenAPI specification format")
                return
                
            info = result.get('info', {})
            version = info.get('version')
            title = info.get('title')
            description = info.get('description')
            
            click.echo("Slurm REST API Information:")
            if title:
                click.echo(f"  Title: {title}")
            if version:
                click.echo(f"  Version: {version}")
            if description:
                click.echo(f"  Description: {description}")
    except Exception as e:
        raise click.ClickException(str(e))

@diag_group.command('show')
@click.option('--format', type=click.Choice([f.value for f in OutputFormat]),
              default=OutputFormat.BASIC.value, help='Output format')
@click.option('--curl', is_flag=True, help='Show curl command instead of executing')
def show_diagnostics(format: str, curl: bool):
    """Show Slurm diagnostics"""
    client = get_client()
    
    try:
        result = client.diag.get_diagnostics(return_curl=curl)
        if curl:
            click.echo(result)
            return
        if format == OutputFormat.JSON.value:
            click.echo(json.dumps(result, indent=2))
        else:
            if isinstance(result, dict):
                # Handle dictionary response
                diag = result.get('statistics', {})
                meta = result.get('meta', {})
            else:
                # Handle response object
                diag = result.statistics.to_dict() if result.statistics else {}
                meta = result.meta.to_dict() if result.meta else {}
                
            if not diag and not meta:
                click.echo("No diagnostic information available")
                return
                
            # Server info
            click.echo("Server Information:")
            slurm_info = meta.get('slurm', {})
            if slurm_info:
                version = slurm_info.get('version', {})
                version_str = f"{version.get('major', '0')}.{version.get('minor', '0')}.{version.get('micro', '0')}"
                click.echo(f"  Version: {version_str}")
                click.echo(f"  Release: {slurm_info.get('release', 'unknown')}")
                click.echo(f"  Cluster: {slurm_info.get('cluster', 'unknown')}")
            click.echo(f"  Thread count: {diag.get('server_thread_count', 0)}")
            click.echo("")
            
            # Queue info
            click.echo("Queue Information:")
            click.echo(f"  Agent queue size: {diag.get('agent_queue_size', 0)}")
            click.echo(f"  DBD agent queue size: {diag.get('dbd_agent_queue_size', 0)}")
            click.echo(f"  Schedule queue length: {diag.get('schedule_queue_length', 0)}")
            click.echo("")
            
            # Job info
            click.echo("Job Statistics:")
            click.echo(f"  Jobs submitted: {diag.get('jobs_submitted', 0)}")
            click.echo(f"  Jobs started: {diag.get('jobs_started', 0)}")
            click.echo(f"  Jobs completed: {diag.get('jobs_completed', 0)}")
            click.echo(f"  Jobs canceled: {diag.get('jobs_canceled', 0)}")
            click.echo(f"  Jobs failed: {diag.get('jobs_failed', 0)}")
            click.echo(f"  Jobs pending: {diag.get('jobs_pending', 0)}")
            click.echo(f"  Jobs running: {diag.get('jobs_running', 0)}")
            click.echo("")
            
            # Scheduler info
            click.echo("Scheduler Statistics:")
            click.echo(f"  Cycles total: {diag.get('schedule_cycle_total', 0)}")
            click.echo(f"  Cycles per minute: {diag.get('schedule_cycle_per_minute', 0)}")
            click.echo(f"  Last cycle time: {diag.get('schedule_cycle_last', 0)} microseconds")
            click.echo(f"  Max cycle time: {diag.get('schedule_cycle_max', 0)} microseconds")
            click.echo(f"  Mean cycle time: {diag.get('schedule_cycle_mean', 0)} microseconds")
    except Exception as e:
        raise click.ClickException(str(e))

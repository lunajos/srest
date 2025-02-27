import click
import json
from ...client import get_client
from ...parsers.submit import OutputFormat
from ..utils import print_table, format_time

@click.group(name='diag')
def diag_group():
    """Diagnostic commands"""
    pass

@diag_group.command('show')
@click.option('--format', type=click.Choice([f.value for f in OutputFormat]),
              default=OutputFormat.BASIC.value, help='Output format')
def show_diagnostics(format: str):
    """Show Slurm diagnostics"""
    client = get_client()
    
    try:
        result = client.get_diag()
        if format == OutputFormat.JSON.value:
            click.echo(json.dumps(result, indent=2))
        else:
            diag = result.get('statistics', {})
            if not diag:
                click.echo("No diagnostic information available")
                return
                
            # Server info
            click.echo("Server Information:")
            click.echo(f"  Version: {diag.get('server_version', 'unknown')}")
            click.echo(f"  Thread count: {diag.get('server_thread_count', 0)}")
            click.echo(f"  Agent count: {diag.get('agent_count', 0)}")
            click.echo("")
            
            # Job info
            click.echo("Job Statistics:")
            click.echo(f"  Jobs submitted: {diag.get('jobs_submitted', 0)}")
            click.echo(f"  Jobs started: {diag.get('jobs_started', 0)}")
            click.echo(f"  Jobs completed: {diag.get('jobs_completed', 0)}")
            click.echo(f"  Jobs canceled: {diag.get('jobs_canceled', 0)}")
            click.echo(f"  Jobs failed: {diag.get('jobs_failed', 0)}")
            click.echo("")
            
            # Scheduler info
            click.echo("Scheduler Statistics:")
            click.echo(f"  Cycles: {diag.get('schedule_cycle_count', 0)}")
            click.echo(f"  Last cycle: {diag.get('schedule_cycle_last', 'unknown')}")
            click.echo(f"  Queue length: {diag.get('schedule_queue_length', 0)}")
            click.echo("")
            
            # Debug info
            if diag.get('debug_flags', []):
                click.echo("Debug Flags:")
                for flag in diag['debug_flags']:
                    click.echo(f"  - {flag}")
    except Exception as e:
        raise click.ClickException(str(e))

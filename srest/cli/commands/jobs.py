import click
import json
from typing import Dict, Any
from ...client import get_client
from ...parsers.submit import SlurmDirectiveParser, OutputFormat

def format_job_submission(result: Dict[str, Any], output_format: OutputFormat) -> str:
    """Format job submission result"""
    if output_format == OutputFormat.PARSABLE:
        return str(result.get('job_id', ''))
    elif output_format == OutputFormat.JSON:
        return json.dumps(result, indent=2)
    else:
        return f"Submitted batch job {result.get('job_id', '')}"

def format_time(minutes: int) -> str:
    """Format time in minutes to readable string"""
    if minutes == 0:
        return 'UNLIMITED'
    days = minutes // 1440
    hours = (minutes % 1440) // 60
    mins = minutes % 60
    if days > 0:
        return f"{days}-{hours:02d}:{mins:02d}"
    return f"{hours:02d}:{mins:02d}"

@click.group(name='jobs')
def jobs_group():
    """Job management commands"""
    pass

@jobs_group.command('submit')
@click.option('--script', required=True, type=click.Path(exists=True))
@click.option('--name', help='Job name')
@click.option('--partition', help='Partition to submit to')
@click.option('--time', help='Time limit (minutes)')
@click.option('--nodes', type=int, help='Number of nodes')
@click.option('--ntasks', type=int, help='Number of tasks')
@click.option('--cpus-per-task', type=int, help='CPUs per task')
@click.option('--mem', help='Memory requirement (e.g., "4G")')
@click.option('--array', help='Job array spec (e.g., "1-10:2")')
@click.option('--dependency', help='Job dependencies')
@click.option('--account', help='Account to charge')
@click.option('--qos', help='Quality of Service')
@click.option('--mcs-label', help='MCS label for security')
@click.option('--parsable', is_flag=True, help='Output only the job ID')
@click.option('--format', type=click.Choice([f.value for f in OutputFormat]), 
              default=OutputFormat.BASIC.value, help='Output format')
@click.option('--ignore-directives', is_flag=True, help='Ignore #SBATCH directives')
def submit_job(script: str, ignore_directives: bool, **kwargs: Dict[str, Any]):
    """Submit a job to Slurm"""
    client = get_client()
    
    # Read script content
    with open(script) as f:
        script_content = f.read()
    
    # Parse directives unless ignored
    if not ignore_directives:
        script_content, directive_params = SlurmDirectiveParser.parse_script(script_content)
        # Command line args override directives
        params = {
            **directive_params,
            **{k: v for k, v in kwargs.items() 
               if v is not None and k not in ['format', 'parsable']}
        }
    else:
        params = {k: v for k, v in kwargs.items() 
                 if v is not None and k not in ['format', 'parsable']}
    
    try:
        result = client.submit_job(script_content, params)
        output_format = OutputFormat.PARSABLE if kwargs.get('parsable') else OutputFormat(kwargs.get('format'))
        click.echo(format_job_submission(result, output_format))
    except Exception as e:
        if kwargs.get('parsable'):
            click.echo(f"error;{str(e)}", err=True)
            raise SystemExit(1)
        raise click.ClickException(str(e))

@jobs_group.command('list')
@click.option('--user', help='Filter by user')
@click.option('--partition', help='Filter by partition')
@click.option('--state', help='Filter by state')
@click.option('--format', type=click.Choice([f.value for f in OutputFormat]),
              default=OutputFormat.BASIC.value, help='Output format')
def list_jobs(user: str, partition: str, state: str, format: str):
    """List jobs"""
    client = get_client()
    
    # Build filters
    filters = {}
    if user:
        filters['user'] = user
    if partition:
        filters['partition'] = partition
    if state:
        filters['state'] = state
    
    try:
        result = client.list_jobs(**filters)
        if format == OutputFormat.JSON.value:
            click.echo(json.dumps(result, indent=2))
        else:
            jobs = result.get('jobs', [])
            if not jobs:
                click.echo("No jobs found")
                return
                
            headers = ['JOBID', 'NAME', 'USER', 'PARTITION', 'STATE', 'TIME', 'NODES']
            rows = []
            
            for job in jobs:
                rows.append([
                    str(job.get('job_id', '')),
                    job.get('name', ''),
                    job.get('user_name', ''),
                    job.get('partition', ''),
                    job.get('job_state', ''),
                    format_time(job.get('time_limit_minutes', 0)),
                    str(job.get('nodes', ''))
                ])
            
            # Print table
            widths = [max(len(str(row[i])) for row in [headers] + rows)
                     for i in range(len(headers))]
            
            # Print headers
            for i, header in enumerate(headers):
                click.echo(f"{header:{widths[i]}}", nl=False)
                click.echo(" " if i < len(headers)-1 else "")
            
            # Print separator
            click.echo("-" * sum(widths))
            
            # Print rows
            for row in rows:
                for i, cell in enumerate(row):
                    click.echo(f"{cell:{widths[i]}}", nl=False)
                    click.echo(" " if i < len(row)-1 else "")
                    
    except Exception as e:
        raise click.ClickException(str(e))

@jobs_group.command('show')
@click.argument('job_id')
@click.option('--format', type=click.Choice([f.value for f in OutputFormat]),
              default=OutputFormat.JSON.value, help='Output format')
def show_job(job_id: str, format: str):
    """Show detailed information about a job"""
    client = get_client()
    try:
        result = client.get_job(job_id)
        if format == OutputFormat.JSON.value:
            # Add queue position if job is pending
            if result.get('job_state') == 'PENDING':
                queue_info = client.get_queue_position(job_id)
                result['queue_info'] = queue_info
            click.echo(json.dumps(result, indent=2))
        else:
            # Basic format - show key details
            job = result
            click.echo(f"Job ID: {job.get('job_id')}")
            click.echo(f"Name: {job.get('name')}")
            click.echo(f"User: {job.get('user_name')}")
            click.echo(f"Account: {job.get('account')}")
            click.echo(f"Partition: {job.get('partition')}")
            click.echo(f"QOS: {job.get('qos')}")
            click.echo(f"State: {job.get('job_state')}")
            
            # Show queue position if pending
            if job.get('job_state') == 'PENDING':
                queue_info = client.get_queue_position(job_id)
                click.echo(f"Queue Position: {queue_info.get('position')}")
                click.echo(f"Estimated Start: {queue_info.get('estimated_start_time')}")
                click.echo(f"Reason: {queue_info.get('reason')}")
            
            click.echo(f"Working Directory: {job.get('work_dir')}")
            click.echo(f"Command: {job.get('command')}")
            
            # Resources
            click.echo("\nResources:")
            click.echo(f"  Nodes: {job.get('nodes')}")
            click.echo(f"  CPUs per Task: {job.get('cpus_per_task')}")
            click.echo(f"  Memory: {job.get('memory_per_node')}")
            click.echo(f"  Time Limit: {format_time(job.get('time_limit_minutes', 0))}")
            
            # Time info
            if job.get('start_time'):
                click.echo(f"\nStart Time: {job.get('start_time')}")
            if job.get('end_time'):
                click.echo(f"End Time: {job.get('end_time')}")
            if job.get('submit_time'):
                click.echo(f"Submit Time: {job.get('submit_time')}")
            
            # Dependencies
            if job.get('dependencies'):
                click.echo(f"\nDependencies: {job.get('dependencies')}")
            
            # Array info
            if job.get('array_job_id'):
                click.echo(f"\nArray Job ID: {job.get('array_job_id')}")
                click.echo(f"Array Task ID: {job.get('array_task_id')}")
            
            # MCS info
            if job.get('mcs_label'):
                click.echo(f"\nMCS Label: {job.get('mcs_label')}")
            
            # Show any error message
            if job.get('stderr_path'):
                click.echo(f"\nStderr Path: {job.get('stderr_path')}")
            if job.get('stdout_path'):
                click.echo(f"\nStdout Path: {job.get('stdout_path')}")
            
    except Exception as e:
        raise click.ClickException(str(e))

@jobs_group.command('cancel')
@click.argument('job_id')
def cancel_job(job_id: str):
    """Cancel a job"""
    client = get_client()
    try:
        client.cancel_job(job_id)
        click.echo(f"Cancelled job {job_id}")
    except Exception as e:
        raise click.ClickException(str(e))
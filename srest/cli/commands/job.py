import click
import json
import os
from typing import Dict, Any, cast, Union
from ...client import get_client
from ...parsers.submit import SlurmDirectiveParser, OutputFormat
from swagger_client.models import V0036JobSubmissionResponse, V0036JobsResponse

def format_job_submission(result: V0036JobSubmissionResponse, output_format: OutputFormat) -> str:
    """Format job submission result"""
    if output_format == OutputFormat.PARSABLE:
        return str(result.job_id)
    elif output_format == OutputFormat.JSON:
        return json.dumps(result.to_dict(), indent=2)
    else:
        return f"Submitted batch job {result.job_id}"

def format_time(minutes: Any) -> str:
    """Format time in minutes to readable string"""
    if not minutes or minutes == 0:
        return 'UNLIMITED'
    try:
        mins = int(minutes)
        days = mins // 1440
        hours = (mins % 1440) // 60
        remaining_mins = mins % 60
        if days > 0:
            return f"{days}-{hours:02d}:{remaining_mins:02d}"
        return f"{hours:02d}:{remaining_mins:02d}"
    except (ValueError, TypeError):
        return 'UNKNOWN'

@click.group(name='job')
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
@click.option('--curl', is_flag=True, help='Output equivalent curl command')
@click.option('--workdir', type=click.Path(exists=True), help='Working directory for the job')
def submit_job(script: str, ignore_directives: bool, curl: bool = False, **kwargs: Dict[str, Any]):
    """Submit a job to Slurm"""
    client = get_client().job
    
    # Read script content and get absolute paths
    script_path = os.path.abspath(script)
    with open(script_path) as f:
        script_content = f.read()
    
    # Parse directives unless ignored
    if not ignore_directives:
        script_content, directive_params = SlurmDirectiveParser.parse_script(script_content)
        # Command line args override directives
        # Handle working directory with priority:
        # 1. Command line --workdir
        # 2. Script directive (--chdir/-D)
        # 3. Default to /home/admin/devel/srest
        if kwargs.get('workdir'):
            kwargs['current_working_directory'] = os.path.abspath(kwargs['workdir'])
            del kwargs['workdir']
            
        params = {
            # Job parameters
            'environment': [],  # Empty environment list required
            **directive_params,  # Script directives (including --chdir if present)
            'current_working_directory': '/home/admin/devel/srest',  # Default working directory
            **{k: v for k, v in kwargs.items()  # Command line args override everything
               if v is not None and k not in ['format', 'parsable']}
        }
    else:
        params = {
            # Job parameters
            'environment': [],  # Empty environment list required
            **{k: v for k, v in kwargs.items() 
               if v is not None and k not in ['format', 'parsable']}
        }
    
    try:
        result = client.submit_job(script_content, params, return_curl=curl)
        if curl:
            click.echo(result)
        else:
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
    client = get_client().job
    
    try:
        result = client.get_jobs()
        if format == OutputFormat.JSON.value:
            click.echo(json.dumps(result, indent=2))
            return

        if isinstance(result, dict):
            jobs = result.get('jobs', [])
        else:
            jobs = result.jobs if hasattr(result, 'jobs') else []

        if not jobs:
            click.echo("No jobs found")
            return
            
        headers = ['JOBID', 'NAME', 'USER', 'PARTITION', 'STATE', 'TIME', 'NODES']
        rows = []
        
        for job in jobs:
            job_data = job if isinstance(job, dict) else job.to_dict()
            state = job_data.get('job_state', '')
            # Handle case where state is a list
            if isinstance(state, list):
                state = state[0] if state else ''
            rows.append([
                str(job_data.get('job_id', '')),
                job_data.get('name', ''),
                job_data.get('user_name', ''),
                job_data.get('partition', ''),
                state,
                format_time(job_data.get('time_limit', 0)),
                str(job_data.get('nodes', ''))
            ])
            
        # Print table
        rows = [[str(cell) for cell in row] for row in rows]  # Convert all cells to strings
        widths = [max(len(row[i]) for row in [headers] + rows)
                 for i in range(len(headers))]
        
        # Print headers
        header_line = "  ".join(f"{header:<{widths[i]}}" for i, header in enumerate(headers))
        click.echo(header_line)
        
        # Print separator
        click.echo("-" * len(header_line))
        
        # Print rows
        for row in rows:
            row_line = "  ".join(f"{cell:<{widths[i]}}" for i, cell in enumerate(row))
            click.echo(row_line)
                    
    except Exception as e:
        raise click.ClickException(str(e))

@jobs_group.command('show')
@click.argument('job_id')
@click.option('--format', type=click.Choice([f.value for f in OutputFormat]),
              default=OutputFormat.JSON.value, help='Output format')
def show_job(job_id: str, format: str):
    """Show detailed information about a job"""
    client = get_client().job
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
            result = cast(V0036JobsResponse, result)
            if not result.jobs or not result.jobs[0]:
                click.echo("Job not found")
                return
                
            job = result.jobs[0]
            click.echo(f"Job ID: {job.job_id}")
            click.echo(f"Name: {job.name}")
            click.echo(f"User: {job.user_name}")
            click.echo(f"Account: {job.account}")
            click.echo(f"Partition: {job.partition}")
            click.echo(f"QOS: {job.qos}")
            click.echo(f"State: {job.job_state}")
            
            # Show queue position if pending
            if job.job_state == 'PENDING':
                # Queue position not supported in v3 yet
                click.echo(f"Reason: {job.state_reason}")
            
            click.echo(f"Working Directory: {job.work_dir}")
            click.echo(f"Command: {job.command}")
            
            # Resources
            click.echo("\nResources:")
            click.echo(f"  Nodes: {job.nodes}")
            click.echo(f"  CPUs per Task: {job.cpus_per_task}")
            click.echo(f"  Memory: {job.memory_per_node}")
            click.echo(f"  Time Limit: {format_time(job.time_limit or 0)}")
            
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
    client = get_client().job
    try:
        client.cancel_job(job_id)
        click.echo(f"Cancelled job {job_id}")
    except Exception as e:
        raise click.ClickException(str(e))

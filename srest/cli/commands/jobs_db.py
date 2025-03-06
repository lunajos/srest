"""Job accounting commands"""
import click
import json
from datetime import datetime, timedelta
from typing import cast
from ...client import get_client
from ...parsers.submit import OutputFormat
from ..utils import print_table
from ...client.v2.db import JobAccountingResponse

def format_time(seconds: int) -> str:
    """Format time in seconds to readable string"""
    if seconds == 0:
        return '00:00'
    minutes = seconds // 60
    hours = minutes // 60
    days = hours // 24
    
    if days > 0:
        return f"{days}-{hours%24:02d}:{minutes%60:02d}:{seconds%60:02d}"
    return f"{hours:02d}:{minutes%60:02d}:{seconds%60:02d}"

def format_memory(memory_bytes: int) -> str:
    """Format memory in bytes to human readable"""
    if memory_bytes == 0:
        return '0'
    units = ['B', 'K', 'M', 'G', 'T']
    k = 1024
    unit_idx = 0
    
    while memory_bytes >= k and unit_idx < len(units)-1:
        memory_bytes /= k
        unit_idx += 1
    
    return f"{memory_bytes:.1f}{units[unit_idx]}"

@click.group(name='sacct')
def sacct_group():
    """Job accounting commands (similar to sacct)"""
    pass

@sacct_group.command('list')
@click.option('--starttime', help='Start time for job query (format: YYYY-MM-DD[THH:MM[:SS]])')
@click.option('--endtime', help='End time for job query (format: YYYY-MM-DD[THH:MM[:SS]])')
@click.option('--user', help='Show jobs from this user')
@click.option('--account', help='Show jobs from this account')
@click.option('--jobs', help='Show jobs with these job IDs (comma separated)')
@click.option('--format', type=click.Choice([f.value for f in OutputFormat]),
              default=OutputFormat.BASIC.value, help='Output format')
@click.option('--curl', is_flag=True, help='Output curl command with JWT and headers')
def list_jobs(starttime: str, endtime: str, user: str, account: str, jobs: str, format: str, curl: bool):
    """List job accounting records"""
    try:
        client = get_client().db
        
        # Parse times
        start_time = None
        end_time = None
        
        if starttime:
            try:
                start_time = datetime.fromisoformat(starttime)
            except ValueError:
                raise click.ClickException(f"Invalid start time format: {starttime}")
                
        if endtime:
            try:
                end_time = datetime.fromisoformat(endtime)
            except ValueError:
                raise click.ClickException(f"Invalid end time format: {endtime}")
        
        # Default to last 24 hours if no time range specified
        if not start_time and not end_time:
            end_time = datetime.now()
            start_time = end_time - timedelta(days=1)
        
        # Split job IDs if provided
        job_ids = jobs.split(',') if jobs else None
        
        if curl:
            # Return curl command for first job ID or general query
            if job_ids:
                curl_command = client.get_jobs(
                    start_time=start_time,
                    end_time=end_time,
                    user=user,
                    account=account,
                    job_id=job_ids[0],
                    return_curl=True
                )
            else:
                curl_command = client.get_jobs(
                    start_time=start_time,
                    end_time=end_time,
                    user=user,
                    account=account,
                    return_curl=True
                )
            click.echo('# Run this command to get job accounting records using curl:')
            click.echo(curl_command)
            return
        
        # Make request for each job ID
        all_jobs = []
        if job_ids:
            for job_id in job_ids:
                result = client.get_jobs(
                    start_time=start_time,
                    end_time=end_time,
                    user=user,
                    account=account,
                    job_id=job_id
                )
                all_jobs.extend(result.jobs)
        else:
            result = client.get_jobs(
                start_time=start_time,
                end_time=end_time,
                user=user,
                account=account
            )
            all_jobs = result.jobs
                
        if format == OutputFormat.JSON.value:
            click.echo(json.dumps(all_jobs, indent=2))
        else:
            if not all_jobs:
                click.echo("No jobs found")
                return
                
            headers = ['JobID', 'JobName', 'Partition', 'Account', 'AllocCPUS', 'State', 'ExitCode']
            rows = []
            
            for job in all_jobs:
                # Get job ID and array task info
                job_id = str(job.get('job_id', ''))
                array_task_id = job.get('array_task_id')
                if array_task_id is not None:
                    job_id = f"{job_id}_{array_task_id}"
                
                # Add main job entry
                rows.append([
                    job_id,
                    job.get('name', '')[:8] + '+' if len(job.get('name', '')) > 8 else job.get('name', ''),
                    job.get('partition', ''),
                    job.get('account', ''),
                    str(job.get('ncpus', 1)),
                    job.get('state', ''),
                    f"{job.get('exit_code', 0)}:{job.get('signal_number', 0)}"
                ])
                
                # Add batch step if present
                if job.get('steps'):
                    for step in job['steps']:
                        if step.get('step_id') == 'batch':
                            rows.append([
                                f"{job_id}.batch",
                                'batch',
                                '',  # Partition not shown for batch step
                                '',  # Account not shown for batch step
                                str(step.get('ncpus', 1)),
                                step.get('state', ''),
                                f"{step.get('exit_code', 0)}:{step.get('signal_number', 0)}"
                            ])
            
            # Print table
            widths = [max(len(str(row[i])) for row in [headers] + rows)
                     for i in range(len(headers))]
            
            # Print headers
            for i, header in enumerate(headers):
                click.echo(f"{header:{widths[i]}}", nl=False)
                click.echo(" " if i < len(headers)-1 else "")
            
            # Print separator
            click.echo("-" * (sum(widths) + len(widths) - 1))
            
            # Print rows
            for row in rows:
                for i, cell in enumerate(row):
                    click.echo(f"{cell:{widths[i]}}", nl=False)
                    click.echo(" " if i < len(row)-1 else "")
                    
    except ValueError as e:
        if "Not logged in" in str(e):
            click.echo("Session expired. Please run 'srest auth login' to log in again.")
            return
        raise click.ClickException(str(e))
    except Exception as e:
        raise click.ClickException(str(e))

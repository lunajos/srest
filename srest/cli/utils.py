"""Utility functions for CLI output formatting"""
from typing import List, Dict, Any
import json
from ..parsers.submit import OutputFormat

def format_time(minutes: int) -> str:
    """Format time from minutes to human readable"""
    if minutes <= 0:
        return "UNLIMITED"
        
    days = minutes // 1440
    hours = (minutes % 1440) // 60
    mins = minutes % 60
    
    if days > 0:
        return f"{days}-{hours:02d}:{mins:02d}:00"
    return f"{hours:02d}:{mins:02d}:00"

def format_memory(mb: int) -> str:
    """Format memory from MB to human readable"""
    if mb <= 0:
        return "UNLIMITED"
        
    if mb >= 1024*1024:
        return f"{mb//(1024*1024)}TB"
    if mb >= 1024:
        return f"{mb//1024}GB"
    return f"{mb}MB"

def print_table(headers: List[str], rows: List[List[str]]):
    """Print formatted table"""
    if not rows:
        return
        
    # Calculate column widths
    widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(str(cell)))
            
    # Print headers
    header_line = "  ".join(h.ljust(w) for h, w in zip(headers, widths))
    print(header_line)
    print("-" * len(header_line))
    
    # Print rows
    for row in rows:
        print("  ".join(str(cell).ljust(w) for cell, w in zip(row, widths)))

def format_job_submission(result: Dict[str, Any], format: OutputFormat) -> str:
    """Format job submission result based on output format"""
    
    if format == OutputFormat.PARSABLE:
        # Format: job_id[;array_job_id][;array_task_id][;cluster_name]
        parts = []
        
        # Add main job ID
        parts.append(str(result.get("job_id", "")))
        
        # Add array job ID if present
        if "array_job_id" in result:
            parts.append(str(result["array_job_id"]))
            
            # Add array task ID if present
            if "array_task_id" in result:
                parts.append(str(result["array_task_id"]))
        
        # Add cluster name if present
        if "cluster_name" in result:
            # Ensure we have all parts up to cluster name
            while len(parts) < 3:
                parts.append("")
            parts.append(result["cluster_name"])
            
        return ";".join(parts)
        
    elif format == OutputFormat.JSON:
        return json.dumps(result, indent=2)
        
    elif format == OutputFormat.DETAILED:
        lines = []
        lines.append(f"Job ID: {result.get('job_id')}")
        
        if result.get("array_job_id"):
            lines.append(f"Array Job ID: {result['array_job_id']}")
            if result.get("array_task_id"):
                lines.append(f"Array Task ID: {result['array_task_id']}")
                
        if result.get("cluster_name"):
            lines.append(f"Cluster: {result['cluster_name']}")
            
        if result.get("job_submit_user_msg"):
            lines.append(f"Message: {result['job_submit_user_msg']}")
            
        return "\n".join(lines)
        
    else:  # BASIC
        return str(result.get("job_id", ""))

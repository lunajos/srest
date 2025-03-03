"""Job submission parsing utilities"""
import re
import logging
import os
from enum import Enum
from typing import Dict, Any, Tuple

# Set up logging
log_dir = os.path.expanduser("~/develop/srest/logs")
os.makedirs(log_dir, exist_ok=True)

# Get the root logger and set up file handler
logger = logging.getLogger(__name__)
file_handler = logging.FileHandler(os.path.join(log_dir, 'parser.log'))
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)

class OutputFormat(Enum):
    """Output format options"""
    BASIC = 'basic'
    JSON = 'json'
    PARSABLE = 'parsable'

class SlurmDirectiveParser:
    """Parser for Slurm script directives"""
    
    # Mapping of #SBATCH arguments to REST API parameters
    DIRECTIVE_MAP = {
        # Basic job settings
        "job_name": "name",
        "name": "name",
        "nodes": "nodes",  # API expects nodes as string
        "ntasks": "tres_per_job",  # API expects tres_per_job
        "cpus_per_task": "cpus_per_task",  # Keep as integer
        "partition": "partition",
        "time": "time_limit",  # API expects time_limit as integer
        "array": "array",
        
        # Memory settings
        "mem": "memory_per_node",  # API expects memory_per_node
        "mem_per_cpu": "memory_per_cpu",
        
        # Account and QoS
        "account": "account",
        "qos": "qos",
        
        # Dependencies and constraints
        "dependency": "dependency",
        "nodelist": "req_nodes",  # API expects req_nodes
        "exclude": "exc_nodes",  # API expects exc_nodes
        "constraint": "constraints",  # API expects constraints
        
        # Email notifications
        "mail_type": "mail_type",
        "mail_user": "mail_user",
        
        # MCS settings
        "mcs_label": "mcs_label",
        
        # Output settings
        "output": "standard_output",  # API expects standard_output
        "error": "standard_error",  # API expects standard_error
        
        # Additional settings
        "licenses": "licenses",
        "gres": "gres",
        "exclusive": "exclusive",
        "oversubscribe": "oversubscribe"
    }
    
    # Time format conversion
    TIME_FORMATS = [
        # days-hours:minutes:seconds
        (re.compile(r'^(\d+)-(\d+):(\d+):(\d+)$'), 
         lambda m: int(m.group(1))*24*60 + int(m.group(2))*60 + int(m.group(3)) + int(m.group(4))/60),
        # days-hours:minutes
        (re.compile(r'^(\d+)-(\d+):(\d+)$'), 
         lambda m: int(m.group(1))*24*60 + int(m.group(2))*60 + int(m.group(3))),
        # hours:minutes:seconds
        (re.compile(r'^(\d+):(\d+):(\d+)$'), 
         lambda m: int(m.group(1))*60 + int(m.group(2)) + int(m.group(3))/60),
        # hours:minutes
        (re.compile(r'^(\d+):(\d+)$'), 
         lambda m: int(m.group(1))*60 + int(m.group(2))),
        # minutes
        (re.compile(r'^(\d+)$'), 
         lambda m: int(m.group(1)))
    ]
    
    @staticmethod
    def parse_script(content: str) -> Tuple[str, Dict[str, Any]]:
        """Parse Slurm script directives"""
        logger.info("Starting to parse script")
        logger.info("=== Input Script Content ===")
        logger.info(content)
        logger.info("==========================")
        
        lines = content.splitlines()
        directives = {}
        script_lines = []
        
        for line_num, line in enumerate(lines, 1):
            # Keep shebang line
            if line.startswith('#!'):
                script_lines.append(line)
                logger.debug(f"Keeping shebang line: {line}")
                continue
                
            if line.startswith('#SBATCH'):
                # Skip commented out directives
                if line.startswith('##'):
                    logger.debug(f"Skipping commented out directive: {line}")
                    script_lines.append(line)
                    continue
                
                # Parse directive
                directive = line[7:].strip()
                logger.debug(f"Processing directive on line {line_num}: {directive}")
                
                if '=' in directive:
                    key, value = directive.split('=', 1)
                    key = key.strip().lstrip('-').replace('-', '_')
                    value = value.strip().strip('"\'')
                    logger.debug(f"Found key-value directive: {key}={value}")
                else:
                    # Handle --flag value format
                    parts = directive.split(maxsplit=1)
                    key = parts[0].strip().lstrip('-').replace('-', '_')
                    value = parts[1].strip() if len(parts) > 1 else None
                    logger.debug(f"Found space-separated directive: {key} {value}")
                    
                # Special case for -p (partition)
                if key == 'p':
                    key = 'partition'
                    logger.debug(f"Mapped -p to partition")
                
                # Map directive to REST API parameter
                api_key = SlurmDirectiveParser.DIRECTIVE_MAP.get(key)
                if api_key:
                    # Handle special cases
                    if api_key == 'mail_type':
                        # Convert to list
                        directives[api_key] = [v.strip() for v in value.split(',')]
                    elif api_key == 'cpus_per_task':
                        # Convert to integer
                        try:
                            directives[api_key] = int(value)
                        except ValueError:
                            logger.warning(f"Invalid integer value for {key}: {value}")
                            directives[api_key] = value
                    elif api_key == 'nodes':
                        # API expects string
                        directives[api_key] = str(value)
                    elif api_key == 'tres_per_job':
                        # Convert ntasks to tres format
                        try:
                            ntasks = int(value)
                            directives[api_key] = f'cpu={ntasks}'
                        except ValueError:
                            logger.warning(f"Invalid integer value for {key}: {value}")
                            directives[api_key] = value
                    else:
                        directives[api_key] = value
                    logger.debug(f"Mapped directive {key} to API parameter {api_key}")
                else:
                    logger.warning(f"Unknown directive {key}, skipping")
            else:
                script_lines.append(line)
                logger.debug(f"Keeping script line: {line}")
        
        logger.info(f"Found {len(directives)} directives")
        logger.debug(f"Parsed directives: {directives}")
        
        # Convert time formats if present
        if "time_limit" in directives:
            original_time = directives["time_limit"]
            for pattern, converter in SlurmDirectiveParser.TIME_FORMATS:
                match = pattern.match(original_time)
                if match:
                    minutes = int(converter(match))
                    directives["time_limit"] = minutes
                    logger.debug(f"Converted time format from {original_time} to {minutes} minutes")
                    break
            else:
                error_msg = f"Invalid time format: {original_time}"
                logger.error(error_msg)
                raise ValueError(error_msg)
            
        # Convert memory formats if present
        if "mem" in directives:
            original_mem = directives["mem"]
            # Remove any spaces
            mem_str = directives["mem"].strip().upper()
            
            # If it's just a number, assume it's megabytes
            if mem_str.isdigit():
                directives["mem"] = f"{mem_str}M"
                logger.debug(f"Converted memory format from {original_mem} to {directives['mem']}")
                
            # Otherwise, keep the format as is (assuming it's valid)
            logger.debug(f"Final memory value: {directives['mem']}")
        
        script_content = '\n'.join(script_lines)
        logger.info("=== Final Script Content ===")
        logger.info(script_content)
        logger.info("==========================")
        
        return script_content, directives
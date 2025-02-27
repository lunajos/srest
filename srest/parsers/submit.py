"""Job submission parsing utilities"""
import re
import logging
import os
from enum import Enum
from typing import Dict, Any, Tuple

# Set up logging
log_dir = os.path.expanduser("~/develop/srest/logs")
os.makedirs(log_dir, exist_ok=True)
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(log_dir, 'parser.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class OutputFormat(Enum):
    """Output format options"""
    BASIC = 'basic'
    JSON = 'json'
    PARSABLE = 'parsable'

class SlurmDirectiveParser:
    """Parser for Slurm script directives"""
    
    # Mapping of #SBATCH arguments to REST API parameters
    DIRECTIVE_MAP = {
        "nodes": "nodes",
        "ntasks": "ntasks",
        "cpus_per_task": "cpus_per_task",
        "partition": "partition",
        "time": "time",
        "name": "name",
        "array": "array",
        "mem": "mem",
        "mem_per_cpu": "mem_per_cpu",
        "account": "account",
        "qos": "qos",
        "dependency": "dependency",
        "mail_type": "mail_type",
        "mail_user": "mail_user",
        "nodelist": "nodelist",
        "exclude": "exclude",
        "constraint": "constraint",
        "mcs_label": "mcs_label"
    }
    
    # Time format conversion
    TIME_FORMATS = [
        (re.compile(r'^(\d+)-(\d+):(\d+):(\d+)$'), lambda m: int(m.group(1))*1440 + int(m.group(2))*60 + int(m.group(3))),  # days-hours:minutes:seconds
        (re.compile(r'^(\d+):(\d+):(\d+)$'), lambda m: int(m.group(1))*60 + int(m.group(2))),  # hours:minutes:seconds
        (re.compile(r'^(\d+):(\d+)$'), lambda m: int(m.group(1))*60 + int(m.group(2))),  # minutes:seconds
        (re.compile(r'^(\d+)$'), lambda m: int(m.group(1)))  # minutes
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
                # Parse directive
                directive = line[7:].strip()
                logger.debug(f"Processing directive on line {line_num}: {directive}")
                
                # Skip commented out directives
                if line.startswith('##SBATCH'):
                    logger.debug(f"Skipping commented out directive: {line}")
                    script_lines.append(line)
                    continue
                
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
                
                directives[key] = value
            else:
                script_lines.append(line)
                logger.debug(f"Keeping script line: {line}")
        
        logger.info(f"Found {len(directives)} directives")
        logger.debug(f"Parsed directives: {directives}")
        
        # Convert time formats if present
        if "time" in directives:
            original_time = directives["time"]
            for pattern, converter in SlurmDirectiveParser.TIME_FORMATS:
                match = pattern.match(directives["time"])
                if match:
                    directives["time"] = converter(match)
                    logger.debug(f"Converted time format from {original_time} to {directives['time']} minutes")
                    break
            else:
                error_msg = f"Invalid time format: {directives['time']}"
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
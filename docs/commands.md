# srest Command Reference

This document provides a comprehensive reference for all `srest` commands, including their usage, options, and current status.

## Table of Contents
- [Authentication Commands](#authentication-commands)
- [Configuration Commands](#configuration-commands)
- [Job Management Commands](#job-management-commands)
- [Node Management Commands](#node-management-commands)
- [Partition Management Commands](#partition-management-commands)
- [Reservation Management Commands](#reservation-management-commands)
- [Diagnostic Commands](#diagnostic-commands)
- [License Commands](#license-commands)
- [Version Commands](#version-commands)
- [Shell Completion Commands](#shell-completion-commands)

## Authentication Commands

### Login
```bash
srest auth login                                  # Interactive login
srest auth login --username slurm                # Specify username
srest auth login --username slurm --password slurm  # Specify username and password
```

### Other Auth Commands
```bash
srest auth logout   # Log out current session
srest auth status   # Check authentication status
srest auth token    # Display current auth token
```

## Configuration Commands

### Get Configuration
```bash
srest config get              # Get specific config value
srest config list            # List all config values
srest config list-api-versions  # List available API versions
srest config detect-api-version # Detect API version
```

### Set Configuration
```bash
# Authentication Configuration
srest config set auth.server_url http://192.168.1.195:8080
srest config set auth.client_id
srest config set auth.client_secret
srest config set auth.realm

# Slurm Configuration
srest config set slurm.url
srest config set slurm.api_version
```

### Delete Configuration
```bash
# Authentication Configuration
srest config delete auth.server_url
srest config delete auth.client_id
srest config delete auth.client_secret
srest config delete auth.realm

# Slurm Configuration
srest config delete slurm.url
srest config delete slurm.api_version
```

## Job Management Commands

### Submit Jobs
```bash
# Basic Job Submission
srest job submit --script tests/test.sbatch            # Submit a job script
srest job submit --script tests/test.sbatch --curl     # Get curl command
srest job submit --script tests/test.sbatch --help     # Show help

# Job Submission Options
srest job submit --script tests/test.sbatch --name TEXT          # Set job name
srest job submit --script tests/test.sbatch --partition TEXT     # Set partition
srest job submit --script tests/test.sbatch --time TEXT          # Set time limit
srest job submit --script tests/test.sbatch --nodes TEXT         # Set node count
srest job submit --script tests/test.sbatch --ntasks INTEGER     # Set task count
srest job submit --script tests/test.sbatch --cpus-per-task INTEGER  # Set CPUs per task
srest job submit --script tests/test.sbatch --mem TEXT           # Set memory
srest job submit --script tests/test.sbatch --array TEXT         # Set array spec
srest job submit --script tests/test.sbatch --account TEXT       # Set account
srest job submit --script tests/test.sbatch --qos TEXT           # Set QoS
srest job submit --script tests/test.sbatch --mcs-label TEXT     # Set MCS label
srest job submit --script tests/test.sbatch --env TEXT           # Set environment
srest job submit --script tests/test.sbatch --dependency TEXT    # Set dependencies
srest job submit --script tests/test.sbatch --parsable          # Parsable output

# Currently Not Working
srest job submit --script tests/test.sbatch --workdir PATH       # Set working directory
srest job submit --script tests/test.sbatch --format [basic|json|parsable]  # Set output format
srest job submit --script tests/test.sbatch --ignore-directives  # Ignore script directives
```

### List and Show Jobs
```bash
srest job list           # List all jobs
srest job list --curl    # Get curl command for list
srest job show 101       # Show specific job
srest job show 101 --curl  # Get curl command for show
```

### Cancel Jobs
```bash
srest job cancel 101       # Cancel specific job
srest job cancel 101 --curl  # Get curl command for cancel
srest job cancel --help    # Show help
```

## Node Management Commands

### List Nodes
```bash
srest nodes list                    # List all nodes
srest nodes list --help            # Show help

# Currently Not Working
srest nodes list --partition test  # List nodes in partition
srest nodes list --state idle     # List nodes by state
```

### Node Information
```bash
# Currently Not Working
srest nodes info localhost
srest nodes info localhost --format basic
srest nodes info localhost --format json
srest nodes info localhost --format parsable
```

## Partition Management Commands

### List Partitions
```bash
srest partitions list                 # List all partitions
srest partitions list --curl          # Get curl command
srest partitions list --format json   # JSON output
srest partitions list --format basic  # Basic output
srest partitions list --format parsable  # Parsable output
```

## Reservation Management Commands

### List Reservations
```bash
srest reservations list      # List all reservations
srest reservations list --curl  # Get curl command
```

### Create Reservations
```bash
srest reservations create --help  # Show help

# Currently Not Working
srest reservations create --name --start-time --duration --nodes --users --accounts --flags --curl
```

### Delete Reservations
```bash
# Currently Not Working
srest reservations delete reservation-name
srest reservations delete reservation-name --curl
```

## Diagnostic Commands

### Version and Status
```bash
srest diag version           # Show version
srest diag version --curl    # Get curl command for version
srest diag show             # Show diagnostics
srest diag show --curl      # Get curl command for diagnostics
```

## License Commands

### List Licenses
```bash
srest licenses list         # List all licenses
srest licenses list --curl  # Get curl command
```

## Version Commands

### Version Information
```bash
# Currently Not Working
srest --version            # Show version

# Working Commands
srest version list         # List versions
srest version show         # Show current version
```

## Shell Completion Commands

### Generate Shell Completions
```bash
srest completion           # Show completion info
srest completion --help    # Show help
srest completion bash      # Generate bash completion
srest completion zsh       # Generate zsh completion
```

## Common Options

Most commands support the following common options:
- `--help`: Show help message and exit
- `--curl`: Output the equivalent curl command instead of executing
- `--format`: Specify output format (basic|json|parsable)

## Known Issues

The following commands are currently not working properly (but work with curl):
1. `srest --version`
2. Reservation management:
   - Create reservations with parameters
   - Delete reservations
3. Node filtering:
   - List nodes by partition
   - List nodes by state
   - Node info with format options
4. Job submission:
   - Working directory specification
   - Format options
   - Directive ignoring

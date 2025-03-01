# SlurmREST CLI

A modern, user-friendly command-line tool for interacting with Slurm's REST API. Combines the simplicity of traditional Slurm commands (`sbatch`, `squeue`) with the flexibility of REST API access.

## Key Features
- Submit jobs using familiar `#SBATCH` directives
- Parse-friendly output formats (like `sbatch --parsable`)
- Full support for job arrays and dependencies
- JSON output for scripting and automation
- Clean, table-formatted output for human readability

## Quick Start
```bash
# Install
pip install slurmrest

# Configure
export SLURM_REST_URL="http://slurm.cluster.com:6820"
export SLURM_REST_TOKEN="your-token"

# Submit a job
srest jobs submit --script job.sh

# List your jobs
srest jobs list --user=$USER
```

## Installation

```bash
# From PyPI
pip install slurmrest

# From source
git clone https://github.com/lunajos/srest.git
cd srest
pip install -e .
```

## Usage

### Job Submission
```bash
# Submit a job
srest jobs submit --script job.sh --partition=debug

# Submit with #SBATCH directives
srest jobs submit --script job_with_directives.sh

# Get parsable output
srest jobs submit --script job.sh --parsable
```

### Job Management
```bash
# List jobs
srest jobs list

# List jobs in specific partition
srest jobs list --partition=debug

# Cancel job
srest jobs cancel 12345
```

### Node Information
```bash
# List all nodes
srest nodes list

# List nodes in specific state
srest nodes list --state=idle
```

### Partition Information
```bash
# List all partitions
srest partitions list
```

## Authentication

The CLI uses Keycloak for authentication. Before using any commands, you need to:

1. Configure Keycloak settings:
```bash
# Set Keycloak server URL
srest config set auth.server_url https://keycloak.example.com

# Optionally configure realm and client ID (defaults: slurm, slurm-rest)
srest config set auth.realm myrealm
srest config set auth.client_id myclient
```

2. Login to get a token:
```bash
srest auth login
# Enter your username and password when prompted
```

The token will be saved in `~/.config/srest/token.json` and automatically refreshed when needed.

To logout:
```bash
srest auth logout
```

## Configuration

Configuration is stored in `~/.config/srest/config.yaml` and can be managed with the following commands:

```bash
# Set a configuration value
srest config set <key> <value>

# Get a configuration value
srest config get <key>

# List all configuration
srest config list
```

Available configuration options:
- `slurm.url`: Slurm REST API base URL
- `auth.server_url`: Keycloak server URL
- `auth.realm`: Keycloak realm (default: slurm)
- `auth.client_id`: Keycloak client ID (default: slurm-rest)

Configuration values can also be set via environment variables:
- `SLURM_REST_URL`: Slurm REST API base URL
- `SLURM_REST_AUTH_SERVER_URL`: Keycloak server URL
- `SLURM_REST_AUTH_REALM`: Keycloak realm
- `SLURM_REST_AUTH_CLIENT_ID`: Keycloak client ID

## Commands

### Jobs
- `srest jobs list`: List all jobs
- `srest jobs submit <script>`: Submit a job script
- `srest jobs cancel <job_id>`: Cancel a job

### Nodes
- `srest nodes list`: List all compute nodes
- `srest nodes show <node>`: Show details for a specific node

### Partitions
- `srest partitions list`: List all partitions

### Reservations
- `srest reservations list`: List all reservations
- `srest reservations create`: Create a new reservation
  - `--name`: Reservation name (required)
  - `--start-time`: Start time (YYYY-MM-DD[THH:MM:SS])
  - `--duration`: Duration in minutes
  - `--nodes`: Node list or count
  - `--users`: Comma-separated list of users
  - `--accounts`: Comma-separated list of accounts
  - `--flags`: Comma-separated list of flags
- `srest reservations delete <name>`: Delete a reservation

### Licenses
- `srest licenses list`: List all licenses and their usage

### Diagnostics
- `srest diag show`: Show Slurm diagnostics including:
  - Server information
  - Job statistics
  - Scheduler statistics
  - Debug flags

### Output Formats
All list commands support different output formats via the `--format` option:
- `basic`: Simple output (default)
- `json`: JSON format
- `detailed`: Detailed human-readable format
- `parsable`: Machine-parsable format

### Environment Variables
- `SLURM_REST_URL`: Base URL for the Slurm REST API (required)
- `SLURM_REST_TOKEN`: Authentication token for the API (required)

## Mock Environment

For testing purposes, you can run a mock Slurm REST API and Keycloak server:

```bash
# Start mock servers
python -m src.mock

# In another terminal, configure srest
srest config set slurm.url http://localhost:8082
srest config set auth.server_url http://localhost:8081

# Login with mock credentials
srest auth login
# Username: mockuser
# Password: any password will work

# Test the mock environment
srest auth test
srest jobs list
srest nodes list
```

The mock environment provides:
- Simulated Slurm REST API with basic functionality
- Mock authentication server
- Simulated job submission and execution
- Mock nodes and partitions
- Basic job state transitions

Mock Server Features:
- Jobs progress through PENDING → RUNNING → COMPLETED states
- Node states and resource usage are randomized
- Predefined partitions: debug, gpu, cpu
- Mock job submission with script parsing
- Simulated job cancellation

Note: The mock servers are for testing only and should not be used in production.

## Examples

### Authentication and Configuration

```bash
# Initial setup
srest config set slurm.url https://slurm.example.com
srest config set auth.server_url https://keycloak.example.com

# Login
srest auth login

# Check token info
srest auth token
srest auth token --raw  # See full token data

# Test authentication
srest auth test

# View current configuration
srest config list
```

### Job Management

```bash
# Submit a simple job
srest jobs submit script.sh

# Submit with specific requirements
srest jobs submit script.sh --partition=debug --time=1:00:00 --mem=4G

# Submit an array job with dependencies
srest jobs submit array_script.sh --array=1-100:10 --dependency=afterok:12345

# Monitor specific jobs
srest jobs list --user=$USER --state=RUNNING,PENDING

# Cancel multiple jobs
srest jobs cancel 12345 12346 12347

# Cancel an entire array
srest jobs cancel 12345_[1-100]
```

### Resource Management

```bash
# View all nodes
srest nodes list

# View idle nodes with specific features
srest nodes list --state=IDLE --features=gpu

# View partition info with node details
srest partitions list --format=detailed

# Create a reservation
srest reservations create \
    --name=workshop \
    --start-time=2025-03-01T09:00:00 \
    --duration=480 \
    --nodes=4 \
    --users=user1,user2,user3

# Monitor license usage
srest licenses list
```

### Advanced Job Submission

```bash
# Submit with SBATCH directives in script
cat > job.sh << 'EOF'
#!/bin/bash
#SBATCH --job-name=ml_training
#SBATCH --partition=gpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --gres=gpu:1
#SBATCH --mem=16G
#SBATCH --time=12:00:00
#SBATCH --mail-type=BEGIN,END,FAIL
#SBATCH --mail-user=user@example.com

python train.py --epochs 100
EOF

srest jobs submit job.sh

# Submit with heterogeneous resources
cat > hetjob.sh << 'EOF'
#!/bin/bash
#SBATCH --job-name=het_job
#SBATCH hetero-job
#SBATCH --partition=gpu
#SBATCH --nodes=1
#SBATCH --gres=gpu:2
: End of step 1
#SBATCH --partition=cpu
#SBATCH --nodes=2
#SBATCH --ntasks-per-node=4
: End of step 2

srun --het-group=0 ./gpu_task.sh &
srun --het-group=1 ./cpu_task.sh &
wait
EOF

srest jobs submit hetjob.sh

# Submit with job arrays and task dependencies
cat > array_dep.sh << 'EOF'
#!/bin/bash
#SBATCH --job-name=process_data
#SBATCH --array=0-9
#SBATCH --dependency=aftercorr:$SLURM_ARRAY_TASK_ID

python process.py --chunk $SLURM_ARRAY_TASK_ID
EOF

srest jobs submit array_dep.sh
```

### Debugging

```bash
# Check system diagnostics
srest diag show

# View diagnostics in JSON format
srest diag show --format=json

# Check token status and expiry
srest auth token

# Test API connectivity
srest auth test

# View raw token for debugging
srest auth token --raw
```

### Using Environment Variables

```bash
# Set up environment
export SLURM_REST_URL=https://slurm.example.com
export SLURM_REST_AUTH_SERVER_URL=https://keycloak.example.com
export SLURM_REST_AUTH_REALM=myrealm
export SLURM_REST_AUTH_CLIENT_ID=myclient

# Commands will use environment variables
srest jobs list
```

## Distribution

### Build RPM

```bash
# Install RPM build tools
sudo yum install rpm-build python3-rpm-macros

# Create RPM build directories
mkdir -p ~/rpmbuild/{BUILD,RPMS,SOURCES,SPECS,SRPMS}

# Create source distribution
python setup.py sdist
cp dist/slurmrest-0.1.0.tar.gz ~/rpmbuild/SOURCES/

# Copy spec file
cp slurmrest.spec ~/rpmbuild/SPECS/

# Build RPM
rpmbuild -ba ~/rpmbuild/SPECS/slurmrest.spec

```

## Development

### Running Tests
```bash
# Install test dependencies
pip install pytest pytest-cov

# Run tests
pytest

# Run tests with coverage
pytest --cov=src
```

### Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## License

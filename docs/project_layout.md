# Slurm REST API Client Project Layout

This document provides a detailed overview of the project structure and how different components work together.

## Project Overview

The Slurm REST API Client (srest) is a command-line tool and Python library for interacting with Slurm's REST API. It provides commands for job submission, monitoring, account management, and more.

## Directory Structure

```
srest/
├── setup.py              # Package configuration and dependencies
├── README.md            # Project documentation
├── docs/               # Documentation directory
└── srest/              # Main package directory
    ├── __init__.py     # Package initialization, exports main classes
    ├── auth/           # Authentication handling
    │   ├── __init__.py
    │   ├── keycloak.py # Keycloak authentication implementation
    │   └── status.py   # Manages auth state (tokens, login status)
    ├── cli/            # Command-line interface implementation
    │   ├── __init__.py # Exports CLI commands
    │   ├── main.py     # Main CLI entry point
    │   ├── utils.py    # Shared CLI utilities
    │   └── commands/   # Individual command implementations
    │       ├── __init__.py
    │       ├── accounts.py  # Account management commands
    │       ├── auth.py      # Authentication commands
    │       ├── config.py    # Configuration commands
    │       ├── diag.py      # Diagnostic commands
    │       ├── job.py       # Job submission/control commands
    │       ├── jobs_db.py   # Job accounting commands (sacct)
    │       ├── licenses.py  # License commands
    │       ├── nodes.py     # Node commands
    │       └── partitions.py # Partition commands
    ├── client/         # API client implementation
    │   ├── __init__.py # Main client class and factory
    │   └── v2/         # Version 2 API implementation
    │       ├── __init__.py
    │       ├── base.py      # Base client with auth/request handling
    │       ├── db.py        # Database operations (accounting)
    │       ├── diag.py      # Diagnostic operations
    │       ├── jobs.py      # Job operations
    │       ├── licenses.py  # License operations
    │       ├── models.py    # Data models/schemas
    │       ├── nodes.py     # Node operations
    │       └── partitions.py # Partition operations
    └── parsers/        # Input parsing utilities
        ├── __init__.py
        └── submit.py   # Job submission script parser
```

## Program Flow

### 1. Command-Line Entry Point

When you run `srest`, this is what happens:

1. The entry point is defined in `setup.py`:
   ```python
   entry_points={
       "console_scripts": [
           "srest=srest.cli.main:cli",  # Maps 'srest' command to cli() function
       ],
   }
   ```

2. `srest/cli/main.py` contains the main `cli()` function that:
   - Sets up logging
   - Configures command groups
   - Handles shell completion

### 2. Command Structure

Commands are structured in a hierarchical way:
```bash
srest <command_group> <command> [options]
# Examples:
srest jobs submit job.sh    # Submit a job
srest accounts list         # List accounts
srest auth login           # Login to Slurm
```

Each command group (jobs, accounts, auth, etc.) is implemented in its own file under `cli/commands/`.

### 3. Authentication Flow

Authentication is handled by `srest/auth/`:

1. `auth/keycloak.py` - Implements Keycloak authentication:
   - Handles login requests
   - Manages JWT tokens
   - Refreshes expired tokens

2. `auth/status.py` - Manages authentication state:
   - Stores tokens in `~/.config/srest/auth_status.json`
   - Tracks login status
   - Provides token for API requests

### 4. API Client Structure

The API client is implemented in `srest/client/`:

1. `client/__init__.py` - Provides the main client interface:
   - `SlurmRESTClient` class - Main client interface
   - `get_client()` function - Factory method to create clients

2. `client/v2/base.py` - Base client implementation:
   - Handles authentication headers
   - Makes HTTP requests
   - Manages API versioning
   - Handles errors

3. Individual operation files (jobs.py, nodes.py, etc.):
   - Implement specific API endpoints
   - Handle request/response data
   - Provide typed interfaces

### 5. Job Submission Flow

When submitting a job (`srest jobs submit`):

1. `cli/commands/job.py` handles the command:
   - Parses command-line arguments
   - Reads job script

2. `parsers/submit.py` parses the job script:
   - Extracts SBATCH directives
   - Processes script content

3. `client/v2/jobs.py` makes the API request:
   - Formats job parameters
   - Sends submission request
   - Returns job ID

### 6. Data Models

Data structures are defined in `client/v2/models.py`:
- Base response types
- Error handling
- Type conversions

## Configuration

The client can be configured in several ways:
1. Command-line options
2. Environment variables
3. Configuration file (`~/.config/srest/config.yaml`)

## Error Handling

Errors are handled at multiple levels:
1. CLI level - User-friendly error messages
2. Client level - API errors and retries
3. Authentication level - Token expiration and refresh

## Development Guidelines

When adding new features:
1. Add command implementation in `cli/commands/`
2. Add API implementation in `client/v2/`
3. Update models if needed
4. Add tests
5. Update documentation

## Testing

Test files follow the same structure as source files:
```
tests/
├── test_auth.py      # Authentication tests
├── test_client.py    # API client tests
├── test_commands.py  # CLI command tests
└── examples/         # Example job scripts
```

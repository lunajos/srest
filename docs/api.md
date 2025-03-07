# Slurm REST API Reference

This document describes the REST API endpoints used by the `srest` client. The API follows OpenAPI 3.0.3 specification and is versioned.

## API Version

Current version: v0.0.42 (Slurm-24.11.2)

## Authentication

The API supports three authentication methods:
1. User + Token headers (`X-SLURM-USER-NAME` + `X-SLURM-USER-TOKEN`)
2. Token only (`X-SLURM-USER-TOKEN`)
3. Bearer Authentication (JWT)

### SSL Verification

Both the Slurm REST API and Keycloak authentication server support SSL certificate verification:

```python
# Using the Python client
from srest.client.v2.base import ClientConfig

# For Slurm REST API
config = ClientConfig(
    base_url="https://slurm.example.com:6820",
    verify_ssl=False  # Disable SSL verification for Slurm API
)

# For Keycloak authentication
from srest.auth.keycloak import KeycloakAuth

auth = KeycloakAuth(
    server_url="https://keycloak.example.com",
    realm="slurm",
    client_id="slurm-rest",
    verify_ssl=False  # Disable SSL verification for Keycloak
)
```

Using the CLI:
```bash
# Configure SSL verification
srest config set slurm.verify_ssl false  # For Slurm API
srest config set auth.verify_ssl false   # For Keycloak
```

> **Warning**: Disabling SSL verification makes your connections vulnerable to man-in-the-middle attacks. Only use this in development/testing environments or when using self-signed certificates. For production use, properly configure SSL certificates.

## Base URL Structure

```
http://<host>:<port>/slurm/v0.0.42/
```

## Endpoints

### Jobs

- List jobs: `GET /slurm/v0.0.42/jobs`
- Submit job: `POST /slurm/v0.0.42/job/submit`
- Get job info: `GET /slurm/v0.0.42/job/{job_id}`
- Cancel job: `DELETE /slurm/v0.0.42/job/{job_id}`

### Nodes

- List nodes: `GET /slurm/v0.0.42/nodes`
- Get node info: `GET /slurm/v0.0.42/node/{node_name}`

### Partitions

- List partitions: `GET /slurm/v0.0.42/partitions`
- Get partition info: `GET /slurm/v0.0.42/partition/{name}`

### Reservations

- List reservations: `GET /slurm/v0.0.42/reservations`
- Create reservation: `POST /slurm/v0.0.42/reservation`
- Get reservation info: `GET /slurm/v0.0.42/reservation/{name}`
- Delete reservation: `DELETE /slurm/v0.0.42/reservation/{name}`

### Diagnostics

- Get diagnostics: `GET /slurm/v0.0.42/diag`
- Ping: `GET /slurm/v0.0.42/ping`

### Licenses

- List licenses: `GET /slurm/v0.0.42/licenses`

## API Groups

The endpoints are grouped into three main tags:
- `slurm`: Methods that query slurmctld (jobs, nodes, partitions, etc.)
- `slurmdb`: Methods that query slurmdbd (accounts, users, QoS)
- `openapi`: Methods that query for generated OpenAPI specifications

## Response Formats

Most endpoints support multiple response formats:
- JSON (default)
- Basic (human-readable)
- Parsable (machine-readable)

## Common Query Parameters

- `format`: Response format (json|basic|parsable)
- `flags`: Additional flags for the operation
- `signal`: Signal type for job cancellation (e.g., SIGTERM, KILL)

## Error Responses

Error responses follow a standard format:
```json
{
  "errors": [
    {
      "error": "string",
      "error_code": integer
    }
  ]
}
```

# Slurm REST API Reference

This document describes the REST API endpoints used by the `srest` client. The API follows OpenAPI 3.0.3 specification and is versioned.

## API Version

Current version: v0.0.42 (Slurm-24.11.2)

## Authentication

The API supports three authentication methods:
1. User + Token headers (`X-SLURM-USER-NAME` + `X-SLURM-USER-TOKEN`)
2. Token only (`X-SLURM-USER-TOKEN`)
3. Bearer Authentication (JWT)

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

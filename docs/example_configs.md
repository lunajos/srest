# Example Configuration Files

This document shows example configuration files for the `srest` client. These files are typically stored in `~/.config/srest/`.

## config.yaml

This is the main configuration file (`~/.config/srest/config.yaml`):

```yaml
# Slurm REST API settings
slurm:
  # Base URL of your Slurm REST API
  url: "https://slurm.example.com:6820"
  # API version to use
  api_version: "v0.0.42"
  # Whether to verify SSL certificates for Slurm API connections
  verify_ssl: true

# Keycloak authentication settings
auth:
  # Base URL of your Keycloak server
  server_url: "https://keycloak.example.com"
  # Keycloak realm name
  realm: "slurm"
  # Client ID for Keycloak authentication
  client_id: "slurm-rest"
  # Client secret (if using confidential client)
  client_secret: "your-client-secret-here"
  # Whether to verify SSL certificates for Keycloak connections
  verify_ssl: true

# Optional: Development environment settings
dev:
  # Enable debug logging
  debug: false
  # Enable mock mode for testing
  mock: false

# Optional: Job submission defaults
job_defaults:
  # Default partition for job submission
  partition: "debug"
  # Default time limit (minutes)
  time: 60
  # Default memory per CPU (MB)
  mem_per_cpu: 1024
```

## token.json

This file (`~/.config/srest/token.json`) stores the current authentication token and is automatically managed by the client:

```json
{
  "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiw...",
  "expires_in": 300,
  "refresh_expires_in": 1800,
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "not-before-policy": 0,
  "session_state": "11111111-2222-3333-4444-555555555555",
  "scope": "email profile",
  "expires_at": "2025-03-07T00:39:14-05:00"
}
```

## auth.json

This file (`~/.config/srest/auth.json`) is used when manually configuring authentication without Keycloak:

```json
{
  "token": "your-jwt-or-user-token-here",
  "token_type": "jwt",
  "expiration": null,
  "username": "your-username"
}
```

## File Permissions

For security, these configuration files should have restricted permissions:

```bash
# Set correct ownership and permissions
chmod 700 ~/.config/srest
chmod 600 ~/.config/srest/config.yaml
chmod 600 ~/.config/srest/token.json
chmod 600 ~/.config/srest/auth.json
```

## Environment Variables

Configuration can also be provided through environment variables:

```bash
# Slurm REST API settings
export SREST_URL="https://slurm.example.com:6820"
export SREST_API_VERSION="v0.0.42"
export SREST_VERIFY_SSL="false"

# Keycloak authentication settings
export SREST_AUTH_URL="https://keycloak.example.com"
export SREST_AUTH_REALM="slurm"
export SREST_AUTH_CLIENT_ID="slurm-rest"
export SREST_AUTH_VERIFY_SSL="false"
```

Environment variables take precedence over configuration files.

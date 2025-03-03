# Manual Configuration Guide

This guide explains how to manually configure the Slurm REST client without using the CLI commands.

## Configuration Location

The client looks for configuration files in the following locations:
- `~/.config/srest/config.json` - Main configuration file
- `~/.config/srest/auth.json` - Authentication status and tokens

## Manual Authentication Setup

### Option 1: JWT Token
To manually configure JWT authentication:

1. Create or edit `~/.config/srest/auth.json`:
```json
{
    "token": "your-jwt-token-here",
    "token_type": "jwt",
    "expiration": null,
    "username": "your-username"
}
```

### Option 2: User Token
To manually configure user token authentication:

1. Create or edit `~/.config/srest/auth.json`:
```json
{
    "token": "your-user-token-here",
    "token_type": "user",
    "expiration": null,
    "username": "your-username"
}
```

## Manual Configuration Setup

Create or edit `~/.config/srest/config.json`:

```json
{
    "slurm": {
        "url": "https://your-slurm-rest-api-url",
        "version": "v0.0.42",
        "verify_ssl": true
    }
}
```

### Configuration Options

- `slurm.url`: The base URL of your Slurm REST API
- `slurm.version`: API version (default: v0.0.42)
- `slurm.verify_ssl`: Whether to verify SSL certificates (default: true)

## Verifying Configuration

After setting up the configuration files, you can verify them using:

```bash
srest config list  # View current configuration
srest auth status  # Check authentication status
```

## Troubleshooting

1. File Permissions
   - Ensure config files are readable only by your user:
   ```bash
   chmod 600 ~/.config/srest/auth.json
   chmod 600 ~/.config/srest/config.json
   ```

2. Common Issues
   - If using JWT, ensure the token is valid and not expired
   - Check that the API URL is accessible from your machine
   - Verify that the username matches your Slurm account

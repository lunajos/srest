"""Authentication commands for Slurm REST API v0.0.42

Supports:
- Bearer Authentication (JWT)
- User + Token headers (X-SLURM-USER-NAME + X-SLURM-USER-TOKEN)
- Token only (X-SLURM-USER-TOKEN)
"""
import click
from datetime import datetime
from ...auth import login as auth_login, logout as auth_logout, get_token_info
from ...auth.status import AuthStatus
from ...parsers.submit import OutputFormat

@click.group(name='auth')
def auth_group():
    """Authentication management commands"""
    pass

@auth_group.command('login')
@click.option('--username', prompt=True)
@click.option('--password', prompt=True, hide_input=True)
def login(username: str, password: str):
    """Login and get authentication token
    
    Uses Bearer Authentication (JWT) by default. For other methods:
    - User + Token: Set auth.user_token=true in config
    - Token only: Set auth.token_only=true in config
    """
    """Login to Keycloak and update auth status"""
    token_info = auth_login(username, password)
    
    # Update auth status
    auth_status = AuthStatus()
    auth_status.update_login(
        token=token_info['token'],
        expires_at=datetime.fromisoformat(token_info['expires']),
        username=username
    )
    
    click.echo("Login successful")

@auth_group.command('logout')
def logout():
    """Logout and clear saved token and status"""
    auth_logout()
    AuthStatus().clear_login()
    click.echo("Logged out")

@auth_group.command('token')
@click.option('--format', type=click.Choice([f.value for f in OutputFormat]),
              default=OutputFormat.BASIC.value, help='Output format')
@click.option('--curl', is_flag=True, help='Output curl command with JWT and headers')
def show_token(format: str, curl: bool = False):
    """Show current token information"""
    """Show current token information"""
    auth_status = AuthStatus()
    
    if not auth_status.is_logged_in():
        click.echo("Not logged in", err=True)
        return
    
    token_info = get_token_info()
    
    if curl:
        # Format curl command with current token
        curl_command = f"curl -H 'Authorization: Bearer {token_info['token']}'" \
                      f" -H 'Content-Type: application/json'" \
                      f" -X GET {auth_status.api_url}/slurm/v0.0.42/token"
        click.echo('# Run this command to get token info using curl:')
        click.echo(curl_command)
        return
    
    if format == OutputFormat.JSON.value:
        click.echo(token_info)
    else:
        status = "Valid" if auth_status.is_logged_in() else "Expired"
        click.echo(f"Login Status: {status}")
        click.echo(f"Token: {token_info['token']}")
        click.echo(f"Expires: {token_info['expires']}")
        if 'claims' in token_info:
            click.echo("\nClaims:")
            for key, value in token_info['claims'].items():
                click.echo(f"  {key}: {value}")

@auth_group.command('status')
def status():
    """Check current login status"""
    auth_status = AuthStatus()
    if auth_status.is_logged_in():
        click.echo("Logged in")
    else:
        click.echo("Not logged in", err=True)

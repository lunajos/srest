"""Authentication commands"""
import click
from ...auth import login as auth_login, logout as auth_logout, get_token_info
from ...parsers.submit import OutputFormat

@click.group(name='auth')
def auth_group():
    """Authentication management commands"""
    pass

@auth_group.command('login')
@click.option('--username', prompt=True)
@click.option('--password', prompt=True, hide_input=True)
def login(username: str, password: str):
    """Login to Keycloak"""
    auth_login(username, password)
    click.echo("Login successful")

@auth_group.command('logout')
def logout():
    """Logout and clear saved token"""
    auth_logout()
    click.echo("Logged out")

@auth_group.command('token')
@click.option('--format', type=click.Choice([f.value for f in OutputFormat]),
              default=OutputFormat.BASIC.value, help='Output format')
def show_token(format: str):
    """Show current token information"""
    token_info = get_token_info()
    
    if format == OutputFormat.JSON.value:
        click.echo(token_info)
    else:
        click.echo(f"Token: {token_info['token']}")
        click.echo(f"Expires: {token_info['expires']}")
        if 'claims' in token_info:
            click.echo("\nClaims:")
            for key, value in token_info['claims'].items():
                click.echo(f"  {key}: {value}")

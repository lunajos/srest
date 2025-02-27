"""Account management commands"""
import click
import json
from ...client import get_client
from ...parsers.submit import OutputFormat
from ..utils import print_table

@click.group(name='accounts')
def accounts_group():
    """Account management commands"""
    pass

@accounts_group.command('list')
@click.option('--format', type=click.Choice([f.value for f in OutputFormat]),
              default=OutputFormat.BASIC.value, help='Output format')
@click.option('--user', help='Filter by user')
def list_accounts(format: str, user: str):
    """List accounts"""
    client = get_client()
    
    try:
        result = client.list_accounts(user=user)
        if format == OutputFormat.JSON.value:
            click.echo(json.dumps(result, indent=2))
        else:
            accounts = result.get('accounts', [])
            if not accounts:
                click.echo("No accounts found")
                return
                
            headers = ['NAME', 'DESCRIPTION', 'ORGANIZATION', 'QOS', 'FAIRSHARE']
            rows = []
            
            for acc in accounts:
                rows.append([
                    acc.get('name', ''),
                    acc.get('description', ''),
                    acc.get('organization', ''),
                    ','.join(acc.get('qos', [])),
                    str(acc.get('fairshare', 0))
                ])
            
            print_table(headers, rows)
    except Exception as e:
        raise click.ClickException(str(e))

@accounts_group.command('show')
@click.argument('account')
@click.option('--format', type=click.Choice([f.value for f in OutputFormat]),
              default=OutputFormat.BASIC.value, help='Output format')
def show_account(account: str, format: str):
    """Show account details"""
    client = get_client()
    
    try:
        result = client.get_account(account)
        if format == OutputFormat.JSON.value:
            click.echo(json.dumps(result, indent=2))
        else:
            acc = result.get('account', {})
            if not acc:
                raise click.ClickException(f"Account not found: {account}")
            
            click.echo(f"Account: {acc['name']}")
            click.echo(f"Description: {acc.get('description', 'N/A')}")
            click.echo(f"Organization: {acc.get('organization', 'N/A')}")
            click.echo(f"QOS: {', '.join(acc.get('qos', []))}")
            click.echo(f"Fairshare: {acc.get('fairshare', 0)}")
            click.echo("\nUsers:")
            for user in acc.get('users', []):
                click.echo(f"  - {user}")
    except Exception as e:
        raise click.ClickException(str(e))

@accounts_group.command('associations')
@click.option('--user', help='Filter by user')
@click.option('--account', help='Filter by account')
@click.option('--format', type=click.Choice([f.value for f in OutputFormat]),
              default=OutputFormat.BASIC.value, help='Output format')
def list_associations(user: str, account: str, format: str):
    """List user-account associations"""
    client = get_client()
    
    try:
        result = client.list_associations(user=user, account=account)
        if format == OutputFormat.JSON.value:
            click.echo(json.dumps(result, indent=2))
        else:
            assocs = result.get('associations', [])
            if not assocs:
                click.echo("No associations found")
                return
                
            headers = ['USER', 'ACCOUNT', 'PARTITION', 'QOS', 'DEFAULT_QOS']
            rows = []
            
            for assoc in assocs:
                rows.append([
                    assoc.get('user', ''),
                    assoc.get('account', ''),
                    assoc.get('partition', '*'),
                    ','.join(assoc.get('qos', [])),
                    assoc.get('default_qos', '')
                ])
            
            print_table(headers, rows)
    except Exception as e:
        raise click.ClickException(str(e))

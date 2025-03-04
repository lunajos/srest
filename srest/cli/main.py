"""Main CLI entry point"""
import click
import logging
import warnings
import urllib3
from .commands import (
    jobs_group, nodes_group, partitions_group, reservations_group,
    licenses_group, diag_group, accounts_group,
    config_group, auth_group
)
from .commands.jobs_db import sacct_group

# Disable urllib3 warnings about LibreSSL
warnings.filterwarnings('ignore', category=urllib3.exceptions.NotOpenSSLWarning)

# Configure logging
logging.getLogger('urllib3').setLevel(logging.WARNING)

def get_completion_script():
    """Get the completion script for the current shell"""
    import os
    shell = os.environ.get('SHELL', '')
    if 'zsh' in shell:
        return '''
#compdef srest

_srest_completion() {
    local -a completions
    local -a completions_with_descriptions
    local -a response
    (( ! $+commands[srest] )) && return 1

    response=("${(@f)$(env COMP_WORDS="${words[*]}" COMP_CWORD=$((CURRENT-1)) _SREST_COMPLETE=zsh_complete srest)}")

    for type key descr in ${response}; do
        if [[ "$type" == "plain" ]]; then
            if [[ "$descr" == "_" ]]; then
                completions+=("$key")
            else
                completions_with_descriptions+=("$key":"$descr")
            fi
        fi
    done

    if [ "${#completions_with_descriptions}" -gt 0 ]; then
        _describe -V unsorted completions_with_descriptions -U
    fi

    if [ "${#completions}" -gt 0 ]; then
        compadd -U -V unsorted -a completions
    fi

    return 0
}

compdef _srest_completion srest
'''
    else:  # Assume bash
        return '''
_srest_completion() {
    local IFS=$'\n'
    local response

    response=$(env COMP_WORDS="${COMP_WORDS[*]}" COMP_CWORD=$COMP_CWORD _SREST_COMPLETE=bash_complete srest)

    for completion in $response; do
        IFS=',' read type value <<< "$completion"
        if [[ $type == 'dir' ]]; then
            COMPREPLY=()
            compopt -o dirnames
        elif [[ $type == 'file' ]]; then
            COMPREPLY=()
            compopt -o default
        elif [[ $type == 'plain' ]]; then
            COMPREPLY+=($value)
        fi
    done

    return 0
}

complete -F _srest_completion srest
'''

@click.group()
@click.version_option()
@click.option('--debug/--no-debug', default=False, help='Enable debug logging')
def cli(debug):
    """Slurm REST API client"""
    log_level = logging.DEBUG if debug else logging.WARNING
    logging.basicConfig(level=log_level, format='%(message)s')

@cli.command()
@click.argument('shell', type=click.Choice(['bash', 'zsh']), required=False)
def completion(shell):
    """Output shell completion code"""
    if not shell:
        import os
        shell = 'zsh' if 'zsh' in os.environ.get('SHELL', '') else 'bash'
    
    if shell == 'zsh':
        click.echo(get_completion_script())
    else:  # bash
        click.echo(get_completion_script())

# Add command groups
cli.add_command(jobs_group)
cli.add_command(nodes_group)
cli.add_command(partitions_group)
cli.add_command(reservations_group)
cli.add_command(licenses_group)
cli.add_command(diag_group)
cli.add_command(accounts_group)

cli.add_command(config_group)
cli.add_command(auth_group)
cli.add_command(sacct_group)

if __name__ == '__main__':
    cli()

import subprocess
from typing import List

import click

from . import gameta_cli, gameta_context, GametaContext


__all__ = ['apply']


@gameta_cli.command()
@click.option('--command', '-c', type=str, required=True, help='Command to be executed')
@click.option('--tags', '-t', type=str, multiple=True, default=[], help='Repository tags to apply commands to')
@click.option('--repositories', '-r', type=str, multiple=True, default=[], help='Repositories to apply commands to')
@click.option('--verbose', '-v', is_flag=True, default=False, help='Display execution output when command is applied')
@click.option('--shell', '-s', is_flag=True, default=False, help='Execute command in a separate shell')
@click.option('--raise-errors', '-e', is_flag=True, default=False,
              help='Raise errors that occur when executing command and terminate execution')
@gameta_context
def apply(
        context: GametaContext,
        command: str,
        tags: List[str],
        repositories: List[str],
        verbose: bool,
        shell: bool,
        raise_errors: bool
) -> None:
    """
    Applies a CLI command to all repositories (by default) or a specific set of repositories
    \f
    Args:
        context (GametaContext): Gameta Context
        command (str): CLI command to be applied
        tags (List[str]): Repository tags to apply command to
        repositories (List[str]): Repositories to apply command to
        verbose (bool): Flag to indicate that output should be displayed as the command is applied
        shell (bool): Flag to indicate that command should be executed in a separate shell
        raise_errors (bool): Flag to indicate that errors should be raised if they occur during execution and the
                             overall execution should be terminated

    Returns:
        None

    Examples:
        $ gameta apply -c "git fetch --all --tags --prune" -t tag1 -t tag2 -t tag3 -r repo_a
        $ gameta apply -c "git fetch --all --tags --prune" -e  # Raise errors and terminate
        $ gameta apply -c "git fetch --all --tags --prune" -s  # Executed in a separate shell
    """
    repos: List[str] = sorted(
        list(
            set([repo for tag in tags for repo in context.tags.get(tag, [])]) |
            set([repo for repo in repositories if repo in context.repositories])
        )
    )
    click.echo(
        f"Applying '{command}' to repos {repos if repos else list(context.repositories.keys())}"
        f"{' in a separate shell' if shell else ''}"
    )
    for repo, c in context.apply([command], repos=repos, shell=shell):
        click.echo(f"Executing {command} in {repo}")
        try:
            if verbose:
                click.echo(subprocess.check_output(c))
            else:
                subprocess.check_output(c)
        except subprocess.SubprocessError as e:
            if raise_errors:
                raise click.ClickException(
                    f'Error {e.__class__.__name__}.{str(e)} occurred when executing command {command} in {repo}'
                )
            click.echo(
                f'Error {e.__class__.__name__}.{str(e)} occurred when executing command {command} in {repo}, '
                f'continuing execution'
            )

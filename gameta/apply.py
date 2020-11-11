import subprocess
from typing import List, Tuple

import click

from .cli import gameta_cli
from .context import gameta_context, GametaContext


__all__ = ['apply']


@gameta_cli.command()
@click.option('--command', '-c', 'commands', type=str, required=True, multiple=True, help='CLI Commands to be executed')
@click.option('--tags', '-t', type=str, multiple=True, default=(), help='Repository tags to apply CLI commands to')
@click.option('--repositories', '-r', type=str, multiple=True, default=(), help='Repositories to apply CLI commands to')
@click.option('--verbose', '-v', is_flag=True, default=False,
              help='Display execution output when CLI commands are applied')
@click.option('--shell', '-s', is_flag=True, default=False, help='Execute CLI commands in a separate shell')
@click.option('--python', '-p', is_flag=True, default=False, help='Execute Python scripts using Python 3 interpreter')
@click.option('--raise-errors', '-e', is_flag=True, default=False,
              help='Raise errors that occur when executing CLI commands and terminate execution')
@gameta_context
def apply(
        context: GametaContext,
        commands: Tuple[str],
        tags: Tuple[str],
        repositories: Tuple[str],
        verbose: bool,
        shell: bool,
        python: bool,
        raise_errors: bool
) -> None:
    """
    Applies a CLI command to all repositories (by default) or a specific set of repositories
    \f
    Args:
        context (GametaContext): Gameta Context
        commands (Tuple[str]): CLI command to be applied
        tags (Tuple[str]): Repository tags to apply command to
        repositories (Tuple[str]): Repositories to apply command to
        verbose (bool): Flag to indicate that output should be displayed as the command is applied
        python (bool): Flag to indicate that command should be executed with the Python 3 interpreter
        shell (bool): Flag to indicate that command should be executed in a separate shell
        raise_errors (bool): Flag to indicate that errors should be raised if they occur during execution and the
                             overall execution should be terminated

    Returns:
        None

    Examples:
        $ gameta apply -c "git fetch --all --tags --prune" -c "git checkout {branch}"  # Multiple commands
        $ gameta apply -c "git fetch --all --tags --prune" -t tag1 -t tag2 -t tag3 -r repo_a  # Apply to tags and repos
        $ gameta apply -c "git fetch --all --tags --prune" -e  # Raise errors and terminate
        $ gameta apply -c "git fetch --all --tags --prune" -s  # Executed in a separate shell
        $ gameta apply -c "git fetch --all --tags --prune" -v  # Verbose

    Raises:
        click.ClickException: If errors occur during processing
    """
    try:
        repos: List[str] = sorted(
            list(
                set([repo for tag in tags for repo in context.tags.get(tag, [])]) |
                set([repo for repo in repositories if repo in context.repositories])
            )
        )

        if python:
            try:
                for command in commands:
                    compile(command, 'test', 'exec')
            except SyntaxError:
                raise click.ClickException(f"One of the commands in {list(commands)} is not a valid Python script")

        # Python subprocess does not handle multiple commands
        # hence we need to handle it in a separate shell
        if len(commands) > 1:
            click.echo("Multiple commands detected, executing in a separate shell")
            shell = True

        if shell:
            click.echo(
                f"Applying {list(commands)} to repos {repos if repos else list(context.repositories.keys())} "
                f"in a separate shell"
            )
        elif python:
            click.echo(
                f"Applying Python commands {list(commands)} to repos "
                f"{repos if repos else list(context.repositories.keys())} in a separate shell"
            )
        else:
            click.echo(
                f"Applying {list(commands)} to repos {repos if repos else list(context.repositories.keys())}"
            )
        for repo, c in context.apply(list(commands), repos=repos, shell=shell, python=python):
            click.echo(f"Executing {' '.join(c)} in {repo}")
            try:
                if verbose:
                    click.echo(subprocess.check_output(c))
                else:
                    subprocess.check_output(c)
            except subprocess.SubprocessError as e:
                if raise_errors:
                    raise click.ClickException(
                        f'Error {e.__class__.__name__}.{str(e)} occurred when executing command {" ".join(c)} in {repo}'
                    )
                click.echo(
                    f'Error {e.__class__.__name__}.{str(e)} occurred when executing command {" ".join(c)} in {repo}, '
                    f'continuing execution'
                )
    except click.ClickException:
        raise
    except Exception as e:
        raise click.ClickException(f"{e.__class__.__name__}.{str(e)}")

import subprocess
from typing import List, Tuple, Optional

import click

from gameta.base import gameta_context, GametaContext


__all__ = ['apply']


@click.command()
@click.option('--command', '-c', 'commands', type=str, required=True, multiple=True, help='CLI Commands to be executed')
@click.option('--tags', '-t', type=str, multiple=True, default=(), help='Repository tags to apply CLI commands to')
@click.option('--repositories', '-r', type=str, multiple=True, default=(), help='Repositories to apply CLI commands to')
@click.option('--all', '-a', 'use_all', is_flag=True, default=False,
              help='Applies the CLI commands to all repositories, overrides the tags and repositories arguments')
@click.option('--verbose', '-v', is_flag=True, default=False,
              help='Display execution output when CLI commands are applied')
@click.option('--shell', '-s', is_flag=True, default=False, help='Execute CLI commands in a separate shell')
@click.option('--python', '-p', is_flag=True, default=False, help='Execute Python scripts using Python 3 interpreter')
@click.option('--venv', '-ve', type=str, default=None, help='Virtualenv to execute commands in')
@click.option('--raise-errors', '-e', is_flag=True, default=False,
              help='Raise errors that occur when executing CLI commands and terminate execution')
@gameta_context
def apply(
        context: GametaContext,
        commands: Tuple[str],
        tags: Tuple[str],
        repositories: Tuple[str],
        use_all: bool,
        verbose: bool,
        shell: bool,
        python: bool,
        venv: Optional[str],
        raise_errors: bool
) -> None:
    """
    Applies a CLI command to the metarepo (by default) or a specific set of repositories
    \f
    Args:
        context (GametaContext): Gameta Context
        commands (Tuple[str]): CLI commands to be applied
        tags (Tuple[str]): Repository tags to apply commands to
        repositories (Tuple[str]): Repositories to apply commands to
        use_all (bool): Flag to indicate that commands should be applied to all repositories
        verbose (bool): Flag to indicate that output should be displayed as the commands is applied
        python (bool): Flag to indicate that commands should be executed with the Python 3 interpreter
        venv (Optional[str]): Virtualenv to execute commands with
        shell (bool): Flag to indicate that commands should be executed in a separate shell
        raise_errors (bool): Flag to indicate that errors should be raised if they occur during execution and the
                             overall execution should be terminated

    Returns:
        None

    Examples:
        $ gameta apply -c "git fetch --all --tags --prune" -c "git checkout {branch}" -a  # All repositories
        $ gameta apply -p -c 'from os import getcwd\nprint(getcwd())'  # Executes a Python script
        $ gameta apply -ve test -c "pip install cryptography"  # Applies command with virtualenv test
        $ gameta apply -c "git fetch --all --tags --prune" -c "git checkout {branch}"  # Multiple commands
        $ gameta apply -c "git fetch --all --tags --prune" -t tag1 -t tag2 -t tag3 -r repo_a  # Apply to tags and repos
        $ gameta apply -c "git fetch --all --tags --prune" -e  # Raise errors and terminate
        $ gameta apply -c "git fetch --all --tags --prune" -s  # Executed in a separate shell
        $ gameta apply -c "git fetch --all --tags --prune" -v  # Verbose

    Raises:
        click.ClickException: If errors occur during processing
    """
    try:
        repos: List[str]
        if use_all:
            repos = list(context.repositories.keys())
        elif repositories or tags:
            repos = sorted(
                list(
                    set([repo for tag in tags for repo in context.tags.get(tag, [])]) |
                    set([repo for repo in repositories if repo in context.repositories])
                )
            )
            # No valid repositories or tags were provided
            if not repos:
                raise click.ClickException(
                    f"The current configuration (tags: {list(tags)}, repositories: {list(repositories)}) yielded no "
                    f"repositories, please check that you entered valid tags and repositories"
                )
        else:
            repos = [context.metarepo]

        if python:
            try:
                for command in commands:
                    compile(command, 'test', 'exec')
            except SyntaxError:
                raise click.ClickException(f"One of the commands in {list(commands)} is not a valid Python script")

        if venv is not None and venv not in context.virtualenvs:
            raise click.ClickException(f"Virtualenv {venv} has not been registered")

        # Python subprocess does not handle multiple commands
        # hence we need to handle it in a separate shell
        if len(commands) > 1:
            click.echo("Multiple commands detected, executing in a separate shell")
            shell = True

        if venv:
            click.echo(
                f"Applying {list(commands)} to repos {repos if repos else list(context.repositories.keys())} "
                f"with virtualenv {venv}"
            )
        elif shell:
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
        for repo, c in context.apply(list(commands), repos=repos, shell=shell, python=python, venv=venv):
            click.echo(f"Executing {' '.join(c)} in {repo}")
            try:
                if verbose:
                    with subprocess.Popen(c, stdout=subprocess.PIPE, stderr=subprocess.STDOUT) as cmd:
                        for line in iter(cmd.stdout.readline, b''):
                            click.echo(line.rstrip())
                else:
                    subprocess.run(c, stderr=subprocess.STDOUT, check=True)
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

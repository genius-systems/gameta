from copy import deepcopy
from typing import Any, Callable, Dict, Optional, Tuple

import click

from gameta.base import GametaContext, gameta_context

__all__ = ['command_cli']


@click.group('cmd')
@gameta_context
def command_cli(context: GametaContext) -> None:
    """
    CLI for managing CLI commands
    \f
    Args:
        context (GametaContext): Gameta Context

    Returns:
        None

    Raises:
        click.ClickException: If we are not currently operating in a metarepo directory
    """
    if not context.is_metarepo:
        raise click.ClickException(f"{context.project_dir} is not a metarepo, initialise it with 'gameta init'")


@command_cli.command()
@click.option('--name', '-n', type=str, required=True, help='Gameta command name to be added to the store')
@click.option('--description', '-d', type=str, default='', help='Brief description of the Gameta command')
@click.option('--overwrite', '-o', type=bool, is_flag=True, default=False,
              help='Overwrite existing Gameta command in the store')
@click.option('--command', '-c', 'commands', type=str, required=True, multiple=True, help='CLI Commands to be executed')
@click.option('--tags', '-t', type=str, multiple=True, default=(), help='Repository tags to apply CLI commands to')
@click.option('--repositories', '-r', type=str, multiple=True, default=(), help='Repositories to apply CLI commands to')
@click.option('--venv', '-ve', type=str, default=None, help="Virtualenv to execute commands with, defaults to None")
@click.option('--all', '-a', 'use_all', is_flag=True, default=False,
              help='Applies the CLI commands to all repositories, overrides the tags and repositories arguments')
@click.option('--verbose', '-v', is_flag=True, default=False,
              help='Display execution output when CLI command is applied')
@click.option('--shell', '-s', is_flag=True, default=False, help='Execute CLI commands in a separate shell')
@click.option('--python', '-p', is_flag=True, default=False, help='Execute Python scripts using Python 3 interpreter')
@click.option('--raise-errors', '-e', is_flag=True, default=False,
              help='Raise errors that occur when executing CLI commands and terminate execution')
@gameta_context
def add(
        context: GametaContext,
        name: str,
        overwrite: bool,
        description: str,
        commands: Tuple[str],
        tags: Tuple[str],
        repositories: Tuple[str],
        venv: Optional[str],
        use_all: bool,
        verbose: bool,
        shell: bool,
        python: bool,
        raise_errors: bool
) -> None:
    """
    Adds a new Gameta command to the Gameta command store
    \f
    Args:
        context (GametaContext): Gameta Context
        name (str): Name of the CLI command to be stored
        description (str): Brief description of the command
        overwrite (bool): Flag to overwrite the existing Gameta command if it exists, defaults to false

        commands (Tuple[str]): CLI commands to be applied
        tags (Tuple[str]): Repository tags to apply commands to
        repositories (Tuple[str]): Repositories to apply commands to
        venv (Optional[str]): Virtualenv to execute commands with, defaults to None
        use_all (bool): Flag to indicate that CLI commands should be applied to all repositories
        verbose (bool): Flag to indicate that output should be displayed as the commands is applied
        shell (bool): Flag to indicate that commands should be executed in a separate shell
        python (bool): Flag to indicate that commands should be executed by the Python 3 interpreter
        raise_errors (bool): Flag to indicate that errors should be raised if they occur during execution and the
                             overall execution should be terminated

    Returns:
        None

    Examples:
        $ gameta cmd add -n cmd_name -c "git fetch --all --tags --prune" -c "git pull"  # Multiple shell commands
        $ gameta cmd add -n cmd_name -ve "test" -c "pip install cryptography"  # With a registered virtualenv named test
        $ gameta cmd add -n cmd_name -s -e -v -c "git fetch --all --tags --prune"  # In a separate shell, verbose,
                                                                                     terminate if errors occur
        $ gameta cmd add -n cmd_name -c "git pull" -a  # Applies to all repositories
        $ gameta cmd add -n cmd_name -c "git pull" -t test  # Applies to repositories tagged with test
        $ gameta cmd add -n cmd_name -c "git pull" -r test  # Applies to the repository named test
        $ gameta cmd add -n cmd_name -p 'print("Hello World")'  # Executes a Python script

    Raises:
        click.ClickException: If errors occur during processing
    """
    # Validate parameters
    # Tags must already be added before they can be used
    if any(t not in context.tags for t in tags):
        raise click.ClickException(
            f"One of the tags in {list(tags)} has not been added, please run `gameta tags add` to add it first"
        )
    # Repositories must already be added before they can be used
    if any(r not in context.repositories for r in repositories):
        raise click.ClickException(
            f"One of the repositories in {list(repositories)} does not exist, please run `gameta repo add` to "
            f"add it first"
        )
    # If Python flag is set, all commands must be valid Python scripts
    if python:
        try:
            for command in commands:
                compile(command, 'test', 'exec')
        except SyntaxError:
            raise click.ClickException(f"One of the commands in {list(commands)} is not a valid Python script")
    # Virtualenv must registered before it can be used
    if venv is not None and venv not in context.virtualenvs:
        raise click.ClickException(
            f"Virtualenv {venv} has not been registered, please run `gameta venv register` to register it first"
        )

    try:
        gameta_command: Dict = {
            'commands': list(commands),
            'description': description,
            'tags': list(tags),
            'repositories': list(repositories),
            'venv': venv,
            'all': use_all,
            'verbose': verbose,
            'shell': True if len(commands) > 1 else shell,
            'python': python,
            'raise_errors': raise_errors
        }

        click.echo(f"Adding command {name} with parameters ({gameta_command}) to the command store")
        if name in context.commands:
            if overwrite is True:
                click.echo(f"Overwriting command {name} in the command store")
            else:
                click.echo(f"Command {name} already exists in the command store")
                return

        context.commands[name] = gameta_command
        context.export()
        click.echo(f"Successfully added command {name} to the command store")
    except Exception as e:
        raise click.ClickException(f"{e.__class__.__name__}.{str(e)}")


@command_cli.command()
@click.option('--name', '-n', type=str, required=True, help='Name of the Gameta command to be deleted')
@gameta_context
def delete(context: GametaContext, name: str) -> None:
    """
    Deletes an existing Gameta command from the Gameta command store
    \f
    Args:
        context (GametaContext): Gameta Context
        name (str): Name of the Gameta command to be deleted

    Returns:
        None

    Examples:
        $ gameta cmd delete -n cmd_name  # Deletes an existing command

    Raises:
        click.ClickException: If errors occur during processing
    """
    click.echo(f"Deleting command {name} from the command store")
    if name not in context.commands:
        raise click.ClickException(f"Command {name} does not exist in the command store")

    try:
        del context.commands[name]
        context.export()
        click.echo(f"Successfully deleted command {name} from the command store")
    except Exception as e:
        raise click.ClickException(f"{e.__class__.__name__}.{str(e)}")


@command_cli.command()
@click.option('--name', '-n', type=str, required=True, help='Gameta command name to be added to the store')
@click.option('--command', '-c', 'commands', type=str, default=None, multiple=True,
              help='New CLI commands to be executed')
@click.option('--description', '-d', type=str, default=None, help='Brief description of the Gameta command')
@click.option('--tags', '-t', type=str, multiple=True, default=None,
              help='New repository tags to apply CLI commands to')
@click.option('--repositories', '-r', type=str, multiple=True, default=None,
              help='New repositories to apply CLI commands to')
@click.option('--venv', '-ve', 'venv', type=str, default=None, help='New virtualenv to execute commands with')
@click.option('--all/--no-all', '-a/-na', 'use_all', is_flag=True, default=None,
              help='Applies the CLI commands to all repositories, overrides the tags and repositories arguments')
@click.option('--verbose/--no-verbose', '-v/-nv', is_flag=True, default=None,
              help='Display execution output when CLI command is applied')
@click.option('--shell/--no-shell', '-s/-ns', is_flag=True, default=None,
              help='Execute CLI commands in a separate shell')
@click.option('--python/--no-python', '-p/-np', is_flag=True, default=None,
              help='Execute Python scripts using Python 3 interpreter')
@click.option('--raise-errors/--no-errors', '-e/-ne', is_flag=True, default=None,
              help='Raise errors that occur when executing CLI commands and terminate execution')
@gameta_context
def update(
        context: GametaContext,
        name: str,
        commands: Optional[Tuple[str]],
        description: Optional[str],
        tags: Optional[Tuple[str]],
        repositories: Optional[Tuple[str]],
        venv: Optional[str],
        use_all: Optional[bool],
        verbose: Optional[bool],
        shell: Optional[bool],
        python: Optional[bool],
        raise_errors: Optional[bool]
) -> None:
    """
    Updates an existing Gameta command in the Gameta command store
    \f
    Args:
        context (GametaContext): Gameta Context
        name (str): Command to be updated
        commands (Tuple[str]): CLI command to be applied
        description (Optional[str]): Brief description of CLI command
        tags (Optional[Tuple[str]]): Repository tags to apply command to
        repositories (Optional[Tuple[str]]): Repositories to apply command to
        venv (Optional[str]): Virtualenv to execute commands with
        use_all (bool): Flag to indicate that CLI commands should be applied to all repositories
        verbose (Optional[bool]): Flag to indicate that output should be displayed as the command is applied
        shell (Optional[bool]): Flag to indicate that command should be executed in a separate shell
        python (Optional[bool]): Flag to indicate that command should be executed by the Python 3 interpreter
        raise_errors (Optional[bool]): Flag to indicate that errors should be raised if they occur during execution and
                                       the overall execution should be terminated

    Returns:
        None

    Examples:
        $ gameta cmd update -n test -c "git fetch --all --tags --prune"  # Updates the CLI commands of test
        $ gameta cmd update -n test -ve test  # Updates the virtualenv of test
        $ gameta cmd update -n test -ns  # Updates test to execute in the same shell

    Raises:
        click.ClickException: If errors occur during processing
    """

    click.echo(f"Updating command {name} in the command store")
    updates: Dict = {
        'commands': commands,
        'description': description,
        'tags': tags,
        'repositories': repositories,
        'venv': venv,
        'all': use_all,
        'verbose': verbose,
        'shell': shell,
        'python': python,
        'raise_errors': raise_errors
    }
    if name not in context.commands:
        raise click.ClickException(f"Command {name} does not exist in the command store")

    try:
        updated_command: Dict = deepcopy(context.commands[name])
        for key, value in updates.items():
            # Skip invalid data
            if not (
                isinstance(value, str) or
                isinstance(value, bool) or
                (isinstance(value, tuple) and len(value) > 0)
            ):
                continue

            updated_command[key] = value

        if 'python' not in updated_command:
            updated_command['python'] = False

        if 'description' not in updated_command:
            updated_command['description'] = ''

        # Validate parameters
        # Multiple commands need to be accompanied with the shell parameter
        if len(updated_command['commands']) > 1 and updated_command['shell'] is False:
            raise click.ClickException('Multiple CLI commands requires shell param to be True')
        # Tags must already be added before they can be used
        if any(t not in context.tags for t in tags):
            raise click.ClickException(
                f"One of the tags in {list(tags)} has not been added, please run `gameta tags add` to add it first"
            )
        # Repositories must already be added before they can be used
        if any(r not in context.repositories for r in repositories):
            raise click.ClickException(
                f"One of the repositories in {list(repositories)} does not exist, please run `gameta repo add` to "
                f"add it first"
            )
        # Virtualenv must be registered before it can be used
        if updated_command['venv'] is not None and updated_command['venv'] not in context.virtualenvs:
            raise click.ClickException(
                f"Virtualenv {venv} has not been registered, please run `gameta venv register` to register it first"
            )
        # If Python flag is set, all commands need to be valid Python scripts
        if updated_command['python']:
            try:
                for command in updated_command['commands']:
                    compile(command, 'test', 'exec')
            except SyntaxError:
                raise click.ClickException(f"One of the commands in {list(commands)} is not a valid Python script")
        # If Python flag was unset, all the commands cannot be valid Python scripts
        if context.commands[name].get('python', False) is True and updated_command['python'] is False:
            for command in updated_command['commands']:
                try:
                    compile(command, 'test', 'exec')
                    raise click.ClickException(
                        f"Python flag was unset but one of the commands in {updated_command['commands']} "
                        f"is still Python compilable"
                    )
                except SyntaxError:
                    continue

        context.commands[name] = updated_command
        context.export()
        click.echo(f"Successfully updated command {name} in the command store")
    except click.ClickException:
        raise
    except Exception as e:
        raise click.ClickException(f"{e.__class__.__name__}.{str(e)}")


@command_cli.command()
@gameta_context
def ls(context: GametaContext) -> None:
    """
    Lists all commands in the Gameta command store
    \f
    Args:
        context (GametaContext): Gameta Context

    Returns:
        None

    Examples:
        $ gameta cmd ls  # Lists all the existing commands in the command store

    Raises:
        click.ClickException: If errors occur during processing
    """
    def format_command(name: str, details: Dict) -> str:
        """
        Formats a command to be printed as a string

        Args:
            name (str): Command name
            details (Dict): Command details to be printed

        Returns:
            str: Formatted command string
        """
        command_string: str = f'{name}:\n'
        param_string: str = '{}: {}\n'
        formatters: Dict[str, Callable[[Any], str]] = {
            'commands': lambda v: ' && '.join(v),
            'tags': lambda v: ', '.join(v),
            'repositories': lambda v: ', '.join(v)
        }
        for key in [
            'description', 'commands', 'tags', 'repositories', 'venv',
            'all', 'verbose', 'shell', 'python', 'raise_errors'
        ]:
            if key in details:
                command_string += '\t' + param_string.format(key, formatters.get(key, str)(details.get(key)))

        return command_string

    try:
        for command, command_details in context.commands.items():
            click.echo(format_command(command, command_details))
    except Exception as e:
        raise click.ClickException(f"{e.__class__.__name__}.{str(e)}")

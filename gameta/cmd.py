from copy import deepcopy
from typing import Tuple, Dict, Optional, Callable, Any

import click

from .cli import gameta_cli
from .context import gameta_context, GametaContext


__all__ = ['command_cli']


@gameta_cli.group('cmd')
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
@click.option('--overwrite', '-o', type=bool, is_flag=True, default=False,
              help='Overwrite existing Gameta command in the store')
@click.option('--command', '-c', 'commands', type=str, required=True, multiple=True, help='CLI Commands to be executed')
@click.option('--tags', '-t', type=str, multiple=True, default=(), help='Repository tags to apply CLI commands to')
@click.option('--repositories', '-r', type=str, multiple=True, default=(), help='Repositories to apply CLI commands to')
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
        commands: Tuple[str],
        tags: Tuple[str],
        repositories: Tuple[str],
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
        overwrite (bool): Flag to overwrite the existing Gameta command if it exists, defaults to false

        commands (Tuple[str]): CLI command to be applied
        tags (Tuple[str]): Repository tags to apply command to
        repositories (Tuple[str]): Repositories to apply command to
        verbose (bool): Flag to indicate that output should be displayed as the command is applied
        shell (bool): Flag to indicate that command should be executed in a separate shell
        python (bool): Flag to indicate that command should be executed by the Python 3 interpreter
        raise_errors (bool): Flag to indicate that errors should be raised if they occur during execution and the
                             overall execution should be terminated

    Returns:
        None

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

    try:
        gameta_command: Dict = {
            'commands': list(commands),
            'tags': list(tags),
            'repositories': list(repositories),
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
@click.option('--tags', '-t', type=str, multiple=True, default=None,
              help='New repository tags to apply CLI commands to')
@click.option('--repositories', '-r', type=str, multiple=True, default=None,
              help='New repositories to apply CLI commands to')
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
        tags: Optional[Tuple[str]],
        repositories: Optional[Tuple[str]],
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
        tags (Tuple[str]): Repository tags to apply command to
        repositories (Tuple[str]): Repositories to apply command to
        verbose (Optional[bool]): Flag to indicate that output should be displayed as the command is applied
        shell (Optional[bool]): Flag to indicate that command should be executed in a separate shell
        python (Optional[bool]): Flag to indicate that command should be executed by the Python 3 interpreter
        raise_errors (Optional[bool]): Flag to indicate that errors should be raised if they occur during execution and
                                       the overall execution should be terminated

    Returns:
        None

    Raises:
        click.ClickException: If errors occur during processing
    """

    click.echo(f"Updating command {name} in the command store")
    updates: Dict = {
        'commands': commands,
        'tags': tags,
        'repositories': repositories,
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
                isinstance(value, bool) or
                (isinstance(value, tuple) and len(value) > 0)
            ):
                continue

            updated_command[key] = value

        if 'python' not in updated_command:
            updated_command['python'] = False

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
        for key in ['commands', 'tags', 'repositories', 'verbose', 'shell', 'python', 'raise_errors']:
            if key in details:
                command_string += '\t' + param_string.format(key, formatters.get(key, str)(details.get(key)))

        return command_string

    try:
        for command, command_details in context.commands.items():
            click.echo(format_command(command, command_details))
    except Exception as e:
        raise click.ClickException(f"{e.__class__.__name__}.{str(e)}")


@command_cli.command()
@click.option('--command', '-c', 'commands', type=str, multiple=True, required=True,
              help='Gameta commands to be invoked')
@click.pass_context
def exec(context: click.Context, commands: Tuple[str]) -> None:
    """
    Executes Gameta commands from the CLI command store
    \f
    Args:
        context (click.Context): Click Context
        commands (Tuple[str]): Gameta commands to be executed

    Returns:
        None

    Raises:
        click.ClickException: If errors occur during processing
    """
    from gameta.apply import apply

    g_context: GametaContext = context.obj
    if any(c not in g_context.commands for c in commands):
        raise click.ClickException(
            f"One of the commands in {list(commands)} does not exist in the Gameta command store, please run "
            f"`gameta cmd add` to add it first"
        )

    try:
        click.echo(f"Executing {list(commands)}")
        for command in commands:
            click.echo(f"Executing Gameta command {command}")
            context.invoke(apply, **g_context.commands[command])
    except Exception as e:
        raise click.ClickException(f"{e.__class__.__name__}.{str(e)}")

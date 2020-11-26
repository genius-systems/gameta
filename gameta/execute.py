from typing import Tuple, Dict

import click

from gameta.context import GametaContext
from gameta.cli import gameta_cli


__all__ = ['execute']


@gameta_cli.command("exec")
@click.option('--command', '-c', 'commands', type=str, multiple=True, required=True,
              help='Gameta commands to be invoked')
@click.pass_context
def execute(context: click.Context, commands: Tuple[str]) -> None:
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
    def get_command(command_name: str) -> Dict:
        """
        Structures a command for execution

        Args:
            command_name (str): Command to be executed

        Returns:
            Dict: Structured command output
        """
        mapping: Dict[str, str] = {
            'commands': 'commands',
            'tags': 'tags',
            'repositories': 'repositories',
            'venv': 'venv',
            'all': 'use_all',
            'verbose': 'verbose',
            'raise_errors': 'raise_errors',
            'python': 'python',
            'shell': 'shell'
        }
        return {
            v: g_context.commands[command_name][k]
            for k, v in mapping.items()
        }

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
            context.invoke(apply, **get_command(command))
    except Exception as e:
        raise click.ClickException(f"{e.__class__.__name__}.{str(e)}")

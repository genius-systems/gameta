
from os import getcwd, chdir
from os.path import abspath

import click

from .context import gameta_context, GametaContext
from gameta import __version__


__all__ = [
    # Gameta CLI
    'gameta_cli'
]


@click.group('gameta', invoke_without_command=True)
@click.option('--project-dir', '-d', type=str, default=getcwd())
@click.option('--version', '-v', is_flag=True, default=False)
@gameta_context
def gameta_cli(context: GametaContext, project_dir: str, version: bool) -> None:
    """
    Gameta CLI, contains commands to simplify your DevOps operations
    \f
    Args:
        context (GametaContext): Gameta Context
        project_dir (str): Project directory, defaults to the current working directory
        version (bool): Flag to print Gameta's version and exit

    Returns:
        None

    Examples:
        $ gameta -v  # Prints version and exits
        $ gameta -d /path/to/project/dir  # Specify a project directory
    """
    if version:
        click.echo(f"Gameta version: {__version__}")
        return

    context.project_dir = abspath(project_dir)
    chdir(context.project_dir)

    # Load current repositories
    context.load()


from .init import *
from .repos import *
from .tags import *
from .apply import *
from .params import *
from .cmd import *
from .constants import *

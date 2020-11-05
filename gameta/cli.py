
from os import getcwd, chdir
from os.path import abspath

import click

from .context import gameta_context, GametaContext

__all__ = [
    # Gameta CLI
    'gameta_cli'
]


@click.group('gameta')
@click.option('--project-dir', '-d', type=str, default=getcwd())
@gameta_context
def gameta_cli(context: GametaContext, project_dir: str) -> None:
    """
    Genisys DevOps CLI, contains all commands that simplify Genisys DevOps operations
    \f
    Args:
        context (GametaContext): DevOps Context
        project_dir (str): Project directory, defaults to the current working directory

    Returns:
        None

    Examples:
        $ gameta  # Use all default values
        $ gameta -d /path/to/project/dir  # Specify a project directory
    """
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

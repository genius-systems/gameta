import json
from os.path import splitext, basename
from typing import Dict

import click

from git import Repo

from . import gameta_cli, gameta_context, GametaContext


__all__ = ['init']


@gameta_cli.command()
@click.option('--git', '-g', is_flag=True, default=False, help='Flag to initialise the current directory as a git repo')
@click.option('--overwrite', '-o', is_flag=True, default=False, help='Flag to overwrite existing .meta file')
@gameta_context
def init(context: GametaContext, overwrite: bool, git: bool) -> None:
    """
    Initialises a repository as a metarepo
    \f
    Args:
        context (GametaContext): Gameta Context
        overwrite (bool): Flag to indicate if existing .meta file should be overwritten
        git (bool): Flag to indicate if we should initialise git in the current directory

    Returns:
        None

    Examples:
        $ gameta init  # With default values
        $ gameta init -g  # Initialises the current working directory as a git repository
        $ gameta init -o  # Overwrites the existing .meta file if it exists
    """
    click.echo(f"Initialising metarepo in {context.project_dir}")

    repo: Repo = Repo(context.project_dir)
    name: str = splitext(basename(repo.remote().url))[0]

    if not context.is_metarepo:
        if repo.bare:
            if not git:
                click.ClickException(f"{context.project_dir} is not a valid git repo, initialise it with -g flag")
            click.echo(f"Initialising {context.project_dir} as a git repo")
            repo.init()
    else:
        if not overwrite:
            click.echo(f"{context.project_dir} is a metarepo, ignoring")
            return

    context.repositories[name] = {
        'url': repo.remote().url,
        'path': '.',
        'tags': ['meta']
    }
    context.export()
    click.secho(f"Successfully initialised {context.project_dir} as a metarepo")

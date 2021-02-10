from os.path import splitext, basename
from typing import Optional

import click

from git import Repo, InvalidGitRepositoryError

from gameta.base import gameta_context, GametaContext


__all__ = ['init']


@click.command()
@click.option('--git', '-g', is_flag=True, default=False, help='Flag to initialise the current directory as a git repo')
@click.option('--overwrite', '-o', is_flag=True, default=False, help='Flag to overwrite existing .gameta file')
@gameta_context
def init(context: GametaContext, overwrite: bool, git: bool) -> None:
    """
    Initialises a repository as a metarepo
    \f
    Args:
        context (GametaContext): Gameta Context
        overwrite (bool): Flag to indicate if existing .gameta file should be overwritten
        git (bool): Flag to indicate if we should initialise git in the current directory

    Returns:
        None

    Examples:
        $ gameta init  # With default values
        $ gameta init -g  # Initialises the current working directory as a git repository
        $ gameta init -o  # Overwrites the existing .gameta file if it exists

    Raises:
        click.ClickException: If errors occur during processing
    """
    click.echo(f"Initialising metarepo in {context.project_dir}")

    try:
        repo: Repo = Repo(context.project_dir)
        name: str = splitext(basename(repo.remote().url))[0]
        url: Optional[str] = repo.remote().url
    except InvalidGitRepositoryError:
        if git is False:
            raise click.ClickException(f"{context.project_dir} is not a valid git repo, initialise it with -g flag")
        click.echo(f"Initialising {context.project_dir} as a git repository")
        Repo.init(context.project_dir)
        name: str = basename(context.project_dir)
        url: Optional[str] = None
    except Exception as e:
        raise click.ClickException(f"{e.__class__.__name__}.{str(e)}")

    try:
        if context.is_metarepo and overwrite is False:
            click.echo(f"{context.project_dir} is a metarepo, ignoring")
            return

        context.repositories[name] = {
            'url': url,
            'path': '.',
            'tags': ['metarepo'],
            '__metarepo__': True
        }
        context.export()
        click.echo(f"Successfully initialised {name} as a metarepo")
    except Exception as e:
        raise click.ClickException(f"{e.__class__.__name__}.{str(e)}")

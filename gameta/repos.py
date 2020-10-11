import json
from os.path import join, normpath, exists
from typing import Dict, Optional

import click
from git import Repo, GitError

from . import gameta_cli, gameta_context, GametaContext


__all__ = ['repo_cli']


@gameta_cli.group('repos')
def repo_cli() -> None:
    """
    CLI for managing repos in metarepos
    \f
    Returns:
        None
    """


@repo_cli.command()
@click.option('--name', '-n', type=str, help='Name of the repository to be added')
@click.option('--url', '-u', type=str, help='URL of the git repository')
@click.option('--path', '-p', type=str, help='Relative path to clone the repository to')
@click.option('--tags', '-t', type=str, multiple=True, help='Tags to add to the repository')
@click.option('--overwrite', '-o', type=str, is_flag=False,
              help='Overwrite the existing repository configuration if it exists')
@gameta_context
def add(context: GametaContext, name: str, url: str, tags: str, path: str, overwrite: bool) -> Optional[Dict]:
    """
    Adds a new repository to the metarepo
    \f
    Args:
        context (GametaContext): Gameta Context
        name (str): Name of the repository to be added
        url (str): URL of the git repository
        path (str): Local relative path to clone the repository to
        tags (str): Tags to add to the repository
        overwrite (bool): Flag to overwrite the existing repository configuration if it exists

    Returns:
        Optional[Dict]: Returns the repository details added
    """
    clone_path: str = normpath(join(context.project_dir, path))

    click.echo(f"Adding git repository {name}, {url} to {clone_path}")
    try:
        if exists(clone_path):
            repo = Repo(clone_path)
            if repo.bare:
                raise click.ClickException(f'Path {clone_path} exists, please clear it before proceeding')
            if repo.remote().url != url:
                raise click.ClickException(
                    f'URL of repository at {clone_path} ({repo.remote().url}) does not match the requested url {url}'
                )
            click.echo(f"Repository {name} exists locally, skipping clone")
        else:
            Repo.clone_from(url, clone_path)
    except GitError as e:
        raise click.ClickException(f'Error cloning {name} into directory {path}: {e.__class__.__name__}.{str(e)}')

    click.echo(f"Repository {name} has been added locally")
    if name in context.repositories:
        click.echo(f"Repository {name} has already been added to .meta file")
        if overwrite is True:
            click.echo(f"Overwriting repository {name} in .meta file")
    else:
        click.echo(f"Adding {name} to .meta file")
        context.repositories[name] = {
            'url': url,
            'path': path,
            'tags': tags
        }
        context.generate_tags()
        context.export()

    click.echo(f"Successfully added repository {name}")
    return context.repositories[name]

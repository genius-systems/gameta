from copy import deepcopy
from os.path import join, normpath, exists
from shutil import rmtree, copytree
from typing import Dict, Optional

import click
from git import Repo, GitError

from .cli import gameta_cli
from .context import gameta_context, GametaContext


__all__ = ['repo_cli']


@gameta_cli.group('repo')
@gameta_context
def repo_cli(context: GametaContext) -> None:
    """
    CLI for managing repos in metarepos
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


@repo_cli.command()
@click.option('--name', '-n', type=str, required=True, help='Name of the repository to be added')
@click.option('--url', '-u', type=str, required=True, help='URL of the git repository')
@click.option('--path', '-p', type=str, required=True, help='Relative path to clone the repository to')
@click.option('--overwrite', '-o', is_flag=True, default=False,
              help='Overwrite the existing repository configuration if it exists, defaults to false')
@gameta_context
def add(context: GametaContext, name: str, url: str, path: str, overwrite: bool) -> Optional[Dict]:
    """
    Adds a new repository to the metarepo
    \f
    Args:
        context (GametaContext): Gameta Context
        name (str): Name of the repository to be added
        url (str): URL of the git repository
        path (str): Local relative path to clone the repository to
        overwrite (bool): Flag to overwrite the existing repository configuration if it exists, defaults to false

    Returns:
        Optional[Dict]: Returns the repository details added

    Examples:
        $ gameta repo add -n repo_name -u https://github.com/git_user/repo_name.git -p path/to/repo
        $ gameta repo add -n repo_name -u https://github.com/git_user/repo_name.git -p path/to/repo -o

    Raises:
        click.ClickException: If errors occur during processing
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
        raise click.ClickException(f'Error cloning {name} into directory {clone_path}: {e.__class__.__name__}.{str(e)}')

    try:
        click.echo(f"Repository {name} has been added locally")
        if name in context.repositories:
            if overwrite is True:
                click.echo(f"Overwriting repository {name} in .meta file")
            else:
                click.echo(f"Repository {name} has already been added to .meta file")
                return
        else:
            click.echo(f"Adding {name} to .meta file")

        context.repositories[name] = {
            'url': url,
            'path': path,
            '__metarepo__': False
        }
        context.add_gitignore(path)
        context.export()

        click.echo(f"Successfully added repository {name}")
        return context.repositories[name]
    except Exception as e:
        raise click.ClickException(f"{e.__class__.__name__}.{str(e)}")


@repo_cli.command()
@click.option('--name', '-n', type=str, required=True, help='Name of the repository to be deleted')
@click.option(' /--no-clear', ' /-c', 'clear', is_flag=True, default=True,
              help='Do not clear the repository folder locally')
@gameta_context
def delete(context: GametaContext, name: str, clear: bool) -> None:
    """
    Deletes the repository from the .meta file and locally if specified
    \f
    Args:
        context (GametaContext): Gameta Context
        name (str): Name of the repository to be deleted
        clear (bool): Flag to indicate if repository should be cleared locally, defaults to true

    Returns:
        None

    Examples:
        $ gameta repo delete -n repo_name
        $ gameta repo delete -n repo_name -c  # Does not clear local repository

    Raises:
        click.ClickException: If errors occur during processing
    """
    try:
        click.echo(f"Deleting repository {name} from .meta file")
        if name not in context.repositories:
            click.echo(f"Repository {name} does not exist in the .meta file, ignoring")
            return

        # Prevent user from deleting primary metarepo
        if context.is_primary_metarepo(name):
            raise click.ClickException(f"Cannot delete repository {name} as it is a metarepo")

        if clear:
            click.echo(f"Clearing repository {name} locally")
            rmtree(join(context.project_dir, context.repositories[name]["path"]), ignore_errors=True)

        context.remove_gitignore(context.repositories[name]["path"])
        del context.repositories[name]
        context.export()
        click.echo(f"Repository {name} successfully deleted")
    except click.ClickException:
        raise
    except Exception as e:
        raise click.ClickException(f"{e.__class__.__name__}.{str(e)}")


@repo_cli.command()
@click.option('--name', '-n', type=str, required=True, help='Name of the repository to be updated')
@click.option('--new-name', '-e', type=str, default=None, help='New repository name to update to')
@click.option('--new-url', '-u', type=str, default=None, help='New repository URL')
@click.option('--new-path', '-p', type=str, default=None,
              help='New relative path to clone the repository to')
@click.option(' /--no-sync', ' /-s', 'sync', is_flag=True, default=True, help='Does not sync all updates locally')
@gameta_context
def update(
        context: GametaContext,
        name: str,
        new_name: Optional[str],
        new_url: Optional[str],
        new_path: Optional[str],
        sync: Optional[bool],
) -> None:
    """
    Updates the key parameters defining a repository
    \f
    Args:
        context (GametaContext): Gameta Context
        name (str): Name of the repository to be updated
        new_name (Optional[str]): New repository name
        new_url (Optional[str]): New repository URL
        new_path (Optional[str]): New relative path
        sync (bool): Sync all updates, defaults to True

    Returns:
        None

    Examples:
        $ gameta repo update -n orig_repo_name -e new_repo_name -u https://github.com/git_user/repo_name.git
                             -p /path/to/repo
        $ gameta repo update -n orig_repo_name -e new_repo_name -u https://github.com/git_user/repo_name.git
                             -p /path/to/repo -s  # Does not sync local changes

    Raises:
        click.ClickException: If errors occur during processing
    """
    if name not in context.repositories:
        raise click.ClickException(f"Repository {name} does not exist in the .meta file, please add it first")

    try:
        click.echo(f"Updating repository {name} with new details (name: {new_name}, url: {new_url}, path: {new_path})")
        curr_repo_details: Dict = context.repositories[name]

        # Update the details
        new_repo_details: Dict = deepcopy(context.repositories[name])
        for key, value in [('url', new_url), ('path', new_path)]:
            if value is not None:
                new_repo_details[key] = value

        if new_name is not None:
            del context.repositories[name]
            name = new_name

        # Perform a physical sync with the updated details
        if sync:
            click.echo("Performing a physical sync")
            if new_url is not None:
                # Only URL changes, need to clear the existing path and clone repository
                click.echo(f"Cloning repository from new URL: {new_url}")
                rmtree(join(context.project_dir, curr_repo_details['path']), ignore_errors=True)
                Repo.clone_from(new_url, normpath(join(context.project_dir, new_repo_details['path'])))
            elif new_url is None and new_path is not None:
                # Only path changes, need to move the directory to the new location
                click.echo(f"Copying repository to new path: {new_path}")
                copytree(
                    join(context.project_dir, curr_repo_details["path"]),
                    join(context.project_dir, new_repo_details["path"])
                )
                rmtree(join(context.project_dir, curr_repo_details['path']), ignore_errors=True)
            else:
                # No physical changes
                click.echo("No physical changes")
            click.echo("Sync complete")

        # Export the updated details
        context.remove_gitignore(curr_repo_details["path"])
        context.add_gitignore(new_repo_details["path"])
        context.repositories[name] = new_repo_details
        context.export()
        click.echo(f"Successfully updated repository {name} with new details")
    except Exception as e:
        raise click.ClickException(f"{e.__class__.__name__}.{str(e)}")


@repo_cli.command()
@gameta_context
def ls(context: GametaContext) -> None:
    """
    Lists all the repositories added in the .meta file
    \f
    Args:
        context (GametaContext): Gameta Context

    Returns:
        None

    Examples:
        $ gameta repo ls

    Raises:
        click.ClickException: If errors occur during processing
    """
    click.echo(f"Listing repositories managed in metarepo {context.project_dir}")
    for repo in context.repositories:
        click.echo(f"{repo}")

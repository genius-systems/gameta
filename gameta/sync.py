import click
from git import Repo, GitError

from gameta.base import gameta_context, GametaContext


__all__ = ['sync']


@click.command()
@gameta_context
def sync(context: GametaContext) -> None:
    """
    Syncs all the repositories listed in the .gameta file locally
    \f
    Args:
        context (GametaContext): Gameta Context

    Returns:
        None

    Examples:
        $ gameta sync

    Raises:
        click.ClickException: If errors occur during processing
    """
    click.echo(f"Syncing all child repositories in metarepo {context.project_dir}")

    try:
        for repo, details in context.repositories.items():

            # We assume the metarepo has already been cloned
            if context.is_primary_metarepo(repo):
                continue

            try:
                Repo.clone_from(details['url'], details['path'])
                click.echo(f'Successfully synced {repo} to {details["path"]}')
            except GitError as e:
                click.echo(f"An error occurred {str(e)}, skipping repo")
                continue
    except Exception as e:
        raise click.ClickException(f"{e.__class__.__name__}.{str(e)}")

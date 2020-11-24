import venv
from os.path import join

import click

from gameta.cli import gameta_cli
from gameta.context import gameta_context, GametaContext


__all__ = ['venv_cli']


@gameta_cli.command("venv")
@gameta_context
def venv_cli(context: GametaContext):
    """
    CLI for managing virtualenvs in metarepos
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


@venv_cli.command()
@click.option('--directory', '-d', type=str, default='.venv', help='Relative directory to the virtual environment')
@click.option('--overwrite', '-o', is_flag=True, default=False,
              help='Flag to overwrite existing directory when virtualenv is created, defaults to false')
@click.option('--site-packages/--no-site-packages', '-s/-ns', 'site_packages', is_flag=True, default=False,
              help='Flag to include all site packages, defaults to false')
@click.option('--pip/--no-pip', '-p/-np', 'pip', is_flag=True, default=True,
              help='Flag to include pip, defaults to true')
@click.option('--symlinks/--no-symlinks', '-l/-nl', 'symlinks', is_flag=True, default=False,
              help='Flag to include pip, defaults to false')
@click.pass_context
def create(
        context: click.Context,
        directory: str,
        overwrite: bool,
        site_packages: bool,
        pip: bool,
        symlinks: bool
) -> None:
    """
    Creates a virtualenv in the specified directory with the given configuration
    \f
    Args:
        context (click.Context): Click Context
        directory (str): Relative directory to the virtualenv
        overwrite (bool): Flag to overwrite existing directory when virtualenv is created, defaults to false
        site_packages (bool): Flag to include all system site packages, defaults to false
        pip (bool): Flag to include pip in the virtualenv, defaults to true
        symlinks (bool): Flag to create symlinks to the python executable instead of actual files, defaults to False

    Returns:
        None
    """
    click.echo(
        f"Creating virtualenv in {join(context.obj.project_dir, directory)} with the following config: "
        f"(site_packages: {site_packages}, pip: {pip}, symlinks: {symlinks}, overwrite: {overwrite})"
    )
    try:
        venv.create(
            directory,
            clear=overwrite,
            with_pip=pip,
            symlinks=symlinks,
            system_site_packages=site_packages,
        )
        context.invoke(register, **{'directory': directory})
        click.echo("Successfully created virtualenv")
    except Exception as e:
        raise click.ClickException(
            f'Virtualenv creation failed with {e.__class__.__name__}.{str(e)}'
        )


@venv_cli.command()
@click.option('--directory', '-d', type=str, default='.venv', help='Directory to the virtual environment')
@gameta_context
def register(context: GametaContext, directory: str) -> None:
    """
    Creates a Genisys reference to the virtual environment
    \f
    Args:
        context (GametaContext): Gameta Context
        directory (str): Directory to the virtual environment

    Returns:
        None
    """
    if not directory:
        raise click.ClickException(f'Invalid directory {directory} provided')
    click.echo(f"Registering Virtual Environment created in {directory}")
    context
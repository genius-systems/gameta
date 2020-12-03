import venv
from os.path import join, exists
from shutil import rmtree

import click

from gameta.cli import gameta_cli
from gameta.base import gameta_context, GametaContext


__all__ = ['venv_cli']


@gameta_cli.group("venv")
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
@click.option('--name', '-n', type=str, required=True, help='Name of the virtual environment')
@click.option('--directory', '-d', type=str, default='.venv', help='Relative directory to the virtual environment')
@click.option('--overwrite', '-o', is_flag=True, default=False,
              help='Flag to overwrite existing directory when virtualenv is created, defaults to false')
@click.option('--site-packages/ ', '-s/ ', 'site_packages', is_flag=True, default=False,
              help='Flag to include all site packages, defaults to false')
@click.option(' /--no-pip', ' /-np', 'pip', is_flag=True, default=True,
              help='Flag to include pip, defaults to true')
@click.option('--symlinks/ ', '-l/ ', 'symlinks', is_flag=True, default=False,
              help='Flag to create symlinks to the python executable instead of actual files, defaults to False')
@click.pass_context
def create(
        context: click.Context,
        name: str,
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
        name (str): Name of the virtualenv
        directory (str): Relative directory to the virtualenv
        overwrite (bool): Flag to overwrite existing directory when virtualenv is created, defaults to false
        site_packages (bool): Flag to include all system site packages, defaults to false
        pip (bool): Flag to include pip in the virtualenv, defaults to true
        symlinks (bool): Flag to create symlinks to the python executable instead of actual files, defaults to False

    Examples:
        $ gameta venv create -n test  # Creates and registers a new virtualenv named test in project directory
        $ gameta venv create -n test -d venv  # Creates a new virtualenv test in directory /path/to/project_dir/venv
        $ gameta venv create -n test -o  # Creates virtualenv and overwrites existing directory
        $ gameta venv create -n test -s  # Adds all site packages to created virtualenv
        $ gameta venv create -n test -np  # Do not add pip to the created virtualenv
        $ gameta venv create -n test -l  # Use symlinks instead of a physical copy of the Python3 interpreter

    Returns:
        None

    Raises:
        click.ClickException: If errors occur during processing
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
        context.invoke(
            register, **{'name': name, 'path': join(context.obj.project_dir, directory), 'overwrite': overwrite}
        )
        click.echo(f"Successfully created virtualenv {name}")
    except Exception as e:
        raise click.ClickException(
            f'Virtualenv creation failed with {e.__class__.__name__}.{str(e)}'
        )


@venv_cli.command()
@click.option('--name', '-n', type=str, required=True, help='Name of the virtual environment')
@click.option('--path', '-p', type=str, required=True, help='Absolute path to the virtual environment')
@click.option('--overwrite', '-o', is_flag=True, default=False,
              help='Flag to overwrite a registered virtualenv, defaults to false')
@gameta_context
def register(context: GametaContext, name: str, path: str, overwrite: bool) -> None:
    """
    Stores a reference to the virtual environment in the .gameta file
    \f
    Args:
        context (GametaContext): Gameta Context
        name (str): Name of the virtualenv
        path (str): Absolute path to the virtual environment
        overwrite (bool): Flag to overwrite a registered virtualenv, defaults to false

    Returns:
        None

    Examples:
        $ gameta venv register -n test -p /path/to/venv  # Registers a virtualenv
        $ gameta venv register -n test -p /path/to/venv  # Overwrites existing virtualenv test if it exists

    Raises:
        click.ClickException: If errors occur during processing
    """
    if not exists(path):
        raise click.ClickException(f'Path {path} does not exist')
    if not (exists(join(path, 'bin', 'activate')) and exists(join(path, 'bin', 'python'))):
        raise click.ClickException(f'Path {path} is not a valid virtualenv')
    if name in context.venvs and not overwrite:
        raise click.ClickException(f'Virtualenv {name} exists and overwrite flag is {overwrite}')
    click.echo(f"Registering virtualenv in {path} as {name}")
    context.venvs[name] = path
    context.export()
    click.echo(f"Successfully registered {name}")


@venv_cli.command()
@click.option('--name', '-n', type=str, required=True, help='Name of the virtualenv')
@click.option('--delete', '-d', is_flag=True, default=False, help='Flag to indicate that virtualenv should be deleted')
@gameta_context
def unregister(context: GametaContext, name: str, delete: bool) -> None:
    """
    Creates a Genisys reference to the virtual environment
    \f
    Args:
        context (GametaContext): Gameta Context
        name (str): Name of the virtualenv
        delete (bool): Flag to indicate that virtualenv should be deleted

    Returns:
        None

    Examples:
        $ gameta venv unregister -n test  # Unregisters a virtualenv in gameta
        $ gameta venv unregister -n test -d  # Unregisters and deletes the virtualenv

    Raises:
        click.ClickException: If errors occur during processing
    """
    if name not in context.venvs:
        raise click.ClickException(f"Virtualenv {name} has not been registered")
    if delete:
        click.echo(f"Deleting virtualenv {name} in path {context.venvs[name]}")
        rmtree(context.venvs[name], ignore_errors=True)
    click.echo(f"Unregistering virtualenv {name}")
    del context.venvs[name]
    context.export()
    click.echo(f"Virtualenv {name} successfully unregistered")

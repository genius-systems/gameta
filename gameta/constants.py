import builtins
from typing import Union

import click

from .cli import gameta_cli
from .context import gameta_context, GametaContext


__all__ = ['constants_cli']


@gameta_cli.group('const')
@gameta_context
def constants_cli(context: GametaContext) -> None:
    """
    CLI for managing constants in metarepos
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


@constants_cli.command()
@click.option("--name", '-n', type=str, required=True, help='Name of the constant to stored')
@click.option("--type", '-t', 'ctype', type=click.Choice(['int', 'float', 'str', 'bool']), required=True,
              help='Type of the constant to be stored as')
@click.option('--value', '-v', type=str, required=True, help='Value of the constant to be stored')
@gameta_context
def add(context: GametaContext, name: str, ctype: str, value: str) -> None:
    """
    Adds a set of constants to the constants store

    Args:
        context (GametaContext): Gameta Context
        name (str): Name of the constant provided
        ctype (str): Type of the constant provided
        value (str): Value of the constant

    Returns:
        None

    Examples:
        $ gameta const add -n test -t str -v hello_world  # Adds constant TEST as a string to Gameta
        $ gameta const add -n test_1 -t float -v 1.0  # Adds constant TEST_1 as a float to Gameta

    Raises:
        click.ClickException: If errors occur during processing
    """
    click.echo(f"Adding constant {name}")
    constant_type: type = getattr(builtins, ctype, str)

    try:
        name: str = name.upper()
        value: Union[int, float, bool, str] = click.types.convert_type(constant_type)(value)
        context.constants[name.upper()] = value
        context.export()
        click.echo(f"Successfully added constant {name}: {value} (type: {ctype}) to .meta file")
    except Exception as e:
        raise click.ClickException(f"{e.__class__.__name__}.{str(e)}")


@constants_cli.command()
@click.option("--name", '-n', type=str, required=True, help="Name of constant to be deleted")
@gameta_context
def delete(context: GametaContext, name: str) -> None:
    """
    Deletes a Gameta constant from the constant store

    Args:
        context (GametaContext): Gameta Context
        name (str): Name of the constant to be deleted

    Returns:
        None

    Examples:
        $ gameta const delete -n test  # Deletes the TEST constant from the constant store

    Raises:
        click.ClickException: If errors occur during processing
    """
    click.echo(f"Deleting constant {name}")
    try:
        if name in context.constants:
            del context.constants[name]
        elif name.upper() in context.constants:
            del context.constants[name.upper()]
        else:
            raise click.ClickException(f"Constant {name} does not exist in .meta file")

        context.export()
        click.echo(f"Successfully deleted constant {name} from .meta file")
    except click.ClickException:
        raise
    except Exception as e:
        raise click.ClickException(f'{e.__class__.__name__}.{str(e)}')

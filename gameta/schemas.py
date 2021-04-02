import json
from os import getcwd
from os.path import join
from pprint import pformat
from typing import Dict, Optional

import click
from jsonschema import Draft7Validator, ValidationError

from gameta import __version__
from gameta.base import Schema, supported_versions, to_schema_tuple
from gameta.base.schemas.schema import to_schema_str

__all__ = ["schema_cli"]


@click.group("schema", invoke_without_command=True)
@click.option(
    "--schema-version",
    "-s",
    "version",
    type=str,
    default=None,
    help=".gameta schema version to print",
)
def schema_cli(version: Optional[str]) -> None:
    """
    CLI for .gameta schemas, prints a specified version if provided
    \f
    Args:
        version (Optional[str]): Version of the schema to be printed

    Returns:
        None
    """
    if version is not None:
        if to_schema_tuple(version) not in supported_versions:
            raise click.ClickException(
                f"Gameta schema version {version} is not supported by Gameta version {__version__}"
            )

        click.echo(f"Printing schema version {version}:")
        click.echo(pformat(supported_versions[to_schema_tuple(version)].schema))


@schema_cli.command()
@click.option(
    "--path",
    "-p",
    type=str,
    default=None,
    help="Absolute path to directory containing .gameta folder to validate",
)
@click.option(
    "--verbose", "-v", is_flag=True, default=False, help="Prints verbose error details"
)
@click.option(
    "--schema-version",
    "-s",
    "version",
    type=str,
    default=None,
    help=".gameta schema version to validate against, defaults to None",
)
def validate(path: str, verbose: bool, version: Optional[str]) -> None:
    """
    Validates the .gameta data against a specified schema version
    \f
    Args:
        path (str): Absolute path to project directory containing .gameta folder
        verbose (bool): Prints verbose error details
        version (str): .gameta schema version to validate against

    Returns:
        None

    Raises:
        click.ClickException: If .gameta file could not be loaded
        click.ClickException: If .gameta version is not supported

    Examples:
        $ gameta schema validate -p path/to/file  # Validate .gameta file in a specific directory
        $ gameta schema validate -v  # Validate with verbose error details
        $ gameta schema validate -s  # Validate against a specific schema version
    """
    # Import .gameta data
    gameta_path: str = join(path if path else getcwd(), ".gameta", ".gameta")
    try:
        with open(gameta_path) as f:
            gameta_data: Dict = json.load(f)
    except Exception as e:
        raise click.ClickException(
            f"Could not load .gameta data from path {gameta_path} provided due to {e.__class__.__name__}.{str(e)}"
        )

    # Get schema version to validate against, defaults to version specified in the .gameta file
    version: str = version or gameta_data["version"]

    # Handle case where gameta version does not support schema context
    if to_schema_tuple(version) not in supported_versions:
        raise click.ClickException(
            f"Gameta schema version {version} is not supported by Gameta version {__version__}"
        )

    click.echo(f"Validating .gameta schema found in {gameta_path}")
    schema: Schema = supported_versions[to_schema_tuple(version)]
    errors: Dict[str, Dict[str, str]] = {}
    validators: Dict[str, Draft7Validator] = schema.validators

    # Iterate over all the schema definitions
    for section in schema.schema["definitions"]:
        if section in gameta_data:

            # Validate each entry independently for thoroughness and collect errors
            for entry_name, entry_data in gameta_data[section].items():
                try:
                    if isinstance(entry_data, dict):
                        validators[section].validate(entry_data)
                    else:
                        validators[section].validate({entry_name: entry_data})
                except ValidationError as e:
                    if section not in errors:
                        errors[section] = {}
                    errors[section][
                        entry_name
                    ] = f"{e.__class__.__name__} {str(e) if verbose else e.message}"

    # Print the errors if there are any
    if errors:
        click.echo(
            f"Validation errors associated with .gameta schema found in {gameta_path}"
        )
        for section_name, section in errors.items():
            click.echo(f"Section {section_name}:")
            for entry_name, error in section.items():
                click.echo(f"\tEntry: {entry_name}, error: {error}")

    else:
        click.echo(
            f"There are no validation errors associated with .gameta schema found in {gameta_path}"
        )


@schema_cli.command()
def ls() -> None:
    """
    Lists all the schema versions that the current version of gameta supports
    \f
    Returns:
        None

    Raises:
        click.ClickException: If errors occur during processing
    """
    click.echo(
        f"Supported schema versions: "
        f"{', '.join([to_schema_str(version) for version in supported_versions])}"
    )

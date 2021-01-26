import json
from os import getcwd
from os.path import join
from typing import Tuple, List, Dict

import click
from jsonschema import Draft7Validator, ValidationError

from gameta import __version__
from gameta.cli import gameta_cli
from gameta.base import supported_versions, Schema, get_schema_version


__all__ = ['schema_cli']


@gameta_cli.group('schema')
def schema_cli() -> None:
    """
    CLI for managing .gameta schemas
    \f

    Returns:
        None

    Raises:
        click.ClickException: If we are not currently operating in a metarepo directory
    """


@schema_cli.command()
@click.option('--path', '-p', type=str, default=None,
              help='Absolute path to directory containing .gameta file to validate')
@click.option('--verbose', '-v', is_flag=True, default=False, help='Prints verbose error details')
def validate(path: str, verbose: bool) -> None:
    """
    Validates the .gameta schema version
    \f
    Args:
        path (str): Absolute path to .gameta schema to validate
        verbose (bool): Prints verbose error details

    Returns:
        None
    """
    # Import .gameta data
    gameta_path: str = join(path if path else getcwd(), '.gameta')
    try:
        with open(gameta_path) as f:
            gameta_data: Dict = json.load(f)
    except Exception as e:
        raise click.ClickException(
            f"Could not load .gameta data from path {gameta_path} provided due to {e.__class__.__name__}.{str(e)}"
        )

    # Handle case where gameta version does not support schema context
    if get_schema_version(gameta_data['version']) not in supported_versions:
        raise click.ClickException(
            f"Gameta schema version {gameta_data['version']} is not supported by Gameta version {__version__}"
        )

    click.echo(f"Validating .gameta schema found in {gameta_path}")
    schema: Schema = supported_versions[get_schema_version(gameta_data['version'])]
    errors: Dict[str, Dict[str, str]] = {}
    validators: Dict[str, Draft7Validator] = schema.validators

    # Iterate over all the schema definitions
    for section in schema.schema['definitions']:
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
                    errors[section][entry_name] = f'{e.__class__.__name__} {str(e) if verbose else e.message}'

    # Print the errors if there are any
    if errors:
        click.echo(f"Validation errors associated with .gameta schema found in {gameta_path}")
        for section_name, section in errors.items():
            click.echo(f"Section {section_name}:")
            for entry_name, error in section.items():
                click.echo(f"\tEntry: {entry_name}, error: {error}")

    else:
        click.echo(f"There are no validation errors associated with .gameta schema found in {gameta_path}")


@schema_cli.command()
@click.option('--version', '-v', type=str, required=True, help='.gameta schema version to upgrade to')
@click.option('--path', '-p', type=str, default=None,
              help='Absolute path to directory containing .gameta file to validate')
def update(version: str, path: str) -> None:
    """
    Updates the current schema version to the selected .gameta schema version (only updates to the minor version), does
    not support downgrades.
    \f
    Args:
        version (str): .gameta schema version to upgrade to
        path (str): Absolute path to .gameta schema to validate

    Returns:
        None

    Raises:
        click.ClickException: If any errors occur during processing
    """
    # Import .gameta data
    gameta_path: str = join(path if path else getcwd(), '.gameta')
    try:
        with open(gameta_path) as f:
            gameta_data: Dict = json.load(f)
        curr_version_str: str = gameta_data.get('version', '0.2.5')
        curr_version: Tuple[int, int, int] = get_schema_version(curr_version_str)
    except Exception as e:
        raise click.ClickException(
            f"Could not load .gameta data from path {gameta_path} provided due to {e.__class__.__name__}.{str(e)}"
        )

    # Validate current .gameta file and data
    if curr_version not in supported_versions:
        raise click.ClickException(
            f"Current version of .gameta file ({curr_version_str}) is not supported by gameta version {__version__}"
        )

    if not supported_versions[curr_version].validators['gameta'].is_valid(gameta_data):
        raise click.ClickException(
            ".gameta data is invalid, run `gameta schema validate` to debug this before updating"
        )

    # Extract desired schema
    try:
        desired_version: Tuple[int, int, int] = get_schema_version(version)
    except Exception:
        raise click.ClickException(f"Invalid version string {version} provided")

    schema_ascending: List[Tuple[int, int, int]] = list(supported_versions)

    # Check if schema is supported
    if desired_version not in supported_versions:
        raise click.ClickException(f"Desired version {version} does not exist")

    # Prevent downgrading
    for i in range(3):
        if desired_version[i] > curr_version[i]:
            break
        elif desired_version[i] == curr_version[i]:
            continue
        else:
            raise click.ClickException(
                f"Desired version {version} is smaller than current version {curr_version_str}, "
                f"downgrading is not supported"
            )

    click.echo(f"Updating current Gameta schema ({curr_version_str}) to version {version}")
    try:
        # Incrementally upgrade the schema
        for version in schema_ascending[
            schema_ascending.index(curr_version) + 1:
            schema_ascending.index(desired_version)
        ]:
            schema: Schema = supported_versions[version]

            # Set the schema version
            gameta_data['version'] = version
            structure: Dict[str, Dict] = schema.structures
            validators: Dict[str, Draft7Validator] = schema.validators

            # Iterate over all the schema sections
            for section in schema.schema['definitions']:
                if section in gameta_data:
                    # Apply default schema changes to each entry of the existing schema
                    for entry_name, entry_data in gameta_data[section].items():
                        entry_data.update(structure.get(section, {}))

                    # Validate changes
                    validators[section].validate(gameta_data[section])

        # Export the finalised changes
        with open(gameta_path, 'w') as f:
            json.dump(gameta_data, f)
        click.echo(f"Successfully updated schema from {curr_version_str} to {version}")
    except Exception as e:
        raise click.ClickException(
            f"Error {e.__class__.__name__}.{str(e)} updating schema from {curr_version_str} to {version}"
        )

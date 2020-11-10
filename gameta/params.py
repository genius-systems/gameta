import builtins
import json
from typing import Type, Optional, TypeVar

import click

from .cli import gameta_cli
from .context import gameta_context, GametaContext


__all__ = ['parameters_cli']


T = TypeVar('T', int, float, str, bool, dict, list)


@gameta_cli.group('params')
@gameta_context
def parameters_cli(context: GametaContext) -> None:
    """
    CLI for managing parameters in metarepos
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


@parameters_cli.command()
@click.option('--param', '-p', type=str, required=True, help="Parameter name to be added to all child repositories")
@click.option('--type', '-t', 'ptype', type=click.Choice(['int', 'float', 'str', 'bool', 'dict', 'list']),
              default='str', help='Parameter type to be added')
@click.option('--value', '-v', type=str, default=None, help="Default value to be used for all child repositories")
@click.option('--skip-prompt', '-y', 'skip_prompt', is_flag=True, default=False,
              help="Skip user prompt and use default values for all")
@gameta_context
def add(context: GametaContext, param: str, ptype: Optional[str], value: Optional[str], skip_prompt: bool) -> None:
    """
    Adds/updates a parameter to all child repositories in the .meta file, users will automatically be prompted to enter
    the parameter value corresponding to each repository. They can provide a type and value parameter to skip this step.
    \f
    Args:
        context (GametaContext): Gameta Context
        param (str): Parameter name to be added to all child repositories
        ptype (Optional[str]): Parameter type to be added
        value (Optional[str]): Default value to be used for all child repositories, value will be rendered with type
                               chosen
        skip_prompt (bool): Flag to indicate if user prompt to enter values for all repositories should be skipped and
                            default value used directly

    Returns:
        None

    Examples:
        $ gameta parameters add -p test -t str -v hello_world  # Adds parameter test with value hello_world to all repos
        $ gameta parameters add -p test -t str -v hello_world -u  # Prompts user input for parameter values

    Raises:
        click.ClickException: If errors occur during processing
    """
    click.echo(f"Adding parameter {param}")
    parameter_type: Type[T] = getattr(builtins, ptype, str)

    def prompt_type_parser(input_value: str) -> T:
        """
        Parser to convert the user inputs into the appropriate type
        
        Args:
            input_value (str): Input received from the command line

        Returns:
            (int, float, str, bool, list, dict): Output parsed into the correct type
        """
        try:
            return json.loads(input_value)
        except json.JSONDecodeError:
            return parameter_type(input_value)

    try:
        for repo, details in context.repositories.items():
            if skip_prompt:
                pvalue: parameter_type = value
            else:
                pvalue: parameter_type = click.prompt(
                    f"Please enter the parameter value for repository {repo} or >* to skip", default=value,
                    value_proc=prompt_type_parser
                )
                if pvalue == ">*":
                    click.echo(f"Skip token was entered, defaulting to default value {value}")
                    pvalue = value
                elif not isinstance(pvalue, parameter_type):
                    click.echo(f"Value {pvalue} (type: {type(pvalue)}) entered is not the required type "
                               f"{parameter_type}, defaulting to default value {value}")
                    pvalue = value
            details[param] = pvalue
            click.echo(f"Adding {param} value {pvalue} for {repo}")
        context.export()
        click.echo(f"Successfully added parameter {param} to .meta file")
    except Exception as e:
        raise click.ClickException(f"{e.__class__.__name__}.{str(e)}")


@parameters_cli.command()
@click.option('--param', '-p', type=str, required=True,
              help="Parameter name to be deleted from all child repositories")
@gameta_context
def delete(context: GametaContext, param: str) -> None:
    """
    Deletes a parameter from all child repositories
    \f
    Args:
        context (GametaContext): Gameta Context
        param (str): Parameter name to be deleted from all child repositories

    Returns:
        None

    Raises:
        click.ClickException: If errors occur during processing
    """
    if param in context.reserved_params['repositories']:
        raise click.ClickException(
            f"Parameter {param} is a reserved parameter {context.reserved_params['repositories']}"
        )

    try:
        click.echo(f"Deleting parameter {param}")
        for repo, details in context.repositories.items():
            try:
                del details[param]
            except KeyError:
                continue
        context.export()
        click.echo(f"Successfully deleted parameter {param} from .meta file")
    except Exception as e:
        raise click.ClickException(f"{e.__class__.__name__}.{str(e)}")

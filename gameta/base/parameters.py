import subprocess
import shlex

import regex as re
from typing import Dict, Any, Optional

from .env import SHELL
from .errors import CommandError


__all__ = ['Parameter']


_sentinel_dict: Dict = {}


class Parameter(object):
    """
    Class for encapsulating Gameta Parameters and performing substitutions on them before they are substituted into
    Gameta Commands

    Attributes:
        pattern (regex.Pattern): Regex pattern
        template (str): Template string to perform substitution on
    """

    pattern: re.regex.Pattern = re.compile(
        r"""
        {
          (?:
            (?P<escaped>\{.*\})                            |  # For escaped characters
            (?P<constructs>
              (?P<shell>__shell__\s*:\s*(?P<shell_val>.*?)) |  # For shell commands
              (?P<param>\$?[A-Za-z0-9_-]+)                 |  # For parameters and constants
            )                                              |
            (?P<or>((?&constructs)\|?)*)               |  # For or logic that comprises of recursive constructs
            (?P<invalid>.*?)                                  # For invalid statements
          )                                                     
        }
        """,
        re.VERBOSE
    )

    def __init__(self, template: str):
        self.template = template

    def substitute(self, mapping: Dict[str, Any]=_sentinel_dict, **kwargs: Dict[str, Any]) -> str:
        """
        Substitutes the parameters provided in the mapping dictionary and kwargs provided into the template string

        Args:
            mapping Dict[str, Any]: Mapping dictionary, defaults to an empty dictionary
            **kwargs Dict[str, Any]: Generic kwargs parameters

        Returns:

        """
        # Generate consolidated mapping dictionary
        if mapping is _sentinel_dict:
            mapping = {}
        mapping.update(kwargs)

        def handle(match: re.regex.Match) -> Optional[str]:
            """
            Handles the value for a single match instance

            Args:
                match (regex.Match): A regex match instance

            Returns:
                Optional[str]: Value for a match instance

            Raises:
                CommandError: If specified parameter does not exist
            """
            # Evaluate output of shell commands
            if match.group('shell') is not None:
                return subprocess.check_output(
                    shlex.split(rf"""{SHELL} -c '{match.group('shell_val')}'""")
                ).decode().strip()

            # Retrieve parameter from parameter dictionary
            elif match.group('param') is not None:
                param: str = match.group('param')
                try:
                    return str(mapping[param])
                except KeyError:
                    raise CommandError(f"Parameter {param} was not provided")

        def parse(match: re.regex.Match) -> str:
            """
            Function to parse each individual match found in the function
            
            Args:
                match (regex.Match): A regex match instance

            Returns:
                str: Parsed string value

            Raises:
                CommandError: None of the parameters in 'or' could be evaluated
                CommandError: Invalid parameter
            """
            # Ignore escaped characters
            if match.group('escaped') is not None:
                return match.group('escaped')

            # Handle shell and param groups
            elif match.group('shell') or match.group('param'):
                return handle(match)

            # Handle or group
            elif match.group('or') is not None:

                # Evaluate each match and return the parameter that evaluated first
                for g in match.group('or').split('|'):
                    try:
                        output: Optional[str] = self.pattern.sub(handle, '{' + g + '}')
                        if output:
                            return output

                    # Ignore errors and proceed to the next
                    except CommandError:
                        continue

                # Raise an error if none of the parameters could be evaluated
                raise CommandError(
                    f"None of the parameters specified in {match.group('or').split('|')} could be evaluated"
                )

            # Handle invalid parameters
            else:
                raise CommandError(f"Invalid parameter(s): {match.group('invalid')}")

        return self.pattern.sub(parse, self.template)

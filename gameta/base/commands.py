import shlex
from contextlib import contextmanager
from copy import deepcopy
from dataclasses import dataclass
from os import getcwd, chdir
from os.path import join, normpath
from typing import List, Dict, Optional, Tuple, Generator, Any, Union

from .env import SHELL, ENV_VARS
from .errors import CommandError
from .parameters import Parameter


__all__ = ['CommandConfig', 'GametaCommand', 'Runner']


@dataclass
class CommandConfig:
    """
    Holds the configuration parameters for a set of Gameta Commands

    Attributes:
        debug (bool): Flag to print debug messages
        sep (str): Shell separator to be used
        shell (bool): Flag to indicate that shell generator should be used
        venv (Optional[str]): Indicates that virtualenv generator should be used
    """
    shell: bool = False
    debug: bool = False
    sep: str = "&&"
    venv: Optional[str] = None

    def __getitem__(self, item):
        return self.__dict__[item]


class GametaCommand(object):
    """
    Handles a set of Gameta Commands, providing functionality to prepare parameters, render commands with these
    parameters and generate the commands according to the given configuration.

    Attributes:
        commands (List[str]): List of pre-rendered bash commands
        params (Dict): Parameters to substitute into bash commands
        config (Command.Config): Configuration class that holds all the relevant rendering configurations
    """

    def __init__(self, commands: List[str], params: Dict, config: CommandConfig):
        self.commands: List[str] = commands
        self.params: Dict = params
        self.config: CommandConfig = config
        self.separators: Dict[str, str] = {';': '; ', '&&': ' && ', '||': ' || '}

    @contextmanager
    def generate(self) -> List[str]:
        """
        Pipeline for generating commands based on the configuration provided

        Returns:
            List[str]: Tokenised commands prepared for subprocess execution
        """
        # Perform parameter substitutions
        substituted_commands: List[str] = self.substitute()

        # Prepare commands according to configuration provided
        if self.config.venv:
            prepared_command: str = self.shell(self.virtualenv(substituted_commands))
        elif self.config.shell:
            prepared_command: str = self.shell(substituted_commands)
        else:
            prepared_command: str = f'{self.separators[self.config.sep]}'.join(substituted_commands)

        # Tokenise results for subprocess execution
        yield self.tokenise(prepared_command)

    def substitute(self) -> List[str]:
        """
        Substitutes the commands with the parameter set provided

        Returns:
            List[str]: Set of commands post-substitution
        """
        try:
            return [Parameter(c).substitute(**self.params) for c in deepcopy(self.commands)]
        except Exception as e:
            raise CommandError(f"Parameter {str(e)} was not provided")

    def virtualenv(self, commands: List[str]) -> List[str]:
        """
        Prepares commands to be executed by a virtualenv by sourcing it prior to execution

        Args:
            commands (List[str]): List of commands to be prepared

        Returns:
            List[str]: Prepared commands to be executed by subprocess
        """
        return [f". {join(self.config.venv, 'bin', 'activate')}"] + commands

    def shell(self, commands: List[str]) -> str:
        """
        Prepares commands to be executed in a separate shell as subprocess does not natively handle piping or multiple
        commands

        Args:
            commands (List[str]): List of commands to be prepared

        Returns:
            str: Prepared command string
        """
        return rf"""{SHELL} -c '{f'{self.separators[self.config.sep]}'.join(commands)}'"""

    @staticmethod
    def tokenise(command: str) -> List[str]:
        """
        Tokenises the commands into a form that is readily acceptable by subprocess

        Args:
            command (str): Constructed commands to be tokenised

        Returns:
            List[str]: Tokenised commands
        """
        return shlex.split(command)


class Runner(object):
    """
    Runner class that encapsulates the execution of all Gameta Commands from parameter generation to command generation.

    Attributes:
        project_dir (str): Absolute path to the project directory
        repositories (Dict[str, Dict[str, Any]]): Repository details
        virtualenvs (Dict[str, str]): Virtualenv data
        constants (Dict[str, Union[str, int, float, bool]]): Gameta constants
    """

    def __init__(
            self,
            project_dir: str,
            repositories: Dict[str, Dict[str, Any]],
            virtualenvs: Dict[str, str],
            constants: Dict[str, Union[str, int, float, bool]],
    ):
        self.project_dir: str = project_dir
        self.repositories: Dict[str, Dict[str, Any]] = repositories
        self.virtualenvs: Dict[str, str] = virtualenvs
        self.constants: Dict[str, Union[str, int, float, bool]] = constants

        self.env_vars: Dict[str, str] = deepcopy(ENV_VARS)

    def apply(
            self,
            commands: List[str],
            repos: List[str] = (),
            **kwargs: Dict[str, Any]
    ) -> Generator[Tuple[str, str], None, None]:
        """
        Yields a list of commands to all repositories or a selected set of them, substitutes relevant parameters stored
        in .gameta file

        Args:
            commands (List[str]): Commands to be applied
            repos (List[str]): Selected set of repositories

        Returns:
            None
        """
        try:
            # Retrieve repositories for execution
            repositories: List[Tuple[str, Dict[str, str]]] = [
                (repo, repo_details) for repo, repo_details in self.repositories.items() if repo in repos
            ]

            # Prepare config by overriding existing configuration with necessary execution values
            config: CommandConfig = CommandConfig(
                **{
                    **kwargs,
                    **{
                        # Python subprocess does not handle multiple commands
                        # hence we need to execute these in a separate shell
                        'shell': True if len(commands) > 1 else kwargs.get('shell', False),
                        'venv': self.virtualenvs[kwargs['venv']] if kwargs.get('venv') else None
                    }
                }
            )

            for repo, repo_details in repositories:
                # Generate complete set of parameters for substitution
                with self.cd(repo_details['path']):
                    with GametaCommand(
                            commands,
                            self.generate_parameters(repo_details),
                            config
                    ) as c:
                        yield repo, c
        except CommandError:
            raise
        except Exception as e:
            raise CommandError(
                f"Error {e.__class__.__name__}.{str(e)} occurred when running commands {commands} in {repos} with "
                f"parameters {kwargs}")

    def generate_parameters(self, repo_details: Dict) -> Dict:
        """
        Generates the set of parameters for each repository to be substituted into command strings.

        Args:
            repo_details (Dict): Repository details from .gameta file

        Returns:
            Dict: Generated set of parameters
        """
        # Substitute into parameters first and combine all into constants
        combined_details: Dict = {
            k: Parameter(v).substitute({**self.constants, **self.env_vars}) if isinstance(v, str) else v
            for k, v in deepcopy(repo_details).items()
        }
        combined_details.update({**self.constants, **self.env_vars})
        return combined_details

    @contextmanager
    def cd(self, sub_directory: str) -> Generator[str, None, None]:
        """
        Changes directory to a subdirectory within the project

        Args:
            sub_directory (str): Relative subdirectory within the project

        Returns:
            Generator[str, None, None]: Path to current directory
        """
        cwd = getcwd()
        path = normpath(join(self.project_dir, sub_directory.lstrip('/')))
        chdir(path)
        yield path
        chdir(cwd)

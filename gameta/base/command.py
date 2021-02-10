import shlex
from copy import deepcopy
from dataclasses import dataclass
from os import getenv
from os.path import join
from types import TracebackType
from typing import List, Dict, Optional, Type


__all__ = ['Command']


SHELL = getenv('SHELL', '/bin/sh')


@dataclass
class Config:
    """
    Holds the configuration parameters for each set of commands

    Attributes:
        python (bool): Use Python generator
        shell (bool): Flag to indicate that shell generator should be used
        venv (Optional[str]): Indicates that virtualenv generator should be used
    """
    python: bool
    shell: bool
    venv: Optional[str] = None

    def __getitem__(self, item):
        return self.__dict__[item]


class Command(object):
    """
    A generic base class for handling a set of commands, providing functionality to generate the commands according to
    the given configuration.

    Attributes:
        commands (List[str]): List of pre-rendered commands
        params (Dict): Parameters to substitute into commands
        config (Config): Configuration class that holds all the relevant rendering configurations
    """
    def __init__(self, commands: List[str], params: Dict, shell: bool, python: bool, venv: Optional[str] = None):
        self.commands: List[str] = commands
        self.params: Dict = params
        self.config: Config = Config(
            **{
                # Python subprocess does not handle multiple commands
                # hence we need to execute these in a separate shell
                'shell': True if len(self.commands) > 1 else shell,
                'python': python,
                'venv': venv
            }
        )

    def __enter__(self) -> List[str]:
        """
        Context manager method for processing commands

        Returns:
            List[str]: Processed commands
        """
        return self.generate()

    def __exit__(
            self,
            exc_type: Optional[Type[BaseException]],
            exc_val: Optional[BaseException],
            exc_tb: Optional[TracebackType]
    ) -> bool:
        """
        Handle exceptions raised by the context manager

        Args:
            exc_type (Optional[Type[BaseException]]): Type of exception raised
            exc_val (Optional[BaseException]): Value of the exception
            exc_tb (Optional[TracebackType]): Traceback of the exception

        Returns:
            bool: If exception was handled
        """
        pass

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
            if self.config.python:
                prepared_command: str = self.shell(self.virtualenv(self.python(substituted_commands)))
            else:
                prepared_command: str = self.shell(self.virtualenv(substituted_commands))
        elif self.config.python:
            prepared_command: str = self.shell(self.python(substituted_commands))
        elif self.config.shell:
            prepared_command: str = self.shell(substituted_commands)
        else:
            prepared_command: str = ' && '.join(substituted_commands)

        # Tokenise results for subprocess execution
        return self.tokenise(prepared_command)

    def substitute(self) -> List[str]:
        """
        Substitutes the commands with the parameter set provided

        Returns:
            List[str]: Set of commands post-substitution
        """
        return [c.format(**self.params) for c in deepcopy(self.commands)]

    def virtualenv(self, commands: List[str]) -> List[str]:
        """
        Prepares commands to be executed by a virtualenv by sourcing it prior to execution

        Args:
            commands (List[str]): List of commands to be prepared

        Returns:
            List[str]: Prepared commands to be executed by subprocess
        """
        return [f". {join(self.config.venv, 'bin', 'activate')}"] + commands

    @staticmethod
    def python(commands: List[str]) -> List[str]:
        """
        Prepares commands to be executed by the system Python interpreter via shell

        Args:
            commands List[str]: Python scripts

        Returns:
            List[str]: Python prepared commands to be executed by subprocess
        """
        return ["python3 -c \'{}\'".format(command.replace('"', '\\\"')) for command in commands]

    @staticmethod
    def shell(commands: List[str]) -> str:
        """
        Prepares commands to be executed in a separate shell as subprocess does not natively handle piping or multiple
        commands

        Args:
            commands (List[str]): List of commands to be prepared

        Returns:
            str: Prepared command string
        """
        return f'{SHELL} -c "' + ' && '.join(commands) + '"'

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

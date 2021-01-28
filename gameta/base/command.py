import shlex
from copy import deepcopy
from os import getenv
from os.path import join
from types import TracebackType
from typing import List, Dict, Optional, Type


__all__ = ['Command']


SHELL = getenv('SHELL', '/bin/sh')


class Command(object):
    """
    A generic base class for handling a set of commands, providing functionality to render the commands according to the
    given configuration.

    Attributes:
        __commands (List[str]): List of pre-rendered commands
        __parameters (Dict): Parameters to substitute into commands
        use_shell (bool): Configuration flag to indicate if command should be executed in a separate shell
        use_python (bool): Configuration flag to indicate if commands are to be executed as Python commands
        venv (Optional[str]): Virtual environment path to render command with, if provided
    """
    def __init__(self, commands: List[str], parameters: Dict, shell: bool, python: bool, venv: Optional[str] = None):
        self.__commands: List[str] = commands
        self.__parameters: Dict = parameters

        # Python subprocess does not handle multiple commands hence we need to execute them in a separate shell
        self.use_shell: bool = True if len(self.__commands) > 1 else shell
        self.use_python: bool = python
        self.venv: Optional[str] = venv

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
        substituted_commands: List[str] = self.substitute()

        if self.venv:
            if self.use_python:
                prepared_command: str = self.shell(self.virtualenv(self.python(substituted_commands)))
            else:
                prepared_command: str = self.shell(self.virtualenv(substituted_commands))
        elif self.use_python:
            prepared_command: str = self.shell(self.python(substituted_commands))
        elif self.use_shell:
            prepared_command: str = self.shell(substituted_commands)
        else:
            prepared_command: str = ' && '.join(substituted_commands)

        return self.tokenise(prepared_command)

    def substitute(self) -> List[str]:
        """
        Substitutes the commands with the parameter set provided

        Returns:
            List[str]: Set of commands post-substitution
        """
        return [c.format(**self.__parameters) for c in deepcopy(self.__commands)]

    def virtualenv(self, commands: List[str]) -> List[str]:
        """
        Prepares commands to be executed by a virtualenv by sourcing it prior to execution

        Args:
            commands (List[str]): List of commands to be prepared

        Returns:
            List[str]: Prepared commands to be executed by subprocess
        """
        return [f". {join(self.venv, 'bin', 'activate')}"] + commands

    def python(self, commands: List[str]) -> List[str]:
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
        Prepares commands to be executed in a separate shell as subprocess does not natively handle piping or mutiple
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

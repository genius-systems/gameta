import json
import shlex
from contextlib import contextmanager
from copy import deepcopy
from os import getenv, getcwd, chdir, environ
from os.path import join, basename, normpath, abspath
from typing import Optional, List, Generator, Dict, Tuple, Union, Any

import click

from gameta import __version__

from .files import File
from .schemas import supported_versions, Schema, to_schema_tuple


__all__ = [
    # Contexts
    'GametaContext', 'gameta_context',
]


SHELL = getenv('SHELL', '/bin/sh')


class Gameta(File):
    """
    Interface for the .gameta file

    Attributes:
        path (str): Absolute path to the .gameta file
        file_name (str): Reference to the .gameta file
    """

    def __init__(self, path: str, file_name: str = '.gameta'):
        super(Gameta, self).__init__(path, file_name)

    def load(self) -> Optional[Any]:
        """
        Loads data from the .gameta file

        Returns:
            Optional[Any]
        """
        # Attempt to load .gameta file
        try:
            with open(self.file, 'r') as f:
                return json.load(f)

        # .gameta file does not exist
        except FileNotFoundError:
            return

        except Exception as e:
            click.echo(f"Could not load {self.file_name} file due to: {e.__class__.__name__}.{str(e)}")

    def export(self, data: Any) -> None:
        """
        Exports data to the .gameta file

        Returns:
            None
        """
        try:
            with open(self.file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            click.echo(f"Could not export data to {self.file_name} file: {e.__class__.__name__}.{str(e)}")


class GametaContext(object):
    """
    GametaContext for the current Gameta session

    Attributes:
        schema (Schema): Schema class for Gameta .gameta file
        project_dir (Optional[str]): Project directory
        is_metarepo (bool): Project is a metarepo
        gameta_data (Dict): Gameta data cache to store extracted data and updated data for export
        repositories (Dict[str, Dict]): Data of all the repositories contained in the metarepo
        tags (Dict[str, List[str]]): Repository data organised according to tags
        constants (Dict[str, Union[str, int, bool, float]]): Gameta constants data extracted
        commands (Dict): Gameta commands data extracted
        env_vars (Dict): Extracted environment variables with keys prefixed with $
        files (Dict[str, File]): File formats supported
    """

    def __init__(self):
        self.project_dir: Optional[str] = None
        self.is_metarepo: bool = False
        self.gameta_data: Dict = {}
        self.virtualenvs: Dict = {}
        self.constants: Dict[str, Union[str, int, bool, float]] = {}
        self.commands: Dict = {}
        self.repositories: Dict[str, Dict] = {}
        self.tags: Dict[str, List[str]] = {}

        self.env_vars: Dict = {
            '$' + k.upper(): v
            for k, v in environ.items()
        }

        self.files: Dict[str, File] = {}

        self.version: str = __version__
        self.schema: Optional[Schema] = None

    def init(self, project_dir: str) -> None:
        """
        Initialises a GametaContext with the project directory. The __init__ process is split into 2 parts (object
        creation and parameter initialisation) such that it can be used with click's context decorator, hence this
        function has to be run to complete the initialisation process.

        Args:
            project_dir (str): Absolute path to the project directory

        Returns:
            None
        """
        self.project_dir = project_dir
        self.files.update({'gameta': Gameta(self.gameta_folder)})

    @property
    def project_name(self) -> str:
        """
        Returns the name of the project

        Returns:
            str: Name of the project
        """
        return basename(self.project_dir)

    @property
    def gameta_folder(self) -> str:
        """
        Returns the path to the .gameta folder of the project

        Returns:
            str: Absolute path to the .gameta folder
        """
        return join(self.project_dir, '.gameta')

    @property
    def gameta(self) -> str:
        """
        Returns the path to the .gameta file of the project, i.e. where it should be if the Project has not been
        initialised

        Returns:
            str: Path to the project's .gameta file
        """
        return self.files['gameta'].file

    @property
    def gitignore(self) -> str:
        """
        Returns the path to the .gitignore file of the project, i.e. where it should be if the Project has not been
        initialised

        Returns:
            str: Path to the project's .gitignore file
        """
        return self.files['gitignore'].file

    @property
    def metarepo(self) -> str:
        """
        Returns the primary metarepo's name

        Returns:
            str: Name of the primary metarepo
        """
        for repo in self.repositories:
            if self.is_primary_metarepo(repo):
                return repo

    @property
    def schema_version(self) -> Tuple[int, int, int]:
        """
        Returns the .gameta schema version

        Returns:
            Tuple[int]
        """
        return self.get_schema_version(self.version)

    @staticmethod
    def get_schema_version(version: str) -> Tuple[int, int, int]:
        """
        A convenience method for parsing and retrieving the schema version

        Args:
            version (str): Version string

        Returns:
            Tuple[int, int, int]: Tuple of schema parameters
        """
        return to_schema_tuple(version)

    def add_gitignore(self, path: str) -> None:
        """
        Adds the path to the gitignore_data

        Args:
            path (str): Path to be added

        Returns:
            None
        """
        self.gitignore_data.append(path + '/\n')

    def remove_gitignore(self, path: str) -> None:
        """
        Removes the path from the gitignore_data

        Args:
            path (str): Path to be removed

        Returns:
            None
        """
        try:
            self.gitignore_data.remove(path + '/\n')
        except ValueError:
            return

    def is_primary_metarepo(self, repo: str) -> bool:
        """
        Returns a boolean if the repository is a primary meta-repository

        Args:
            repo (str): Repository to check

        Returns:
            bool: Flag to indicate if repository is a primary meta-repository
        """
        return abspath(self.repositories[repo]["path"]) == self.project_dir

    def load(self) -> None:
        """
        Loads data from all supported file formats

        Returns:
            None
        """
        for file, interface in self.files.items():
            interface.load()

        # Retrieve validation schemas
        try:
            self.version = self.gameta_data['version']
            self.schema = supported_versions[self.schema_version]
        except Exception as e:
            self.version = __version__
            self.schema = supported_versions[self.schema_version]
            click.echo(
                f"Could not retrieve schema version, defaulting to latest Gameta schema version, "
                f"error: {e.__class__.__name__}.{str(e)}"
            )
            click.echo("To debug this issue, run `gameta schema validate`")

        # Validate repositories
        try:
            for repo in self.gameta_data['repositories'].values():
                self.schema.validators['repositories'].validate(repo)
            self.repositories = self.gameta_data['repositories']
            self.is_metarepo = True
            self.generate_tags()
        except Exception as e:
            self.repositories = {}
            self.tags = {}
            click.echo(f"Malformed repository element, error: {e.__class__.__name__}.{str(e)}")

        # Validate commands
        try:
            for command in self.gameta_data.get('commands', {}).values():
                self.schema.validators['commands'].validate(command)
            self.commands = self.gameta_data.get('commands', {})
        except Exception as e:
            self.commands = {}
            click.echo(f"Malformed commands element, error: {e.__class__.__name__}.{str(e)}")

        # Validate constants
        try:
            self.schema.validators['constants'].validate(self.gameta_data.get('constants', {}))
            self.constants = self.gameta_data.get('constants', {})
        except Exception as e:
            self.constants = {}
            click.echo(f"Malformed constants element, error: {e.__class__.__name__}.{str(e)}")

        # Validate virtualenvs
        try:
            self.schema.validators['virtualenvs'].validate(self.gameta_data.get('virtualenvs', {}))
            self.virtualenvs = self.gameta_data.get('virtualenvs', {})
        except Exception as e:
            self.virtualenvs = {}
            click.echo(f"Malformed virtualenvs element, error: {e.__class__.__name__}.{str(e)}")

    def export(self) -> None:
        """
        Exports data to all supported file formats

        Returns:
            None
        """

        # Moving this here in the event we wish to validate the outgoing data and for consistency's sake
        self.gameta_data['version'] = self.version
        self.gameta_data['repositories'] = self.repositories
        if self.commands:
            self.gameta_data['commands'] = self.commands
        if self.constants:
            self.gameta_data['constants'] = self.constants
        if self.virtualenvs:
            self.gameta_data['virtualenvs'] = self.virtualenvs

        for file, interface in self.files.items():
            interface.export()

    def generate_tags(self) -> None:
        """
        Updates the tag indexes of the repositories

        Returns:
            None
        """
        for repo, details in self.repositories.items():
            for tag in details.get('tags', []):
                if tag in self.tags:
                    self.tags[tag].append(repo)
                else:
                    self.tags[tag] = [repo]

    def apply(
            self,
            commands: List[str],
            repos: List[str] = (),
            shell: bool = False,
            python: bool = False,
            venv: Optional[str] = None,
    ) -> Generator[Tuple[str, str], None, None]:
        """
        Yields a list of commands to all repositories or a selected set of them, substitutes relevant parameters stored
        in .gameta file

        Args:
            commands (List[str]): Commands to be applied
            repos (List[str]): Selected set of repositories
            shell (bool): Flag to indicate if a separate shell should be used
            python (bool): Flag to indicate if commands are to be tokenised as Python commands
            venv (Optional[str]): Virtualenv parameter for executing commands

        Returns:
            None
        """
        repositories: List[Tuple[str, Dict[str, str]]] = [
            (repo, details) for repo, details in self.repositories.items() if repo in repos
        ]

        for repo, details in repositories:
            # Generate complete set of parameters for substitution

            with self.cd(details['path']):
                repo_commands: List[str] = [
                    c.format(**self.generate_parameters(repo, details, python)) for c in deepcopy(commands)
                ]
                if venv is not None:
                    command: List[str] = self.virtualenv(
                        venv, self.python(repo_commands, shell=False) if python else repo_commands
                    )
                elif python:
                    command: List[str] = self.python(repo_commands)
                elif shell:
                    command: List[str] = self.shell(repo_commands)
                else:
                    command: List[str] = self.tokenise(' && '.join(repo_commands))
                yield repo, command

    def generate_parameters(self, repo: str, repo_details: Dict, python: bool = False) -> Dict:
        """
        Generates the set of parameters for each repository to be substituted into command strings. 
        
        Args:
            repo (str): Repository name of parameters to be generated
            repo_details (Dict): Repository details from .gameta file
            python (bool): Flag to indicate if Python variables should be generated, defaults to False

        Returns:
            Dict: Generated set of parameters
        """

        combined_details: Dict = {
            k: v.format(**self.env_vars) if isinstance(v, str) else v
            for k, v in deepcopy(repo_details).items()
        }
        if python:
            repositories: Dict = deepcopy(self.repositories)
            repositories[repo] = deepcopy(combined_details)
            combined_details.update(
                {
                    '__repos__':
                        json.dumps(repositories)
                            .replace("true", "True")
                            .replace("false", "False")
                            .replace("null", "None")
                }
            )
        combined_details.update(self.constants)
        combined_details.update(self.env_vars)
        return combined_details

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

    def shell(self, commands: List[str]) -> List[str]:
        """
        Prepares commands to be executed in a separate shell as subprocess does not natively handle piping

        Args:
            commands (List[str]): User-defined commands

        Returns:
            List[str]: Shell command string to be executed by subprocess
        """
        return self.tokenise(
            f'{SHELL} -c "' +
            ' && '.join(commands) +
            '"'
        )

    def virtualenv(self, venv: str, commands: List[str]) -> List[str]:
        """
        Prepares commands to be executed by a virtualenv by sourcing it prior to execution

        Args:
            venv (str): Name of virtualenv to be activated
            commands (List[str]): Python scripts or shell commands

        Returns:
            List[str]: Prepared commands to be executed by subprocess
        """
        return self.shell([f". {join(self.virtualenvs[venv], 'bin', 'activate')}"] + commands)

    def python(self, commands: List[str], shell: bool = True) -> List[str]:
        """
        Prepares commands to be executed by the system Python interpreter via shell

        Args:
            commands List[str]: Python scripts
            shell: Flag to indicate if shell should be used to generate the command

        Returns:
            List[str]: Python prepared commands to be executed by subprocess
        """
        commands: List[str] = ["python3 -c \'{}\'".format(command.replace('"', '\\\"')) for command in commands]
        return self.shell(commands) if shell else commands


gameta_context = click.make_pass_decorator(GametaContext, ensure=True)

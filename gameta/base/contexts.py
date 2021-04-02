import json
from contextlib import contextmanager
from os.path import join, basename, abspath
from typing import Optional, List, Dict, Tuple, Union, Any

import click

from gameta import __version__
from .errors import ContextError

from .files import File
from .schemas import supported_versions, Schema, to_schema_tuple
from .vcs import vcs_interfaces, GametaRepo
from .commands import Runner


__all__ = [
    # Contexts
    'GametaContext', 'gameta_context',
]


class Gameta(File):
    """
    Interface for the .gameta file

    Attributes:
        path (str): Absolute path to the .gameta file
        file_name (str): Reference to the .gameta file
    """

    def __init__(self, path: str, file_name: str = '.gameta'):
        super(Gameta, self).__init__(path, file_name)

    def load(self) -> Any:
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
            return {}

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
        version (str): Gameta version
        schema (Schema): Schema class for Gameta .gameta file
        project_dir (Optional[str]): Project directory
        is_metarepo (bool): Project is a metarepo
        files (Dict[str, File]): File formats supported
        gameta_data (Dict): Gameta data cache to store extracted data and updated data for export
        repositories (Dict[str, Dict]): Data of all the repositories contained in the metarepo
        tags (Dict[str, List[str]]): Repository data organised according to tags
        constants (Dict[str, Union[str, int, bool, float]]): Gameta constants data extracted
        commands (Dict): Gameta commands data extracted
    """

    def __init__(self):
        self.version: str = __version__

        # Project dependent variables
        self.schema: Optional[Schema] = None
        self.project_dir: Optional[str] = None
        self.is_metarepo: bool = False
        self.files: Dict[str, File] = {}

        self.gameta_data: Dict[str, Any] = {}
        self.repositories: Dict[str, Dict[str, Any]] = {}
        self.tags: Dict[str, List[str]] = {}
        self.commands: Dict = {}
        self.virtualenvs: Dict[str, str] = {}
        self.constants: Dict[str, Union[str, int, bool, float]] = {}

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

        Raises:
            ContextError: If Gameta Context has not been initialised
        """
        if self.project_dir is None:
            raise ContextError("Gameta Context has not been initialised, run the init function first")

        return basename(self.project_dir)

    @property
    def gameta_folder(self) -> str:
        """
        Returns the path to the .gameta folder of the project

        Returns:
            str: Absolute path to the .gameta folder

        Raises:
            ContextError: If Gameta Context has not been initialised
        """
        if self.project_dir is None:
            raise ContextError("Gameta Context has not been initialised, run the init function first")

        return join(self.project_dir, '.gameta')

    @property
    def gameta(self) -> str:
        """
        Returns the path to the .gameta file of the project, i.e. where it should be if the Project has not been
        initialised

        Returns:
            str: Path to the project's .gameta file

        Raises:
            ContextError: If Gameta Context has not been initialised
        """
        if 'gameta' not in self.files:
            raise ContextError("Gameta Context has not been initialised, run the init function first")

        return self.files['gameta'].file

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

    @property
    def runner(self) -> Runner:
        """
        Returns a runner populated with existing context values for executing commands

        Returns:
            Runner: Instantiated runner
        """
        return Runner(self.project_dir, self.repositories, self.virtualenvs, self.constants)

    @contextmanager
    def repo(self, repo: str) -> GametaRepo:
        """
        Convenience method to retrieve a GametaRepo for managing a particular repository

        Args:
            repo (str): Name of the repository

        Returns:
            GametaRepo: Instantiated GametaRepo
        """
        yield vcs_interfaces[self.repositories[repo]['vcs']].generate_repo(self.repositories[repo]['path'])

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

    def is_primary_metarepo(self, repo: str) -> bool:
        """
        Returns a boolean if the repository is a primary meta-repository

        Args:
            repo (str): Repository to check

        Returns:
            bool: Flag to indicate if repository is a primary meta-repository

        Raises:
            ContextError: If repository does not exist
        """
        if repo not in self.repositories:
            raise ContextError(f"Repository {repo} does not exist")

        return abspath(self.repositories[repo]["path"]) == self.project_dir

    def load(self) -> None:
        """
        Loads data from all supported file formats

        Returns:
            None
        """
        for file, interface in self.files.items():
            self.gameta_data = interface.load()

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
        if self.repositories:
            self.gameta_data['repositories'] = self.repositories
        if self.commands:
            self.gameta_data['commands'] = self.commands
        if self.constants:
            self.gameta_data['constants'] = self.constants
        if self.virtualenvs:
            self.gameta_data['virtualenvs'] = self.virtualenvs

        self.files['gameta'].export(self.gameta_data)

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


gameta_context = click.make_pass_decorator(GametaContext, ensure=True)

import json
import shlex
from abc import abstractmethod
from contextlib import contextmanager
from copy import deepcopy
from os import getenv, getcwd, chdir, environ
from os.path import join, basename, normpath, abspath
from typing import Optional, List, Generator, Dict, Tuple, Union

import click


from jsonschema.validators import Draft7Validator


__all__ = [
    # Contexts
    'GametaContext', 'gameta_context',
]


SHELL = getenv('SHELL', '/bin/sh')


class File(object):
    """
    Generic file interface for Gameta file formats

    Attributes:
        context (GametaContext): Reference to Gameta Context
        file_name (str): Name of the reference file
    """

    def __init__(self, context: 'GametaContext', file_name: str):
        self.context = context
        self.file_name = file_name

    @property
    def file(self) -> str:
        """
        Returns the absolute path to the reference file

        Returns:
            str: Absolute path to the file
        """
        return join(self.context.project_dir, self.file_name)

    @abstractmethod
    def load(self) -> None:
        """
        Abstractmethod to load data and validate data from the file and populate the GametaContext

        Returns:
            None
        """

    @abstractmethod
    def export(self) -> None:
        """
        Abstractmethod to export data from the GametaContext to the file

        Returns:
            None
        """


class GitIgnore(File):
    """
    Interface for the .gitignore file

    Attributes:
        context (GametaContext): Reference to Gameta Context
        file_name (str): Reference to the .gitignore file
    """
    def __init__(self, context: 'GametaContext', file_name: str = '.gitignore'):
        super(GitIgnore, self).__init__(context, file_name)

    def load(self) -> None:
        """
        Loads data from the .gitignore file and populates the GametaContext

        Returns:
            None
        """
        try:
            with open(self.file, 'r') as f:
                self.context.gitignore_data = f.readlines()
        except FileNotFoundError:
            return
        except Exception as e:
            self.context.gitignore_data = []
            click.echo(f"Could not load {self.file_name} file due to: {e.__class__.__name__}.{str(e)}")

    def export(self) -> None:
        """
        Exports data from the GametaContext to the .gitignore file

        Returns:
            None
        """
        try:
            with open(self.file, 'w') as f:
                f.writelines(self.context.gitignore_data)
        except Exception as e:
            click.echo(f"Could not export data to {self.file_name} file: {e.__class__.__name__}.{str(e)}")


class Meta(File):
    """
    Interface for the .meta file

    Attributes:
        context (GametaContext): Reference to Gameta Context
        file_name (str): Reference to the .meta file
    """

    def __init__(self, context: 'GametaContext', file_name: str = '.meta'):
        super(Meta, self).__init__(context, file_name)

    def load(self) -> None:
        """
        Loads data from the .meta file, validates it and populates the GametaContext

        Returns:
            None
        """
        # Attempt to load .meta file
        try:
            with open(self.file_name, 'r') as f:
                self.context.gameta_data = json.load(f)
        except FileNotFoundError:
            return
        except Exception as e:
            click.echo(f"Could not load {self.file_name} file due to: {e.__class__.__name__}.{str(e)}")

        # Validate repositories
        try:
            for repo in self.context.gameta_data['projects'].values():
                self.context.validators['repositories'].validate(repo)
            self.context.repositories = self.context.gameta_data['projects']
            self.context.is_metarepo = True
            self.context.generate_tags()
        except Exception as e:
            self.context.repositories = {}
            self.context.tags = {}
            click.echo(f"Malformed repository element, error: {e.__class__.__name__}.{str(e)}")

        # Validate commands
        try:
            for command in self.context.gameta_data.get('commands', {}).values():
                self.context.validators['commands'].validate(command)
            self.context.commands = self.context.gameta_data.get('commands', {})
        except Exception as e:
            self.context.commands = {}
            click.echo(f"Malformed commands element, error: {e.__class__.__name__}.{str(e)}")

        # Validate constants
        try:
            self.context.validators['constants'].validate(self.context.gameta_data.get('constants', {}))
            self.context.constants = self.context.gameta_data.get('constants', {})
        except Exception as e:
            self.context.constants = {}
            click.echo(f"Malformed constants element, error: {e.__class__.__name__}.{str(e)}")

    def export(self) -> None:
        """
        Exports data from the GametaContext to the .meta file

        Returns:
            None
        """
        try:
            self.context.gameta_data['projects'] = self.context.repositories
            if self.context.commands:
                self.context.gameta_data['commands'] = self.context.commands
            if self.context.constants:
                self.context.gameta_data['constants'] = self.context.constants
            with open(self.file, 'w') as f:
                json.dump(self.context.gameta_data, f, indent=2)
        except Exception as e:
            click.echo(f"Could not export data to {self.file_name} file: {e.__class__.__name__}.{str(e)}")


class GametaContext(object):
    """
    GametaContext for the current Gameta session

    Attributes:
        __schema__ (Dict): JSON Schema for Gameta .meta file
        validators (Dict[str, jsonschema.Draft7Validator]): JSON Schema validators for each object component
        reserved_params (Dict[str, List[str]): Reserved parameters for each object group

        project_dir (Optional[str]): Project directory
        is_metarepo (bool): Project is a metarepo
        gameta_data (Dict): Gameta data extracted and exported
        repositories (Dict[str, Dict]): Data of all the repositories contained in the metarepo
        tags (Dict[str, List[str]]): Repository data organised according to tags
        constants (Dict[str, Union[str, int, bool, float]]): Gameta constants data extracted
        commands (Dict): Gameta commands data extracted
        gitignore_data (List[str]): Gitignore data extracted from the .gitignore file
        env_vars (Dict): Extracted environment variables with keys prefixed with $
        files (Dict[str, File]): File formats supported
    """
    __schema__: Dict = {
        '$schema': "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "repositories": {
                "$ref": "#/definitions/repositories"
            },
            "commands": {
                "$ref": "#/definitions/commands"
            },
            "constants": {
                "$ref": "#/definitions/constants"
            },
            "required": [
                "repositories"
            ]
        },
        'definitions': {
            "repositories": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": ["string", "null"],
                        "format": "uri"
                    },
                    "path": {
                        "type": "string"
                    },
                    "tags": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        }
                    },
                    "__metarepo__": {
                        "type": "boolean"
                    }
                },
                "required": [
                    "url", "path", "__metarepo__"
                ]
            },
            "commands": {
                "type": "object",
                "properties": {
                    "commands": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        },
                    },
                    "raise_errors": {
                        "type": "boolean"
                    },
                    "shell": {
                        "type": "boolean"
                    },
                    "python": {
                        "type": "boolean"
                    },
                    "verbose": {
                        "type": "boolean"
                    },
                    "repositories": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        },
                    },
                    "tags": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        },
                    }
                },
                "minProperties": 6,
                "maxProperties": 7,
                "additionalProperties": False,
            },
            "constants": {
                "type": "object",
                "propertyNames": {
                    "pattern": "^[A-Z0-9_-]"
                }
            }
        }
    }

    validators = {
        'meta': Draft7Validator(__schema__),
        'repositories': Draft7Validator(__schema__['definitions']['repositories']),
        'commands': Draft7Validator(__schema__['definitions']['commands']),
        'constants': Draft7Validator(__schema__['definitions']['constants'])
    }

    reserved_params: Dict[str, List[str]] = {
        'repositories': list(__schema__['definitions']['repositories']['properties'].keys()),
        'commands': list(__schema__['definitions']['commands']['properties'].keys())
    }

    def __init__(self):
        self.project_dir: Optional[str] = None
        self.gitignore_data: List[str] = []
        self.is_metarepo: bool = False
        self.gameta_data: Dict = {}
        self.constants: Dict[str, Union[str, int, bool, float]] = {}
        self.commands: Dict = {}
        self.repositories: Dict[str, Dict] = {}
        self.tags: Dict[str, List[str]] = {}

        self.env_vars: Dict = {
            '$' + k.upper(): v
            for k, v in environ.items()
        }

        self.files: Dict[str, File] = {
            'meta': Meta(self),
            'gitignore': GitIgnore(self)
        }

    @property
    def project_name(self) -> str:
        """
        Returns the name of the project

        Returns:
            str: Name of the project
        """
        return basename(self.project_dir)

    @property
    def meta(self) -> str:
        """
        Returns the path to the .meta file of the project, i.e. where it should be if the Project has not been
        initialised

        Returns:
            str: Path to the project's .meta file
        """
        return self.files['meta'].file

    @property
    def gitignore(self) -> str:
        """
        Returns the path to the .gitignore file of the project, i.e. where it should be if the Project has not been
        initialised

        Returns:
            str: Path to the project's .gitignore file
        """
        return self.files['gitignore'].file

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

    def export(self) -> None:
        """
        Exports data to all supported file formats

        Returns:
            None
        """
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
    ) -> Generator[Tuple[str, str], None, None]:
        """
        Yields a list of commands to all repositories or a selected set of them, substitutes relevant parameters stored
        in .meta file

        Args:
            commands (List[str]): Commands to be applied
            repos (List[str]): Selected set of repositories
            shell (bool): Flag to indicate if a separate shell should be used
            python (bool): Flag to indicate if commands are to be tokenised as Python commands

        Returns:
            None
        """
        repositories: List[Tuple[str, Dict[str, str]]] = \
            [(repo, details) for repo, details in self.repositories.items() if repo in repos] or \
            list(self.repositories.items())

        for repo, details in repositories:
            # Generate complete set of parameters for substitution
            combined_details: Dict = deepcopy(details)
            combined_details.update(self.constants)
            combined_details.update(self.env_vars)
            combined_details.update(
                {
                    '__repos__':
                        json.dumps(self.repositories)
                        .replace("true", "True")
                        .replace("false", "False")
                        .replace("null", "None")
                }
            )

            with self.cd(combined_details['path']):
                repo_commands: List[str] = [c.format(**combined_details) for c in deepcopy(commands)]
                if python:
                    command: List[str] = self.python(repo_commands)
                elif shell:
                    command: List[str] = self.shell(repo_commands)
                else:
                    command: List[str] = self.tokenise(' && '.join(repo_commands))
                yield repo, command

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

    def python(self, commands: List[str]) -> List[str]:
        """
        Prepares commands to be executed by Python interpreter via shell

        Args:
            commands List[str]: Python scripts

        Returns:
            List[str]: Python prepared commands to be executed by subprocess
        """
        return self.shell(
            ["python3 -c \'{}\'".format(command.replace('"', '\\\"')) for command in commands]
        )


gameta_context = click.make_pass_decorator(GametaContext, ensure=True)

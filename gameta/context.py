import json
import shlex
from contextlib import contextmanager
from copy import deepcopy
from os import getenv, getcwd, chdir
from os.path import join, basename, normpath, abspath
from typing import Optional, List, Generator, Dict, Tuple

import click


__all__ = [
    # Contexts
    'GametaContext', 'gameta_context',
]


SHELL = getenv('SHELL', '/bin/sh')


class GametaContext(object):
    """
    GametaContext for the current Gameta session

    Attributes:
        project_dir (Optional[str]): Project directory
        is_metarepo (bool): Project is a metarepo
        gameta_data (Dict): Gameta data extracted and exported
        repositories (Dict[str, Dict]): Data of all the repositories contained in the metarepo
        tags (Dict[str, List[str]]): Repository data organised according to tags
    """
    reserved_params = ['url', 'path', 'tags', '__metarepo__']

    def __init__(self):
        self.is_metarepo: bool = False
        self.gitignore_data: List[str] = []
        self.project_dir: Optional[str] = None
        self.gameta_data: Dict = {}
        self.commands: Dict = {}
        self.repositories: Dict[str, Dict] = {}
        self.tags: Dict[str, List[str]] = {}

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
        return join(self.project_dir, '.meta')

    @property
    def gitignore(self) -> str:
        """
        Returns the path to the .gitignore file of the project, i.e. where it should be if the Project has not been
        initialised

        Returns:
            str: Path to the project's .gitignore file
        """
        return join(self.project_dir, '.gitignore')

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
        Finds all repositories to manage and groups them into relative groups

        Returns:
            None
        """
        try:
            with open(self.meta, 'r') as f:
                self.gameta_data = json.load(f)
                self.repositories = self.gameta_data['projects']
                self.commands = self.gameta_data.get('commands', {})
            self.is_metarepo = True
        except FileNotFoundError:
            return
        except Exception as e:
            self.repositories = {}
            self.commands = {}
            click.echo(f"Could not load .meta file due to: {e.__class__.__name__}.{str(e)}")
            return

        try:
            self.generate_tags()
        except Exception as e:
            self.repositories = {}
            self.commands = {}
            click.echo(f"Malformed .meta file, error: {e.__class__.__name__}.{str(e)}")
            return

        try:
            with open(self.gitignore, 'r') as f:
                self.gitignore_data = f.readlines()
        except FileNotFoundError:
            return
        except Exception as e:
            self.gitignore_data = []
            click.ClickException(f"Could not load .gitignore file due to: {e.__class__.__name__}.{str(e)}")
            return

    def export(self) -> None:
        """
        Exports updated Gameta data to .meta file and gitignore data to the .gitignore file

        Returns:
            None
        """
        try:
            self.gameta_data['projects'] = self.repositories
            self.gameta_data['commands'] = self.commands
            with open(self.meta, 'w+') as f:
                json.dump(self.gameta_data, f)
        except Exception as e:
            raise click.ClickException(
                f"Could not export gameta data to .meta file: {e.__class__.__name__}.{str(e)}"
            )

        try:
            with open(self.gitignore, 'w+') as f:
                f.writelines(self.gitignore_data)
        except Exception as e:
            raise click.ClickException(
                f"Could not export gitignore data to .gitignore file: {e.__class__.__name__}.{str(e)}"
            )

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
            shell: bool = False
    ) -> Generator[Tuple[str, str], None, None]:
        """
        Yields a list of commands to all repositories or a selected set of them, substitutes relevant parameters stored
        in .meta file

        Args:
            commands (List[str]): Commands to be applied
            repos (List[str]): Selected set of repositories
            shell (bool): Flag to indicate if a separate shell should be used

        Returns:
            None
        """
        repositories: List[Tuple[str, Dict[str, str]]] = \
            [(repo, details) for repo, details in self.repositories.items() if repo in repos] or \
            list(self.repositories.items())

        for repo, details in repositories:
            with self.cd(details['path']):
                repo_commands: List[str] = [c.format(**details) for c in deepcopy(commands)]
                command: List[str] = self.shell(repo_commands) if shell else self.tokenise(' && '.join(repo_commands))
                yield repo, command

    @staticmethod
    def tokenise(command: str) -> List[str]:
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
        Executes commands provided in a separate shell as subprocess does not natively handle piping

        Args:
            commands (List[str]): User-defined commands

        Returns:
            List[str]: Shell command string to be executed by subprocess
        """
        return self.tokenise(
            f'{SHELL} -c " ' +
            ' && '.join(commands) +
            '"'
        )


gameta_context = click.make_pass_decorator(GametaContext, ensure=True)

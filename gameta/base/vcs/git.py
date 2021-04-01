from os.path import basename, splitext, join
from typing import Optional, Any, Dict, Tuple, List

import git

from ..errors import VCSError
from ..files import File

from .vcs import VCS, GametaRepo


__all__ = ['Git', 'GitRepo']


class Git(VCS):
    """
    Wrapper around a git VCS interface

    Attributes:
        name (str): Name of the interface
        path (str): Absolute path to the folder
        __interface (Any): Git VCS interface
    """
    name: str = 'git'

    def __init__(self, path: str):
        super(Git, self).__init__(path)
        self.__interface: Any = git

    @classmethod
    def is_vcs_type(cls, path: str) -> bool:
        """
        Evaluates if folder is a valid git repository

        Args:
            path (str): Absolute path to the folder

        Returns:
            bool: If folder is a valid git repository
        """
        try:
            git.Repo(path)
            return True
        except git.InvalidGitRepositoryError:
            return False

    @classmethod
    def generate_repo(cls, path: str) -> 'GitRepo':
        """
        Generates a GitRepo instance from a git repository

        Args:
            path (str): Absolute path to the folder

        Returns:
            GitRepo: A GitRepo instance

        Raises:
            VCSError: If operation fails
        """
        try:
            repo: git.Repo = git.Repo(path)
            details: Dict = {
                'path': path,
                'name': splitext(basename(repo.remote().url))[0],
                'url': repo.remote().url,
                'branch': str(repo.active_branch),
                'hash': repo.commit().hexsha,
            }
            return GitRepo(cls(path), GitIgnore(path), details, repo)
        except Exception as e:
            raise VCSError(f"Could not create git repository due to {e.__class__.__name__}.{str(e)}")

    @classmethod
    def init(cls, path: str) -> 'GitRepo':
        """
        Initialises a folder as a git repository

        Args:
            path (str): Absolute path to the folder

        Returns:
            GitRepo: A GitRepo instance

        Raises:
            VCSError: If operation fails
        """
        try:
            repo: git.Repo = git.Repo.init(path)
            details: Dict = {
                'path': path,
                'name': basename(path),
                'url': None,
                'branch': str(repo.active_branch),
                'hash': None,
            }
            return GitRepo(cls(path), GitIgnore(path), details, repo)
        except Exception as e:
            raise VCSError(f"Could not initialise git repository due to {e.__class__.__name__}.{str(e)}")

    @classmethod
    def clone(cls, path: str, url: str) -> 'GitRepo':
        """
        Git clones a new URL to the path specified and generates a GitRepo instance

        Args:
            path (str): Absolute path to the folder
            url (str): URL to clone from

        Returns:
            GitRepo: A GitRepo instance

        Raises:
            VCSError: If operation fails
        """
        if not url:
            raise VCSError(f"URL {url} is invalid")
        try:
            repo: git.Repo = git.Repo.clone_from(url, path)
            details: Dict = {
                'path': path,
                'name': splitext(basename(url))[0],
                'url': url,
                'branch': str(repo.active_branch),
                'hash': repo.commit().hexsha
            }
            return GitRepo(cls(path), GitIgnore(path), details, repo)
        except Exception as e:
            raise VCSError(f"Could not initialise git repository due to {e.__class__.__name__}.{str(e)}")


class GitIgnore(File):
    """
    Interface for the .gitignore file

    Attributes:
        path (str): Absolute path to the folder
        file_name (str): Reference to the .gitignore file
    """
    def __init__(self, path: str, file_name: str = '.gitignore'):
        super(GitIgnore, self).__init__(path, file_name)

    def load(self) -> Any:
        """
        Loads and returns data from the .gitignore file

        Returns:
            Optional[Any]: Returns the data loaded from the file or none if the file does not exist
        """
        try:
            with open(self.file, 'r') as f:
                return f.readlines()

        # Handle case where file has not been created
        except FileNotFoundError:
            return []

        # General exception case
        except Exception as e:
            VCSError(f"Could not load {self.file_name} file due to: {e.__class__.__name__}.{str(e)}")

    def export(self, data: Any) -> None:
        """
        Exports data from the GametaContext to the .gitignore file

        Args:
            data (Any): Data to be exported to file

        Returns:
            None
        """
        try:
            with open(self.file, 'a+') as f:
                f.writelines(data)
        except Exception as e:
            raise VCSError(f"Could not export data to {self.file_name} file: {e.__class__.__name__}.{str(e)}")


class GitRepo(GametaRepo):
    """
    Git repository interface for managing the git repository

    Attributes:
        interface (Git): Git interface wrapper
        ignore_file (GitIgnore): File that holds all the data to be ignored
        details (Dict): Git repository details
        repo (git.Repo): Git Repo class for interacting with the repository
        *args (Tuple): Generic arguments
        **kwargs (Dict[str, Any]): Generic keyword arguments
    """

    def __init__(
            self,
            interface: Git,
            ignore_file: GitIgnore,
            details: Dict,
            repo: git.Repo,
            *args: Tuple[Any],
            **kwargs: Dict[str, Any]
    ):
        super(GitRepo, self).__init__(interface, ignore_file, details)

        # Repo class
        self.repo: git.Repo = repo

        # GitIgnore data
        self.ignore_data: List[str] = self.ignore_file.load()

    def fetch(self, *args: Tuple, **kwargs: Dict) -> None:
        """
        Fetches updates from all remotes

        Args:
            *args (Tuple): Generic args
            **kwargs (Dict): Generic kwargs

        Returns:
            None

        Raises:
            VCSError: If errors occur during execution
        """
        try:
            for remote in self.repo.remotes:
                remote.fetch(*args, **{**{'tags': True, 'prune': True}, **kwargs})
        except git.GitError as e:
            raise VCSError(f"{e.__class__.__name__}.{str(e)} fetching remote updates")

    def switch(self, branch: str, *args: Tuple, **kwargs: Dict) -> None:
        """
        Creates a branch locally if it does not exist and checks it out

        Args:
            branch (str): Branch name or commit or reference
            *args (Tuple): Generic args
            **kwargs (Dict): Generic kwargs acceptable values include the following in a key-default mapping
                            {'force': False, 'logmsg': None}

        Returns:
            None

        Raises:
            VCSError: If errors occur during execution
        """
        try:
            # Evaluate if the commit exists in the repository
            try:
                commit: str = self.repo.rev_parse(branch).hexsha

            # Defaults to the current head (this is a new branch
            except git.BadName:
                commit: str = 'HEAD'

            # Check out branch
            self.repo.head.set_reference(
                # Create branch
                self.repo.create_head(
                    branch,
                    kwargs.get('commit', commit),
                    kwargs.get('force', False),
                    kwargs.get('logmsg')
                ),
                kwargs.get('logmsg')
            )
            self.repo.head.reset(index=True, working_tree=True)

            # Update the commit and branches
            self['hash'] = self.repo.commit().hexsha
            super(GitRepo, self).switch(str(self.repo.active_branch))
        except git.GitError as e:
            raise VCSError(f"{e.__class__.__name__}.{str(e)} creating branch {branch}")

    def push(self, branch: str, remote: str, *args, **kwargs) -> None:
        """
        Pushes a branch to a remote

        Args:
            branch (str): Name of the branch
            remote (str): Name of the remote
            *args (Tuple): Generic args
            **kwargs (Dict): Generic kwargs

        Returns:
            None

        Raises:
            VCSError: If errors occur during execution
        """
        try:
            if branch not in self.repo.remote(remote).refs:
                self.repo.remote(remote).push(branch, *args, **kwargs)
        except git.GitError as e:
            raise VCSError(f"{e.__class__.__name__}.{str(e)} pushing branch {branch}")

    def update(self, source: str = 'origin', branch: Optional[str] = None, *args: Tuple, **kwargs: Dict) -> None:
        """
        Merge the latest code into the current branch

        Args:
            source (str): Remote source to merge from, defaults to origin
            branch (str): Remote branch to merge from, defaults to master
            *args (Tuple): Generic args
            **kwargs (Dict): Generic kwargs

        Returns:
            None

        Raises:
            VCSError: If remote source does not exist
            VCSError: If remote branch does not exist
            VCSError: If errors occur during execution
        """
        # Handle case where remote source does not exist
        if source not in [r.name for r in self.repo.remotes]:
            raise VCSError(f"Remote {source} does not exist")

        # Default branch to current branch
        if branch is None:
            branch = self.branch

        # Handle case where remote branch does not exist
        if join(source, branch) not in [str(i) for i in self.repo.remote(source).refs]:
            raise VCSError(f"Branch {branch} does not exist in remote source {source}")

        # Pull data from remote
        try:
            self.repo.remote(source).pull(branch, *args, **kwargs)
        except git.GitError as e:
            raise VCSError(f"{e.__class__.__name__}.{str(e)} pulling data from {source}/{branch}")

        # Update the latest commit hash
        self['hash'] = self.repo.commit().hexsha

    def ignore(self, files: List[str], *args: Tuple, **kwargs: Dict) -> None:
        """
        Ignores a list of files

        Args:
            files (List[str]): List of file globs to be ignored, files are relative paths within repository directory
            *args (Tuple): Generic args
            **kwargs (Dict): Generic kwargs

        Returns:
            None

        Raises:
            VCSError: If errors occur during execution
        """
        try:
            data: List[str] = [f + '\n' for f in files]
            if not self.ignore_file.exists():
                self.ignore_file.create()
            self.ignore_file.export(data)
            self.ignore_data.extend(data)
        except Exception as e:
            raise VCSError(f"{e.__class__.__name__}.{str(e)} adding {files} to .gitignore")

    def remove_ignore(self, files: List[str], *args: Tuple, **kwargs: Dict) -> None:
        """
        Removes files that have been added to the .gitignore

        Args:
            files (List[str]): List of file globs to be removed, files are relative paths within repository directory
            *args (Tuple): Generic args
            **kwargs (Dict): Generic kwargs

        Returns:
            None

        Raises:
            VCSError: If errors occur during execution
        """
        try:
            data: List[str] = [f + '\n' for f in files]
            for f in data:
                try:
                    self.ignore_data.remove(f)
                except ValueError:
                    continue
            self.ignore_file.clear()
            self.ignore_file.export(self.ignore_data)
        except Exception as e:
            raise VCSError(f"{e.__class__.__name__}.{str(e)} adding {files} to .gitignore")

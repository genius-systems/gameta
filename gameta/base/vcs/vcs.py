
from abc import abstractmethod

from typing import Any, Optional, List, Dict, Tuple

from ..files import File


__all__ = ['VCS', 'GametaRepo']


class VCS(object):
    """
    Base client wrapper interface for VCS systems

    Attributes:
        name (str): Name of the interface
        path (str): Absolute path to the folder
        __interface (Optional[Any]): Wrapper around the interface
    """
    name: str = 'base'

    def __init__(self, path: str):
        self.path: str = path
        self.__interface: Optional[Any] = None

    @classmethod
    @abstractmethod
    def is_vcs_type(cls, path: str) -> bool:
        """
        Evaluates if path is a valid VCS repository

        Args:
            path (str): Absolute path to the VCS repository

        Returns:
            bool: If path is a valid VCS repository

        Raises:
            NotImplementedError: If method has not been implemented
        """
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def generate_repo(cls, path: str) -> 'GametaRepo':
        """
        Generates a GametaRepo along with the interface created

        Args:
            path (str): Absolute path to the repository

        Returns:
            GametaRepo: A GametaRepo instance

        Raises:
            VCSError: If operation fails
            NotImplementedError: If method has not been implemented
        """
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def init(cls, path: str) -> 'GametaRepo':
        """
        Initialises the path specified as a GametaRepo

        Args:
            path (str): Absolute path to the repository

        Returns:
            GametaRepo: Initialised GametaRepo instance

        Raises:
            VCSError: If operation fails
            NotImplementedError: If method has not been implemented
        """
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def clone(cls, path: str, url: str) -> 'GametaRepo':
        """
        Clones a new URL to the path specified and generates a GametaRepo instance

        Args:
            path (str): Absolute path to the clone destination
            url (str): URL to clone from

        Returns:
            GametaRepo: Initialised GametaRepo instance

        Raises:
            VCSError: If operation fails
            NotImplementedError: If method has not been implemented
        """
        raise NotImplementedError

    def __getattribute__(self, item):
        return self.__interface.__getattribute__(item)


class GametaRepo(object):
    """
    Base interface for a repository initialised by the VCS interface.

    Attributes:
        interface (VCS): VCS interface wrapper
        ignore_file (File): File that holds all the data to be ignored
        details (Optional[Dict[str, Any]]): Repository details if provided, defaults to an empty Dictionary
        *args (Tuple[Any]): Generic arguments
        **kwargs (Dict[str, Any]): Generic keyword arguments
    """
    def __init__(
            self,
            interface: 'VCS',
            ignore_file: 'File',
            details: Optional[Dict[str, Any]] = None,
            *args: Tuple[Any],
            **kwargs: Dict[str, Any]
    ):
        self.ignore_file: File = ignore_file
        self.interface: VCS = interface

        # Repository details
        self.__details: Dict[str, Any] = details or {}

    def __setitem__(self, key: str, value: Any) -> None:
        """
        Update repository details

        Args:
            key (str): Repository details key
            value (Any): Repository details value

        Returns:
            None
        """
        self.__details[key] = value

    def __getitem__(self, item) -> Any:
        """
        Retrieve repository detail

        Args:
            item (str): Key of item to be retrieved

        Returns:
            Any: Repository detail retrieved
        """
        return self.__details[item]

    @abstractmethod
    def fetch(self, *args: Tuple, **kwargs: Dict) -> None:
        """
        Fetches all updates

        Args:
            *args (Tuple): Generic args
            **kwargs (Dict): Generic kwargs

        Returns:
            None

        Raises:
            VCSError: If errors occur during execution
        """
        raise NotImplementedError

    @abstractmethod
    def switch(self, branch: str, *args: Tuple, **kwargs: Dict) -> None:
        """
        Switches to a specified branch, creating it if it does not exist

        Args:
            branch (str): Branch name
            *args (Tuple): Generic args
            **kwargs (Dict): Generic kwargs

        Returns:
            None

        Raises:
            VCSError: If errors occur during execution
        """
        self['branch'] = branch

    @abstractmethod
    def push(self, branch: str, remote: str, *args: Tuple, **kwargs: Dict) -> None:
        """
        Pushes a specified branch to a specified remote

        Args:
            branch (str): Name of the branch
            remote (str): Name of the remote
            *args (Tuple): Generic args
            **kwargs (Dict): Generic kwargs

        Returns:
            None
        """
        raise NotImplementedError

    @abstractmethod
    def update(self, source: str, branch: str, *args: Tuple, **kwargs: Dict) -> None:
        """
        Merge the latest code into the current branch

        Args:
            source (str): Remote source to merge from
            branch (str): Remote branch to merge from
            *args (Tuple): Generic args
            **kwargs (Dict): Generic kwargs

        Returns:
            None

        Raises:
            VCSError: If errors occur during execution
        """
        raise NotImplementedError

    @abstractmethod
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
        raise NotImplementedError

    @abstractmethod
    def remove_ignore(self, files: List[str], *args: Tuple, **kwargs: Dict) -> None:
        """
        Removes files that have been ignored so that they can be tracked

        Args:
            files (List[str]): List of file globs to be removed, files are relative paths within repository directory
            *args (Tuple): Generic args
            **kwargs (Dict): Generic kwargs

        Returns:
            None

        Raises:
            VCSError: If errors occur during execution
        """
        raise NotImplementedError

    @property
    def name(self) -> Optional[str]:
        """
        Returns the name of the repository

        Returns:
            Optional[str]: Name of the repository or none if uninitialised
        """
        return self.__details.get('name')

    @property
    def url(self) -> Optional[str]:
        """
        Returns the URL of the repository

        Returns:
            Optional[str]: URL of the repository or none if uninitialised
        """
        return self.__details.get('url')

    @property
    def branch(self) -> Optional[str]:
        """
        Returns the current branch repository is in

        Returns:
            Optional[str]: Name of the current branch or none if uninitialised
        """
        return self.__details.get('branch')

    @property
    def hash(self) -> Optional[str]:
        """
        Returns the current commit hash repository is in

        Returns:
            Optional[str]: Name of the current commit or none if uninitialised
        """
        return self.__details.get('hash')

    @property
    def path(self) -> Optional[str]:
        """
        Returns the current path to repository

        Returns:
            Optional[str]: Path of the current folder or none if uninitialised
        """
        return self.__details.get('path')

    @property
    def vcs(self) -> str:
        return self.interface.name

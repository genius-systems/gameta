from abc import abstractmethod
from os.path import exists, join
from typing import Any

__all__ = ['File']


class File(object):
    """
    Generic file interface for Gameta files

    Attributes:
        path (str): Absolute path to the folder containing the file
        file_name (str): Name of the reference file
    """

    def __init__(self, path: str, file_name: str):
        self.path = path
        self.file_name = file_name

    @property
    def file(self) -> str:
        """
        Returns the absolute path to the reference file

        Returns:
            str: Absolute path to the file
        """
        return join(self.path, self.file_name)

    def exists(self) -> bool:
        """
        Returns a boolean indicating if the file exists

        Returns:
            bool: Boolean indicator if the file exists
        """
        return exists(self.file)

    def create(self) -> None:
        """
        Creates an empty file

        Returns:
            None
        """
        with open(self.file, 'w+'):
            pass

    @abstractmethod
    def load(self) -> Any:
        """
        Abstractmethod to load and return data from the file

        Returns:
            Any
        """

    @abstractmethod
    def export(self, data: Any) -> None:
        """
        Abstractmethod to export data to the file

        Args:
            data (Any): Data to be exported

        Returns:
            None
        """
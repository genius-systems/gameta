import re

from abc import abstractmethod
from copy import deepcopy
from typing import Dict, List, Tuple

from jsonschema import Draft7Validator


__all__ = ['Schema', 'get_schema_version']


schema_expression: re.Pattern = re.compile(r'(?P<maj>[0-9]+)\.(?P<min>[0-9]+)\.(?P<patch>[0-9]+).*')


def get_schema_version(version: str) -> Tuple[int, int, int]:
    """
    Breaks down the schema version

    Returns:
        Tuple[int, int, int]: Parsed schema version
    """
    return tuple(int(i) for i in schema_expression.search(version).groups())


class Schema(object):
    """
    A generic class that represents a Gameta file schema and associated functionalities

    Attributes:
        version (str): Version string
        __schema (Dict): Schema document
        __validators (Dict[str, Draft7Validator]): JSON schema validators for schema version
        __reserved_params (Dict[str, List[str]): Reserved parameters for structured components in the schema
    """
    def __init__(self, version: str, schema: Dict):
        """
        Initialisation function

        Args:
            version (str): Schema version
        """
        self.version: str = version
        self.__schema: Dict = schema
        self.__validators: Dict[str, Draft7Validator] = {
            'gameta': Draft7Validator(self.__schema)
        }
        self.__validators.update({k: Draft7Validator(v) for k, v in self.__schema['definitions'].items()})
        self.__reserved_params: Dict[str, List[str]] = {
            p: list(self.schema['definitions'][p]['properties'].keys())
            for p in ['repositories', 'commands']
        }

    @property
    def schema(self) -> Dict:
        """
        Returns a copy of the underlying Gameta schema document

        Returns:
            Dict: Schema document
        """
        return deepcopy(self.__schema)

    @property
    def validators(self) -> Dict[str, Draft7Validator]:
        """
        Returns a copy of all the relevant validators used to validate a Gameta schema of a particular version

        Returns:
            Dict[str, Draft7Validator]: JSON schema validators indexed by component type
        """
        return deepcopy(self.__validators)

    @property
    def reserved_params(self) -> Dict[str, List[str]]:
        """
        Returns a copy of the reserved parameters for structured components within a Gameta schema

        Returns:
            Dict[str, List[str]]: Reserved parameters index
        """
        return deepcopy(self.__reserved_params)

    @property
    @abstractmethod
    def structures(self) -> Dict[str, Dict]:
        """
        Returns a set of dictionaries that structure input for each class of objects, containing all default values
        that differ from the previous version

        Returns:
            Dict[str, Dict]: Dictionary of structures
        """

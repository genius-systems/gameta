import re
from copy import deepcopy
from typing import Dict, List, Pattern, Tuple

from jsonschema import Draft7Validator

__all__ = ["Schema", "to_schema_tuple", "to_schema_str"]


schema_expression: Pattern = re.compile(
    r"(?P<maj>[0-9]+)\.(?P<min>[0-9]+)\.(?P<patch>[0-9]+).*"
)


def to_schema_tuple(version: str) -> Tuple[int, int, int]:
    """
    Converts a schema version string into schema version tuple

    Args:
        version (str): Schema version string

    Returns:
        Tuple[int, int, int]: Schema version tuple
    """
    return tuple(int(i) for i in schema_expression.search(version).groups())


def to_schema_str(version: Tuple[int, int, int]) -> str:
    """
    Converts a schema version tuple into a schema version string

    Args:
        version (Tuple[int, int, int]): Schema version tuple

    Returns:
        str: Schema version string
    """
    if not version or any(not isinstance(i, int) for i in version):
        raise TypeError("Invalid version")
    return ".".join(str(i) for i in version)


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
            "gameta": Draft7Validator(self.__schema)
        }
        self.__validators.update(
            {k: Draft7Validator(v) for k, v in self.__schema["definitions"].items()}
        )
        self.__reserved_params: Dict[str, List[str]] = {
            p: list(self.schema["definitions"][p]["properties"].keys())
            for p in ["repositories", "commands"]
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

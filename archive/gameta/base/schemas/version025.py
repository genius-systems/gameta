from typing import Dict, Type

from .schema import Schema

__all__ = ['v025']


class Version025Schema(Schema):
    """
    Schema for Gameta schema version 0.2.5
    """

    @property
    def structures(self) -> Dict[str, Dict]:
        """
        Returns a set of dictionaries that structure input for each schema class object, containing all default values
        versus the previous version

        Returns:
            Dict[str, Dict]: Dictionary of structures
        """
        return {
            'repositories': {},
            'commands': {},
        }


v025: Version025Schema = Version025Schema(
    version='0.2.5',
    schema={
        '$schema': "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "repositories": {
                "type": "object",
                "additionalProperties": {
                    "$ref": "#/definitions/repositories"
                }
            },
            "commands": {
                "type": "object",
                "additionalProperties": {
                    "$ref": "#/definitions/commands"
                }
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
                    "description": {
                        "type": "string"
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
                "maxProperties": 8,
                "additionalProperties": False,
            },
            "constants": {
                "type": "object",
                "propertyNames": {
                    "pattern": "^[$A-Z0-9_-]"
                }
            }
        }
    }
)

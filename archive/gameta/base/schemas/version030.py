from typing import Dict

from .schema import Schema

__all__ = ['v030']


class Version030Schema(Schema):
    """
    Schema for Gameta schema version 0.3.0
    """

    def structures(self) -> Dict[str, Dict]:
        """
        Returns a set of dictionaries that structure input for each schema class object, containing all default values
        when upgrading from 0.2.X version

        Returns:
            Dict[str, Dict]: Dictionary of structures
        """
        return {
            'repositories': {},
            'commands': {
                'all': False,
                'venv': None,
            },
            'virtualenvs': {},
        }


v030: Version030Schema = Version030Schema(
    version='0.3.0',
    schema={
        '$schema': "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "version": {
                "type": "string",
                "pattern": "^([0-9]+.){2}([0-9]+[ab]?[0-9]?)$"
            },
            "virtualenvs": {
                "$ref": "#/definitions/virtualenvs"
            },
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
                "version"
            ]
        },
        'definitions': {
            "virtualenvs": {
                "type": "object",
                "propertyNames": {
                    "pattern": "^[a-zA-Z0-9_-]+$"
                },
                "additionalProperties": {
                    "type": "string"
                }
            },
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
                    "all": {
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
                    },
                    "venv": {
                        "type": ["string", "null"]
                    }
                },
                "minProperties": 10,
                "maxProperties": 10,
                "additionalProperties": False,
            },
            "constants": {
                "type": "object",
                "propertyNames": {
                    "pattern": "^\$?[A-Z0-9_-]+$"
                }
            }
        }
    }
)

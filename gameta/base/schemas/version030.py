
from .schema import Schema


__all__ = ['v030']


v030: Schema = Schema(
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
                        "format": "uri",
                        "default": None
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
                    "vcs": {
                        "type": "string",
                        "enum": ["git"],
                        "default": "git"
                    },
                    "__metarepo__": {
                        "type": "boolean",
                        "default": False
                    }
                },
                "required": [
                    "url", "path", "__metarepo__", "vcs"
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
                        "type": "string",
                        "default": ""
                    },
                    "raise_errors": {
                        "type": "boolean",
                        "default": False
                    },
                    "all": {
                        "type": "boolean",
                        "default": False
                    },
                    "shell": {
                        "type": "boolean",
                        "default": False
                    },
                    "verbose": {
                        "type": "boolean",
                        "default": False,
                    },
                    "debug": {
                        "type": "boolean",
                        "default": False
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
                        "type": ["string", "null"],
                        "default": None
                    },
                    "sep": {
                        "type": "string",
                        "enum": ["&&", "||", ";"],
                        "default": "&&"
                    }
                },
                "minProperties": 11,
                "maxProperties": 11,
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

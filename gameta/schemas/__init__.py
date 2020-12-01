
from gameta.cli import gameta_cli
from gameta.context import gameta_context, GametaContext


__all__ = ['schema_cli', 'schemas']


schemas = {
    ('0', '2'): {
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
    },
    ('0', '3'): {
        '$schema': "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "version": {
                "$ref": "#/definitions/version"
            },
            "virtualenvs": {
                "$ref": "#/definitions/virtualenvs"
            },
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
                "version", "repositories"
            ]
        },
        'definitions': {
            "version": {
                "type": "string",
                "pattern": "^([0-9].){2}([0-9]){1}(.?[ab0-9]){1}?$"
            },
            "virtualenvs": {
                "type": "object",
                "propertyNames": {
                    "pattern": "^[a-zA-Z0-9_-]"
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
                    "pattern": "^[$A-Z0-9_-]"
                }
            }
        }
    }
}


@gameta_cli.command("schema")
@gameta_context
def schema_cli(context: GametaContext) -> None:
    """
    Updates the schema version of the .meta file to the latest Gameta schema version

    Args:
        context (GametaContext): Gameta Context

    Returns:
        None

    Raises:
        click.ClickException: If errors occur during processing
    """

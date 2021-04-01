
from .schema import Schema


__all__ = ['v025']


v025: Schema = Schema(
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

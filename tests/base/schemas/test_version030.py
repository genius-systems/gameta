from unittest import TestCase

from gameta.base import supported_versions


class TestVersion030Schema(TestCase):
    def setUp(self) -> None:
        self.maxDiff = None
        self.schema = supported_versions[(0, 3, 0)]
        self.validators = self.schema.validators

    def test_schema_version_valid_schema(self):
        test_schema = {
            "version": "0.3.0a1",
            "repositories": {
                "gameta": {
                    "__metarepo__": True,
                    "path": ".",
                    "tags": [
                        "metarepo"
                    ],
                    "url": "git@github.com:genius-systems/gameta.git",
                    "vcs": "git"
                },
                "GitPython": {
                    "__metarepo__": False,
                    "path": "GitPython",
                    "tags": [
                        "a",
                        "b",
                        "c"
                    ],
                    "url": "https://github.com/gitpython-developers/GitPython.git",
                    "vcs": "git"
                },
                "gitdb": {
                    "__metarepo__": False,
                    "path": "core/gitdb",
                    "tags": [
                        "a",
                        "c",
                        "d"
                    ],
                    "url": "https://github.com/gitpython-developers/gitdb.git",
                    "vcs": "git"
                }
            },
            "commands": {
                "hello_world": {
                    "commands": [
                        "git fetch --all --tags --prune"
                    ],
                    "description": "",
                    "tags": [
                        "a",
                        "b"
                    ],
                    "repositories": [
                        "gameta"
                    ],
                    "verbose": False,
                    "all": True,
                    "shell": False,
                    "debug": False,
                    "sep": "&&",
                    "venv": None,
                    "raise_errors": True
                },
                "hello_world2": {
                    "commands": [
                        "git fetch --all --tags --prune"
                    ],
                    "description": "",
                    "tags": [
                        "a",
                        "b"
                    ],
                    "repositories": [
                        "gameta"
                    ],
                    "verbose": False,
                    "all": True,
                    "shell": False,
                    "debug": False,
                    "sep": "&&",
                    "venv": None,
                    "raise_errors": True
                },
                "hello_world3": {
                    "commands": [
                        "from random import choice\nfrom string import ascii_lowercase, ascii_uppercase, digits, punctuation\nwith open(\"{ENCRYPTION_FILE_NAME}\", \"w\") as f:\n    f.write(\"\".join([choice(ascii_lowercase + ascii_uppercase + digits + punctuation) for _ in range({KEY_LEN})]))"
                    ],
                    "description": "",
                    "tags": [],
                    "repositories": [
                        "gameta"
                    ],
                    "verbose": False,
                    "all": False,
                    "shell": False,
                    "debug": False,
                    "sep": "&&",
                    "venv": None,
                    "raise_errors": True
                }
            },
            "constants": {
                "ENCRYPTION_FILE_NAME": "encryption.txt",
                "KEY_LEN": 16,
                "$TEST1": "hello"
            },
            "virtualenvs": {
                "hello_world": "path/to/virtualenv",
                "hello": "path/to/virtualenv"
            }
        }
        self.assertTrue(self.validators['gameta'].is_valid(test_schema))

    def test_schema_version_invalid_version_invalid_version_number(self):
        test_schemas = {
            "version": "0.3.X"
        }
        self.assertFalse(self.validators['gameta'].is_valid(test_schemas))

    def test_schema_version_invalid_version_missing_version_number(self):
        test_schemas = {
            'version': '0.3'
        }
        self.assertFalse(self.validators['gameta'].is_valid(test_schemas))

    def test_schema_version_invalid_version_null_version(self):
        test_schemas = {
            'version': None
        }
        self.assertFalse(self.validators['gameta'].is_valid(test_schemas))


    def test_schema_version_invalid_version_empty_version(self):
        test_schemas = {
            'version': ''
        }
        self.assertFalse(self.validators['gameta'].is_valid(test_schemas))

    def test_schema_version_invalid_version_invalid_string(self):
        test_schemas = {
            'version': 'asdf'
        }
        self.assertFalse(self.validators['gameta'].is_valid(test_schemas))

    def test_schema_version_invalid_version_invalid_test_release(self):
        test_schemas = {
            'version': '1.3.3c2'
        }
        self.assertFalse(self.validators['gameta'].is_valid(test_schemas))

    def test_schema_version_invalid_version_additional_characters(self):
        test_schemas = {
            "version": "0.3.1!"
        }
        self.assertFalse(self.validators['gameta'].is_valid(test_schemas))

    def test_schema_version_invalid_repositories_(self):
        test_schemas = {
            'missing_required_field': {
                "path": ".",
                "tags": [
                    "metarepo"
                ],
                "url": "git@github.com:genius-systems/gameta.git"
            },
            'invalid_path_type': {
                "__metarepo__": True,
                "path": None,
                "tags": [
                    "metarepo"
                ],
                "url": "git@github.com:genius-systems/gameta.git"
            },
            'invalid_tags_type': {
                "__metarepo__": True,
                "path": None,
                "tags": [
                    1.0, 1, None, False
                ],
                "url": "git@github.com:genius-systems/gameta.git"
            },
        }
        for schema in test_schemas.values():
            self.assertFalse(self.validators['repositories'].is_valid(schema))

    def test_schema_version_invalid_repositories_missing_required_field(self):
        test_schemas = {
            "path": ".",
            "tags": [
                "metarepo"
            ],
            "url": "git@github.com:genius-systems/gameta.git"
        }
        self.assertFalse(self.validators['repositories'].is_valid(test_schemas))

    def test_schema_version_invalid_repositories_invalid_path_type(self):
        test_schemas = {
            "__metarepo__": True,
            "path": None,
            "tags": [
                "metarepo"
            ],
            "url": "git@github.com:genius-systems/gameta.git"
        }
        self.assertFalse(self.validators['repositories'].is_valid(test_schemas))

    def test_schema_version_invalid_repositories_invalid_tags_type(self):
        test_schemas = {
            "__metarepo__": True,
            "path": None,
            "tags": [
                1.0, 1, None, False
            ],
            "url": "git@github.com:genius-systems/gameta.git"
        }
        self.assertFalse(self.validators['repositories'].is_valid(test_schemas))

    def test_schema_version_invalid_constants_invalid_case(self):
        test_schemas = {
            "hello": "world!"
        }
        self.assertFalse(self.validators['constants'].is_valid(test_schemas))

    def test_schema_version_invalid_constants_restricted_characters(self):
        test_schemas = {
            "HELLO&#*#(@)!}{": "world!"
        }
        self.assertFalse(self.validators['constants'].is_valid(test_schemas))

    def test_schema_version_invalid_constants_only_dollars(self):
        test_schemas = {
            "$": "world!",
        }
        self.assertFalse(self.validators['constants'].is_valid(test_schemas))

    def test_schema_version_invalid_constants_spacings(self):
        test_schemas = {
            "hello world": "world!",
        }
        for schema in test_schemas.values():
            self.assertFalse(self.validators['constants'].is_valid(schema))

    def test_schema_version_invalid_constants_new_line(self):
        test_schemas = {
            "hello\nworld": "world!",
        }
        self.assertFalse(self.validators['constants'].is_valid(test_schemas))

    def test_schema_version_invalid_constants_tabs(self):
        test_schemas = {
            "hello\tworld": "world!",
        }
        self.assertFalse(self.validators['constants'].is_valid(test_schemas))

    def test_schema_version_invalid_virtualenvs_spacings(self):
        test_schemas = {
            "hello world": "path/to/virtualenv"
        }
        self.assertFalse(self.validators['virtualenvs'].is_valid(test_schemas))

    def test_schema_version_invalid_virtualenvs_tabs(self):
        test_schemas = {
            "hello\tworld": "path/to/virtualenv"
        }
        self.assertFalse(self.validators['virtualenvs'].is_valid(test_schemas))

    def test_schema_version_invalid_virtualenvs_new_line(self):
        test_schemas = {
            "hello\nworld": "path/to/virtualenv"
        }
        self.assertFalse(self.validators['virtualenvs'].is_valid(test_schemas))

    def test_schema_version_invalid_virtualenvs_restricted_characters(self):
        test_schemas = {
            "hello_world:\"'+$&#*@(){}": "path/to/virtualenv"
        }
        self.assertFalse(self.validators['virtualenvs'].is_valid(test_schemas))

    def test_schema_version_invalid_virtualenvs_empty_name_string(self):
        test_schemas = {
            "": "world!",
        }
        self.assertFalse(self.validators['virtualenvs'].is_valid(test_schemas))

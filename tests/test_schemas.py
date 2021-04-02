import json
from os.path import join, dirname
from pprint import pformat
from shutil import copytree
from unittest import TestCase

from click.testing import CliRunner

from gameta import __version__
from gameta.base import supported_versions, to_schema_tuple
from gameta.schemas import schema_cli, validate, ls


class TestSchemaCli(TestCase):
    def setUp(self) -> None:
        self.maxDiff = None
        self.runner = CliRunner()
        self.schema = schema_cli

    def test_schema_cli_print_schema(self):
        params = {'version': '0.3.0'}
        with self.runner.isolated_filesystem() as f:
            result = self.runner.invoke(self.schema, ['-s', params['version']])
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                f"Printing schema version {params['version']}:\n" +
                pformat(supported_versions[to_schema_tuple(params['version'])].schema) + '\n'
            )

    def test_schema_cli_print_non_existent_schema(self):
        params = {'version': '0.1.1'}
        with self.runner.isolated_filesystem() as f:
            result = self.runner.invoke(self.schema, ['-s', params['version']])
            self.assertEqual(result.exit_code, 1)
            self.assertEqual(
                result.output,
                f"Error: Gameta schema version {params['version']} is not supported by Gameta version {__version__}\n"
            )



class TestSchemaValidate(TestCase):
    def setUp(self) -> None:
        self.maxDiff = None
        self.runner = CliRunner()
        self.validate = validate

    def test_validate_gameta_schema_missing(self):
        with self.runner.isolated_filesystem() as f:
            result = self.runner.invoke(self.validate)
            self.assertEqual(result.exit_code, 1)
            self.assertEqual(
                result.output,
                f"Error: Could not load .gameta data from path {join(f, '.gameta', '.gameta')} provided due to "
                f"FileNotFoundError.[Errno 2] No such file or directory: '{join(f, '.gameta', '.gameta')}'\n"
            )

    def test_validate_gameta_schema_does_not_exist(self):
        params = {
            'version': '0.1.1'
        }
        with self.runner.isolated_filesystem() as f:
            copytree(join(dirname(__file__), 'data', 'gameta_multi_repos_only'), f, dirs_exist_ok=True)
            with open(join(f, '.gameta', '.gameta'), 'r+') as m:
                output = json.load(m)
                output['version'] = params['version']
            with open(join(f, '.gameta', '.gameta'), 'w') as m:
                json.dump(output, m)
            result = self.runner.invoke(self.validate)
            self.assertEqual(result.exit_code, 1)
            self.assertEqual(
                result.output,
                f"Error: Gameta schema version {params['version']} is not supported by Gameta version {__version__}\n"
            )

    def test_validate_gameta_schema_invalid(self):
        params = {
            'repositories': {
                "invalid_repository": {
                    'path': None,
                    '__metarepo__': False,
                    'url': 'http://test.git'
                }
            },
            'commands': {
                "invalid_command": {
                    'commands': ['git fetch --all --tags --prune'],
                    'description': '',
                    'tags': ['a', 'b'],
                    'repositories': ['gameta'],
                    'verbose': False,
                    'all': True,
                    'raise_errors': True
                }
            },
            'virtualenvs': {
                'hello!': 'path/to/venv',
                'world!': 'path/to/venv'
            },
            'constants': {
                'hello': 'world'
            },
        }
        with self.runner.isolated_filesystem() as f:
            copytree(join(dirname(__file__), 'data', 'gameta_multi_repos_only'), f, dirs_exist_ok=True)
            with open(join(f, '.gameta', '.gameta'), 'r+') as m:
                output = json.load(m)
                output['repositories'].update(params['repositories'])
                output['commands'] = params['commands']
                output['virtualenvs'] = params['virtualenvs']
                output['constants'] = params['constants']
            with open(join(f, '.gameta', '.gameta'), 'w') as m:
                json.dump(output, m)
            result = self.runner.invoke(self.validate, ['-s', '0.3.0'])
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                f"Validating .gameta schema found in {join(f, '.gameta', '.gameta')}\n"
                f"Validation errors associated with .gameta schema found in {join(f, '.gameta', '.gameta')}\n"
                "Section virtualenvs:\n"
                "\tEntry: hello!, error: ValidationError 'hello!' does not match '^[a-zA-Z0-9_-]+$'\n"
                "\tEntry: world!, error: ValidationError 'world!' does not match '^[a-zA-Z0-9_-]+$'\n"
                "Section repositories:\n"
                "\tEntry: invalid_repository, error: ValidationError None is not of type 'string'\n"
                "Section commands:\n"
                "\tEntry: invalid_command, error: ValidationError "
                "{'commands': ['git fetch --all --tags --prune'], "
                "'description': '', 'tags': ['a', 'b'], 'repositories': ['gameta'], 'verbose': False, "
                "'all': True, 'raise_errors': True} does not have enough properties\n"
                "Section constants:\n"
                '\t' r"Entry: hello, error: ValidationError 'hello' does not match '^\\$?[A-Z0-9_-]+$'" '\n'
            )

    def test_validate_gameta_schema_valid(self):
        params = {
            'commands': {
                'hello_world': {
                    'commands': ['git fetch --all --tags --prune'],
                    'description': '',
                    'tags': ['a', 'b'],
                    'repositories': ['gameta'],
                    'verbose': False,
                    'all': True,
                    'shell': False,
                    'debug': False,
                    'sep': '&&',
                    'venv': None,
                    'raise_errors': True
                }
            },
            'virtualenvs': {
                'hello_world': 'path/to/venv'
            },
            'constants': {
                'HELLO': 'world'
            },
        }
        with self.runner.isolated_filesystem() as f:
            copytree(join(dirname(__file__), 'data', 'gameta_multi_repos_only'), f, dirs_exist_ok=True)
            with open(join(f, '.gameta', '.gameta'), 'r+') as m:
                output = json.load(m)
                output['commands'] = params['commands']
                output['virtualenvs'] = params['virtualenvs']
                output['constants'] = params['constants']
            with open(join(f, '.gameta', '.gameta'), 'w') as m:
                json.dump(output, m)
            result = self.runner.invoke(self.validate)
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                f"Validating .gameta schema found in {join(f, '.gameta', '.gameta')}\n"
                f"There are no validation errors associated with .gameta schema found in "
                f"{join(f, '.gameta', '.gameta')}\n"
            )

    def test_validate_gameta_schema_validate_against_different_schema(self):
        params = {
            'commands': {
                'hello_world': {
                    'commands': ['git fetch --all --tags --prune'],
                    'description': '',
                    'tags': ['a', 'b'],
                    'repositories': ['gameta'],
                    'verbose': False,
                    'all': True,
                    'shell': False,
                    'debug': False,
                    'sep': '&&',
                    'venv': None,
                    'raise_errors': True
                }
            },
            'virtualenvs': {
                'hello_world': 'path/to/venv'
            },
            'constants': {
                'HELLO': 'world'
            },
        }
        with self.runner.isolated_filesystem() as f:
            copytree(join(dirname(__file__), 'data', 'gameta_multi_repos_only'), f, dirs_exist_ok=True)
            with open(join(f, '.gameta', '.gameta'), 'r+') as m:
                output = json.load(m)
                output['commands'] = params['commands']
                output['virtualenvs'] = params['virtualenvs']
                output['constants'] = params['constants']
            with open(join(f, '.gameta', '.gameta'), 'w') as m:
                json.dump(output, m)
            result = self.runner.invoke(self.validate, ['-s', '0.2.7'])
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                f"Validating .gameta schema found in {join(f, '.gameta', '.gameta')}\n"
                f"Validation errors associated with .gameta schema found in {join(f, '.gameta', '.gameta')}\n"
                "Section commands:\n"
                "\tEntry: hello_world, error: ValidationError {'commands': ['git fetch --all --tags --prune'], "
                "'description': '', 'tags': ['a', 'b'], 'repositories': ['gameta'], 'verbose': False, 'all': True, "
                "'shell': False, 'debug': False, 'sep': '&&', 'venv': None, 'raise_errors': True} has too many "
                "properties\n"
            )
            result = self.runner.invoke(self.validate)
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                f"Validating .gameta schema found in {join(f, '.gameta', '.gameta')}\n"
                f"There are no validation errors associated with .gameta schema found in "
                f"{join(f, '.gameta', '.gameta')}\n"
            )

    def test_validate_gameta_schema_from_path(self):
        params = {
            'commands': {
                'hello_world': {
                    'commands': ['git fetch --all --tags --prune'],
                    'description': '',
                    'tags': ['a', 'b'],
                    'repositories': ['gameta'],
                    'verbose': False,
                    'all': True,
                    'shell': False,
                    'debug': False,
                    'sep': '&&',
                    'venv': None,
                    'raise_errors': True
                }
            },
            'virtualenvs': {
                'hello_world': 'path/to/venv'
            },
            'constants': {
                'HELLO': 'world'
            },
        }
        with self.runner.isolated_filesystem() as f:
            copytree(join(dirname(__file__), 'data', 'gameta_multi_repos_only'), join(f, 'test'))
            with open(join(f, 'test', '.gameta', '.gameta'), 'r+') as m:
                output = json.load(m)
                output['commands'] = params['commands']
                output['virtualenvs'] = params['virtualenvs']
                output['constants'] = params['constants']
            with open(join(f, 'test', '.gameta', '.gameta'), 'w') as m:
                json.dump(output, m)
            result = self.runner.invoke(self.validate, ['--path', join(f, 'test')])
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                f"Validating .gameta schema found in {join(f, 'test', '.gameta', '.gameta')}\n"
                f"There are no validation errors associated with .gameta schema found in "
                f"{join(f, 'test', '.gameta', '.gameta')}\n"
            )

    def test_validate_gameta_schema_invalid_verbose(self):
        params = {
            'repositories': {
                "invalid_repository": {
                    'path': None,
                    '__metarepo__': False,
                    'url': 'http://test.git'
                }
            },
            'commands': {
                "invalid_command": {
                    'commands': ['git fetch --all --tags --prune'],
                    'description': '',
                    'tags': ['a', 'b'],
                    'repositories': ['gameta'],
                    'verbose': False,
                    'all': True,
                    'raise_errors': True
                }
            },
            'virtualenvs': {
                'hello!': 'path/to/venv',
                'world!': 'path/to/venv'
            },
            'constants': {
                'hello': 'world'
            },
        }
        with self.runner.isolated_filesystem() as f:
            copytree(join(dirname(__file__), 'data', 'gameta_multi_repos_only'), f, dirs_exist_ok=True)
            with open(join(f, '.gameta', '.gameta'), 'r+') as m:
                output = json.load(m)
                output['repositories'].update(params['repositories'])
                output['commands'] = params['commands']
                output['virtualenvs'] = params['virtualenvs']
                output['constants'] = params['constants']
            with open(join(f, '.gameta', '.gameta'), 'w') as m:
                json.dump(output, m)
            result = self.runner.invoke(self.validate, ['-v'])
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                f"Validating .gameta schema found in {join(f, '.gameta', '.gameta')}\n"
                f"Validation errors associated with .gameta schema found in {join(f, '.gameta', '.gameta')}\n"
                "Section virtualenvs:\n"
                "\tEntry: hello!, error: ValidationError 'hello!' does not match '^[a-zA-Z0-9_-]+$'\n"
                "\nFailed validating 'pattern' in schema['propertyNames']:\n"
                "    {'pattern': '^[a-zA-Z0-9_-]+$'}\n"
                "\nOn instance:\n"
                "    'hello!'\n"
                "\tEntry: world!, error: ValidationError 'world!' does not match '^[a-zA-Z0-9_-]+$'\n"
                "\nFailed validating 'pattern' in schema['propertyNames']:\n"
                "    {'pattern': '^[a-zA-Z0-9_-]+$'}\n"
                "\nOn instance:\n"
                "    'world!'\n"
                "Section repositories:\n"
                "\tEntry: invalid_repository, error: ValidationError None is not of type 'string'\n"
                "\nFailed validating 'type' in schema['properties']['path']:\n"
                "    {'type': 'string'}\n"
                "\nOn instance['path']:\n"
                "    None\n"
                "Section commands:\n"
                "\tEntry: invalid_command, error: ValidationError "
                "{'commands': ['git fetch --all --tags --prune'], "
                "'description': '', 'tags': ['a', 'b'], 'repositories': ['gameta'], 'verbose': False, "
                "'all': True, 'raise_errors': True} does not have enough properties\n"
                "\nFailed validating 'minProperties' in schema:\n"
                "    {'additionalProperties': False,\n"
                "     'maxProperties': 11,\n"
                "     'minProperties': 11,\n"
                "     'properties': {'all': {'default': False, 'type': 'boolean'},\n"
                "                    'commands': {'items': {'type': 'string'},\n"
                "                                 'type': 'array'},\n"
                "                    'debug': {'default': False, 'type': 'boolean'},\n"
                "                    'description': {'default': '', 'type': 'string'},\n"
                "                    'raise_errors': {'default': False, 'type': 'boolean'},\n"
                "                    'repositories': {'items': {'type': 'string'},\n"
                "                                     'type': 'array'},\n"
                "                    'sep': {'default': '&&',\n"
                "                            'enum': ['&&', '||', ';'],\n"
                "                            'type': 'string'},\n"
                "                    'shell': {'default': False, 'type': 'boolean'},\n"
                "                    'tags': {'items': {'type': 'string'}, 'type': 'array'},\n"
                "                    'venv': {'default': None, 'type': ['string', 'null']},\n"
                "                    'verbose': {'default': False, 'type': 'boolean'}},\n"
                "     'type': 'object'}\n"
                "\nOn instance:\n"
                "    {'all': True,\n"
                "     'commands': ['git fetch --all --tags --prune'],\n"
                "     'description': '',\n"
                "     'raise_errors': True,\n"
                "     'repositories': ['gameta'],\n"
                "     'tags': ['a', 'b'],\n"
                "     'verbose': False}\n"
                "Section constants:\n"
                "\tEntry: hello, error: ValidationError 'hello' does not match '^\\\$?[A-Z0-9_-]+$'\n"
                "\nFailed validating 'pattern' in schema['propertyNames']:\n"
                "    {'pattern': '^\\\$?[A-Z0-9_-]+$'}\n"
                "\nOn instance:\n"
                "    'hello'\n"
            )


class TestSchemaLs(TestCase):
    def setUp(self) -> None:
        self.maxDiff = None
        self.runner = CliRunner()
        self.ls = ls

    def test_schema_ls_all(self):
        with self.runner.isolated_filesystem() as f:
            result = self.runner.invoke(self.ls)
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                f"Supported schema versions: 0.2.5, 0.2.6, 0.2.7, 0.3.0\n"
            )

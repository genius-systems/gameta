import json
from os import makedirs
from os.path import dirname, join
from shutil import copyfile
from unittest import TestCase

from click.testing import CliRunner

from gameta import __version__
from gameta.schemas import ls, update, validate


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
                f"Error: Could not load .gameta data from path {join(f, '.gameta')} provided due to "
                f"FileNotFoundError.[Errno 2] No such file or directory: '{join(f, '.gameta')}'\n"
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
            with open(join(dirname(__file__), 'data', '.gameta_other_repos'), 'r') as m1:
                output = json.load(m1)
                with open(join(f, '.gameta'), 'w') as m2:
                    output['repositories'].update(params['repositories'])
                    output['commands'] = params['commands']
                    output['virtualenvs'] = params['virtualenvs']
                    output['constants'] = params['constants']
                    json.dump(output, m2)
            result = self.runner.invoke(self.validate)
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                f"Validating .gameta schema found in {join(f, '.gameta')}\n"
                f"Validation errors associated with .gameta schema found in {join(f, '.gameta')}\n"
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
                "\tEntry: hello, error: ValidationError 'hello' does not match '^\\\$?[A-Z0-9_-]+$'\n"
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
                    'python': False,
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
            with open(join(dirname(__file__), 'data', '.gameta_other_repos'), 'r') as m1:
                output = json.load(m1)
                with open(join(f, '.gameta'), 'w') as m2:
                    output['commands'] = params['commands']
                    output['virtualenvs'] = params['virtualenvs']
                    output['constants'] = params['constants']
                    json.dump(output, m2)
            result = self.runner.invoke(self.validate)
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                f"Validating .gameta schema found in {join(f, '.gameta')}\n"
                f"There are no validation errors associated with .gameta schema found in {join(f, '.gameta')}\n"
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
                    'python': False,
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
            makedirs(join(f, 'test'))
            with open(join(dirname(__file__), 'data', '.gameta_other_repos'), 'r') as m1:
                output = json.load(m1)
                with open(join(f, 'test', '.gameta'), 'w') as m2:
                    output['commands'] = params['commands']
                    output['virtualenvs'] = params['virtualenvs']
                    output['constants'] = params['constants']
                    json.dump(output, m2)
            result = self.runner.invoke(self.validate, ['--path', join(f, 'test')])
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                f"Validating .gameta schema found in {join(f, 'test', '.gameta')}\n"
                f"There are no validation errors associated with .gameta schema found in {join(f, 'test', '.gameta')}\n"
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
            with open(join(dirname(__file__), 'data', '.gameta_other_repos'), 'r') as m1:
                output = json.load(m1)
                with open(join(f, '.gameta'), 'w') as m2:
                    output['repositories'].update(params['repositories'])
                    output['commands'] = params['commands']
                    output['virtualenvs'] = params['virtualenvs']
                    output['constants'] = params['constants']
                    json.dump(output, m2)
            result = self.runner.invoke(self.validate, ['-v'])
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                f"Validating .gameta schema found in {join(f, '.gameta')}\n"
                f"Validation errors associated with .gameta schema found in {join(f, '.gameta')}\n"
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
                "     'maxProperties': 10,\n"
                "     'minProperties': 10,\n"
                "     'properties': {'all': {'type': 'boolean'},\n"
                "                    'commands': {'items': {'type': 'string'},\n"
                "                                 'type': 'array'},\n"
                "                    'description': {'type': 'string'},\n"
                "                    'python': {'type': 'boolean'},\n"
                "                    'raise_errors': {'type': 'boolean'},\n"
                "                    'repositories': {'items': {'type': 'string'},\n"
                "                                     'type': 'array'},\n"
                "                    'shell': {'type': 'boolean'},\n"
                "                    'tags': {'items': {'type': 'string'}, 'type': 'array'},\n"
                "                    'venv': {'type': ['string', 'null']},\n"
                "                    'verbose': {'type': 'boolean'}},\n"
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


class TestSchemaUpdate(TestCase):
    def setUp(self) -> None:
        self.maxDiff = None
        self.runner = CliRunner()
        self.update = update

    def test_schema_update_successful_update(self):
        test_params = {
            'curr_version': '0.2.5',
            'desired_version': __version__
        }
        with self.runner.isolated_filesystem() as f:
            with open(join(dirname(__file__), 'data', '.gameta_v025'), 'r') as m1:
                output = json.load(m1)
                with open(join(f, '.gameta'), 'w') as m2:
                    output['repositories']['gameta']['test_param'] = 'test'
                    json.dump(output, m2)
            result = self.runner.invoke(self.update)
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                f"Updating current Gameta schema ({test_params['curr_version']}) "
                f"to version {test_params['desired_version']}\n"
                f"Successfully updated schema from {test_params['curr_version']} to {test_params['desired_version']}\n"
            )
            with open(join(f, '.gameta')) as g:
                self.assertEqual(
                    json.load(g),
                    {
                        'commands': {
                            'hello_world': {
                                'commands': ['git fetch --all --tags --prune'],
                                'description': '',
                                'python': False,
                                'raise_errors': True,
                                'repositories': ['gameta'],
                                'shell': False,
                                'tags': ['a', 'b'],
                                'verbose': False
                            },
                            'hello_world2': {
                                'commands': ['git fetch --all --tags --prune'],
                                'description': '',
                                'python': False,
                                'raise_errors': True,
                                'repositories': ['gameta'],
                                'shell': False,
                                'tags': ['a', 'b'],
                                'verbose': False
                            },
                            'hello_world3': {
                                'commands': ['from random import choice\n'
                                             'from string import '
                                             'ascii_lowercase, ascii_uppercase, '
                                             'digits, punctuation\n'
                                             'with '
                                             'open("{ENCRYPTION_FILE_NAME}", '
                                             '"w") as f:\n'
                                             '    '
                                             'f.write("".join([choice(ascii_lowercase '
                                             '+ ascii_uppercase + digits + '
                                             'punctuation) for _ in '
                                             'range({KEY_LEN})]))'],
                                'description': '',
                                'python': True,
                                'raise_errors': True,
                                'repositories': ['gameta'],
                                'shell': False,
                                'tags': [],
                                'verbose': False
                            }
                        },
                        'repositories': {
                            'GitPython': {
                                '__metarepo__': False,
                                'path': 'GitPython',
                                'tags': ['a', 'b', 'c'],
                                'url': 'https://github.com/gitpython-developers/GitPython.git'},
                            'gameta': {
                                '__metarepo__': True,
                                'path': '.',
                                'tags': ['metarepo'],
                                'test_param': 'test',
                                'url': 'git@github.com:genius-systems/gameta.git'},
                            'gitdb': {
                                '__metarepo__': False,
                                'path': 'core/gitdb',
                                'tags': ['a', 'c', 'd'],
                                'url': 'https://github.com/gitpython-developers/gitdb.git'}
                        }
                    }
                )

    def test_schema_update_invalid_version_string(self):
        test_params = {
            'curr_version': '0.2.5',
            'desired_version': '0.3.a'
        }
        with self.runner.isolated_filesystem() as f:
            copyfile(join(dirname(__file__), 'data', '.gameta_v025'), join(f, '.gameta'))
            result = self.runner.invoke(self.update, ["-s", test_params['desired_version']])
            self.assertEqual(result.exit_code, 1)
            self.assertEqual(
                result.output,
                f"Error: Invalid version string {test_params['desired_version']} provided\n"
            )

    def test_schema_update_version_does_not_exist(self):
        test_params = {
            'curr_version': '0.2.5',
            'desired_version': '0.2.6'
        }
        with self.runner.isolated_filesystem() as f:
            copyfile(join(dirname(__file__), 'data', '.gameta_v025'), join(f, '.gameta'))
            result = self.runner.invoke(self.update, ["-s", test_params['desired_version']])
            self.assertEqual(result.exit_code, 1)
            self.assertEqual(
                result.output,
                f"Error: Desired version {test_params['desired_version']} does not exist\n"
            )

    def test_schema_update_attempting_to_downgrade(self):
        test_params = {
            'curr_version': '0.3.0',
            'desired_version': '0.2.5'
        }
        with self.runner.isolated_filesystem() as f:
            copyfile(join(dirname(__file__), 'data', '.gameta_full'), join(f, '.gameta'))
            result = self.runner.invoke(self.update, ["-s", test_params['desired_version']])
            self.assertEqual(result.exit_code, 1)
            self.assertEqual(
                result.output,
                f"Error: Desired version {test_params['desired_version']} "
                f"is smaller than current version {test_params['curr_version']}, downgrading is not supported\n"
            )

    def test_schema_update_gameta_file_does_not_exist(self):
        test_params = {
            'curr_version': '0.2.5',
            'desired_version': '0.3.0'
        }
        with self.runner.isolated_filesystem() as f:
            result = self.runner.invoke(self.update, ["-s", test_params['desired_version']])
            self.assertEqual(result.exit_code, 1)
            self.assertEqual(
                result.output,
                f"Error: Could not load .gameta data from path {join(f, '.gameta')} provided due to "
                f"FileNotFoundError.[Errno 2] No such file or directory: '{join(f, '.gameta')}'\n"
            )

    def test_schema_update_gameta_data_invalid(self):
        test_params = {
            'curr_version': '0.2.5',
            'desired_version': '0.3.0'
        }
        with self.runner.isolated_filesystem() as f:
            with open(join(dirname(__file__), 'data', '.gameta_v025'), 'r') as m1:
                output = json.load(m1)
                with open(join(f, '.gameta'), 'w') as m2:
                    del output['repositories']['gameta']['url']
                    json.dump(output, m2)
            result = self.runner.invoke(self.update, ["-s", test_params['desired_version']])
            self.assertEqual(result.exit_code, 1)
            self.assertEqual(
                result.output,
                f"Error: .gameta data is invalid, run `gameta schema validate` to debug this before updating\n"
            )

    def test_schema_update_unsupported_schema_version(self):
        test_params = {
            'curr_version': '0.1.0',
            'desired_version': '0.3.0'
        }
        with self.runner.isolated_filesystem() as f:
            with open(join(dirname(__file__), 'data', '.gameta_v025'), 'r') as m1:
                output = json.load(m1)
                with open(join(f, '.gameta'), 'w') as m2:
                    output['version'] = test_params['curr_version']
                    json.dump(output, m2)
            result = self.runner.invoke(self.update, ["-s", test_params['desired_version']])
            self.assertEqual(result.exit_code, 1)
            self.assertEqual(
                result.output,
                f"Error: Current version of .gameta file ({test_params['curr_version']}) "
                f"is not supported by gameta version {__version__}\n"
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
                f"Supported schema versions: 0.2.5, 0.3.0\n"
            )

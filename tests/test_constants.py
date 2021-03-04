import json
from os.path import join, dirname
from shutil import copyfile
from unittest import TestCase
from unittest.mock import patch

from click.testing import CliRunner

from gameta.context import GametaContext
from gameta.constants import add, delete


class TestConstantsAdd(TestCase):
    def setUp(self) -> None:
        self.maxDiff = None
        self.runner = CliRunner()
        self.add = add

    @patch('gameta.cli.click.Context.ensure_object')
    def test_constants_add_parameters_missing_key_parameters(self, mock_ensure_object):
        with self.runner.isolated_filesystem() as f:
            copyfile(join(dirname(__file__), 'data', '.meta_other_repos'), join(f, '.meta'))
            context = GametaContext()
            context.project_dir = f
            context.load()
            mock_ensure_object.return_value = context
            result = self.runner.invoke(self.add)
            self.assertEqual(result.exit_code, 2)
            self.assertEqual(
                result.output,
                "Usage: add [OPTIONS]\n"
                "Try 'add --help' for help.\n"
                "\n"
                "Error: Missing option '--name' / '-n'.\n"
            )

    @patch('gameta.cli.click.Context.ensure_object')
    def test_constants_add_valid_constant(self, mock_ensure_object):
        params = {
            'name': 'test',
            'type': 'int',
            'value': 1
        }
        with self.runner.isolated_filesystem() as f:
            copyfile(join(dirname(__file__), 'data', '.meta_other_repos'), join(f, '.meta'))
            context = GametaContext()
            context.project_dir = f
            context.load()
            mock_ensure_object.return_value = context
            result = self.runner.invoke(self.add, ['-n', params['name'], '-t', params['type'], '-v', params['value']])
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                f"Adding constant {params['name']}\n"
                f"Successfully added constant {params['name'].upper()}: {params['value']} (type: {params['type']}) "
                f"to .meta file\n"
            )
            with open(join(f, '.meta'), 'r') as m:
                self.assertEqual(
                    json.load(m),
                    {
                        'projects': {
                            'GitPython': {
                                'path': 'GitPython',
                                'tags': ['a', 'b', 'c'],
                                'url': 'https://github.com/gitpython-developers/GitPython.git',
                                '__metarepo__': False
                            },
                            'gameta': {
                                'path': '.',
                                'tags': ['metarepo'],
                                'url': 'git@github.com:genius-systems/gameta.git',
                                '__metarepo__': True
                            },
                            'gitdb': {
                                'path': 'core/gitdb',
                                'tags': ['a', 'c', 'd'],
                                'url': 'https://github.com/gitpython-developers/gitdb.git',
                                '__metarepo__': False
                            }
                        },
                        "constants": {
                            "TEST": 1
                        }
                    }
                )

    @patch('gameta.cli.click.Context.ensure_object')
    def test_constants_add_constant_with_invalid_type_bool(self, mock_ensure_object):
        params = {
            'name': 'test',
            'type': 'bool',
            'value': 'hello_world'
        }
        with self.runner.isolated_filesystem() as f:
            copyfile(join(dirname(__file__), 'data', '.meta_other_repos'), join(f, '.meta'))
            context = GametaContext()
            context.project_dir = f
            context.load()
            mock_ensure_object.return_value = context
            result = self.runner.invoke(self.add, ['-n', params['name'], '-t', params['type'], '-v', params['value']])
            self.assertEqual(result.exit_code, 1)
            self.assertEqual(
                result.output,
                f"Adding constant {params['name']}\n"
                f"Error: BadParameter.{params['value']} is not a valid boolean\n"
            )
            with open(join(f, '.meta'), 'r') as m:
                self.assertEqual(
                    json.load(m),
                    {
                        'projects': {
                            'GitPython': {
                                'path': 'GitPython',
                                'tags': ['a', 'b', 'c'],
                                'url': 'https://github.com/gitpython-developers/GitPython.git',
                                '__metarepo__': False
                            },
                            'gameta': {
                                'path': '.',
                                'tags': ['metarepo'],
                                'url': 'git@github.com:genius-systems/gameta.git',
                                '__metarepo__': True
                            },
                            'gitdb': {
                                'path': 'core/gitdb',
                                'tags': ['a', 'c', 'd'],
                                'url': 'https://github.com/gitpython-developers/gitdb.git',
                                '__metarepo__': False
                            }
                        }
                    }
                )

    @patch('gameta.cli.click.Context.ensure_object')
    def test_constants_add_boolean_stored_as_string(self, mock_ensure_object):
        params = {
            'name': 'test',
            'type': 'str',
            'value': 'True'
        }
        with self.runner.isolated_filesystem() as f:
            copyfile(join(dirname(__file__), 'data', '.meta_other_repos'), join(f, '.meta'))
            context = GametaContext()
            context.project_dir = f
            context.load()
            mock_ensure_object.return_value = context
            result = self.runner.invoke(self.add, ['-n', params['name'], '-t', params['type'], '-v', params['value']])
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                f"Adding constant {params['name']}\n"
                f"Successfully added constant {params['name'].upper()}: {params['value']} (type: {params['type']}) "
                f"to .meta file\n"
            )
            with open(join(f, '.meta'), 'r') as m:
                self.assertEqual(
                    json.load(m),
                    {
                        'projects': {
                            'GitPython': {
                                'path': 'GitPython',
                                'tags': ['a', 'b', 'c'],
                                'url': 'https://github.com/gitpython-developers/GitPython.git',
                                '__metarepo__': False
                            },
                            'gameta': {
                                'path': '.',
                                'tags': ['metarepo'],
                                'url': 'git@github.com:genius-systems/gameta.git',
                                '__metarepo__': True
                            },
                            'gitdb': {
                                'path': 'core/gitdb',
                                'tags': ['a', 'c', 'd'],
                                'url': 'https://github.com/gitpython-developers/gitdb.git',
                                '__metarepo__': False
                            }
                        },
                        "constants": {
                            "TEST": 'True'
                        }
                    }
                )


class TestConstantsDelete(TestCase):
    def setUp(self) -> None:
        self.maxDiff = None
        self.runner = CliRunner()
        self.delete = delete

    @patch('gameta.cli.click.Context.ensure_object')
    def test_constants_delete_parameters_missing_key_parameters(self, mock_ensure_object):
        with self.runner.isolated_filesystem() as f:
            copyfile(join(dirname(__file__), 'data', '.meta_other_repos'), join(f, '.meta'))
            context = GametaContext()
            context.project_dir = f
            context.load()
            mock_ensure_object.return_value = context
            result = self.runner.invoke(self.delete)
            self.assertEqual(result.exit_code, 2)
            self.assertEqual(
                result.output,
                "Usage: delete [OPTIONS]\n"
                "Try 'delete --help' for help.\n"
                "\n"
                "Error: Missing option '--name' / '-n'.\n"
            )

    @patch('gameta.cli.click.Context.ensure_object')
    def test_constants_delete_an_existing_constant_in_lowercase(self, mock_ensure_object):
        params = {
            'name': 'test'
        }
        with self.runner.isolated_filesystem() as f:
            with open(join(dirname(__file__), 'data', '.meta_other_repos'), 'r') as m1:
                output = json.load(m1)
                with open(join(f, '.meta'), 'w+') as m2:
                    output.update({'constants': {'TEST': "hello_world"}})
                    json.dump(output, m2)
            context = GametaContext()
            context.project_dir = f
            context.load()
            mock_ensure_object.return_value = context
            result = self.runner.invoke(self.delete, ['-n', params['name']])
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                f"Deleting constant {params['name']}\n"
                f"Successfully deleted constant {params['name']} from .meta file\n"
            )
            with open(join(f, '.meta'), 'r') as m:
                self.assertEqual(
                    json.load(m),
                    {
                        'projects': {
                            'GitPython': {
                                'path': 'GitPython',
                                'tags': ['a', 'b', 'c'],
                                'url': 'https://github.com/gitpython-developers/GitPython.git',
                                '__metarepo__': False
                            },
                            'gameta': {
                                'path': '.',
                                'tags': ['metarepo'],
                                'url': 'git@github.com:genius-systems/gameta.git',
                                '__metarepo__': True
                            },
                            'gitdb': {
                                'path': 'core/gitdb',
                                'tags': ['a', 'c', 'd'],
                                'url': 'https://github.com/gitpython-developers/gitdb.git',
                                '__metarepo__': False
                            }
                        },
                        "constants": {}
                    }
                )

    @patch('gameta.cli.click.Context.ensure_object')
    def test_constants_delete_an_existing_constant_in_uppercase(self, mock_ensure_object):
        params = {
            'name': 'TEST'
        }
        with self.runner.isolated_filesystem() as f:
            with open(join(dirname(__file__), 'data', '.meta_other_repos'), 'r') as m1:
                output = json.load(m1)
                with open(join(f, '.meta'), 'w+') as m2:
                    output.update({'constants': {'TEST': "hello_world"}})
                    json.dump(output, m2)
            context = GametaContext()
            context.project_dir = f
            context.load()
            mock_ensure_object.return_value = context
            result = self.runner.invoke(self.delete, ['-n', params['name']])
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                f"Deleting constant {params['name']}\n"
                f"Successfully deleted constant {params['name']} from .meta file\n"
            )
            with open(join(f, '.meta'), 'r') as m:
                self.assertEqual(
                    json.load(m),
                    {
                        'projects': {
                            'GitPython': {
                                'path': 'GitPython',
                                'tags': ['a', 'b', 'c'],
                                'url': 'https://github.com/gitpython-developers/GitPython.git',
                                '__metarepo__': False
                            },
                            'gameta': {
                                'path': '.',
                                'tags': ['metarepo'],
                                'url': 'git@github.com:genius-systems/gameta.git',
                                '__metarepo__': True
                            },
                            'gitdb': {
                                'path': 'core/gitdb',
                                'tags': ['a', 'c', 'd'],
                                'url': 'https://github.com/gitpython-developers/gitdb.git',
                                '__metarepo__': False
                            }
                        },
                        "constants": {}
                    }
                )

    @patch('gameta.cli.click.Context.ensure_object')
    def test_constants_delete_an_non_existent_constant(self, mock_ensure_object):
        params = {
            'name': 'hello'
        }
        with self.runner.isolated_filesystem() as f:
            with open(join(dirname(__file__), 'data', '.meta_other_repos'), 'r') as m1:
                output = json.load(m1)
                with open(join(f, '.meta'), 'w+') as m2:
                    output.update({'constants': {'TEST': "hello_world"}})
                    json.dump(output, m2)
            context = GametaContext()
            context.project_dir = f
            context.load()
            mock_ensure_object.return_value = context
            result = self.runner.invoke(self.delete, ['-n', params['name']])
            self.assertEqual(result.exit_code, 1)
            self.assertEqual(
                result.output,
                f"Deleting constant {params['name']}\n"
                f"Error: Constant {params['name']} does not exist in .meta file\n"
            )
            with open(join(f, '.meta'), 'r') as m:
                self.assertEqual(
                    json.load(m),
                    {
                        'projects': {
                            'GitPython': {
                                'path': 'GitPython',
                                'tags': ['a', 'b', 'c'],
                                'url': 'https://github.com/gitpython-developers/GitPython.git',
                                '__metarepo__': False
                            },
                            'gameta': {
                                'path': '.',
                                'tags': ['metarepo'],
                                'url': 'git@github.com:genius-systems/gameta.git',
                                '__metarepo__': True
                            },
                            'gitdb': {
                                'path': 'core/gitdb',
                                'tags': ['a', 'c', 'd'],
                                'url': 'https://github.com/gitpython-developers/gitdb.git',
                                '__metarepo__': False
                            }
                        },
                        "constants": {
                            "TEST": "hello_world"
                        }
                    }
                )

    @patch('gameta.cli.click.Context.ensure_object')
    def test_constants_delete_constant_from_empty_meta_file(self, mock_ensure_object):
        params = {
            'name': 'hello'
        }
        with self.runner.isolated_filesystem() as f:
            with open(join(f, '.meta'), 'w+') as m:
                json.dump({}, m)
            context = GametaContext()
            context.project_dir = f
            context.load()
            mock_ensure_object.return_value = context
            result = self.runner.invoke(self.delete, ['-n', params['name']])
            self.assertEqual(result.exit_code, 1)
            self.assertEqual(
                result.output,
                f"Deleting constant {params['name']}\n"
                f"Error: Constant {params['name']} does not exist in .meta file\n"
            )
            with open(join(f, '.meta'), 'r') as m:
                self.assertEqual(json.load(m), {})

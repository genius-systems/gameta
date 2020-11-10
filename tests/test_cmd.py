import json
import zipfile
from os.path import join, dirname, exists
from shutil import copyfile, copytree
from unittest import TestCase
from unittest.mock import patch

from click import Context
from click.testing import CliRunner

from gameta.context import GametaContext
from gameta.cmd import add, delete, update, ls, exec


class TestCommandAdd(TestCase):
    def setUp(self) -> None:
        self.runner = CliRunner()
        self.add = add

    @patch('gameta.cli.click.Context.ensure_object')
    def test_command_add_key_parameters_not_provided(self, mock_ensure_object):
        with self.runner.isolated_filesystem() as f:
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'git.zip'), 'r') as template:
                template.extractall(f)
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
    def test_command_add_no_meta_file(self, mock_ensure_object):
        params = {
            'name': 'hello_world',
            'commands': ['git fetch --all --tags --prune', 'git pull'],
        }
        with self.runner.isolated_filesystem() as f:
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'git.zip'), 'r') as template:
                template.extractall(f)
            context = GametaContext()
            context.project_dir = f
            context.load()
            mock_ensure_object.return_value = context
            result = self.runner.invoke(
                self.add, ['-n', params['name'], '-c', params['commands'][0], '-c', params['commands'][1]]
            )
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                f"Adding command {params['name']} with parameters ({{'commands': {params['commands']}, "
                f"'tags': [], 'repositories': [], 'verbose': False, 'shell': True, 'raise_errors': False}}) "
                f"to the command store\n"
                f"Successfully added command {params['name']} to the command store\n"
            )
            self.assertTrue(exists(join(f, '.meta')))
            with open(join(f, '.meta'), 'r') as m:
                self.assertEqual(
                    json.load(m),
                    {
                        'projects': {},
                        'commands': {
                            params['name']: {
                                'commands': params['commands'],
                                'raise_errors': False,
                                'repositories': [],
                                'shell': True,
                                'tags': [],
                                'verbose': False
                            }
                        }
                    }
                )

    @patch('gameta.cli.click.Context.ensure_object')
    def test_command_add_full_data(self, mock_ensure_object):
        params = {
            'name': 'hello_world',
            'commands': ['git fetch --all --tags --prune', 'git pull'],
            'tags': ['a', 'b'],
            'repositories': ['gameta'],
            'verbose': True,
            'shell': True,
            'raise_errors': True
        }
        with self.runner.isolated_filesystem() as f:
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'git.zip'), 'r') as template:
                template.extractall(f)
            copyfile(join(dirname(__file__), 'data', '.meta_other_repos'), join(f, '.meta'))
            context = GametaContext()
            context.project_dir = f
            context.load()
            mock_ensure_object.return_value = context
            result = self.runner.invoke(
                self.add,
                [
                    '-n', params['name'],
                    '-c', params['commands'][0],
                    '-c', params['commands'][1],
                    '-t', params['tags'][0],
                    '-t', params['tags'][1],
                    '-r', params['repositories'][0],
                    '-v', '-s', '-e'
                ]
            )
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                f"Adding command {params['name']} with parameters ({{'commands': {params['commands']}, "
                f"'tags': {params['tags']}, 'repositories': {params['repositories']}, 'verbose': {params['verbose']}, "
                f"'shell': {params['shell']}, 'raise_errors': {params['raise_errors']}}}) "
                f"to the command store\n"
                f"Successfully added command {params['name']} to the command store\n"
            )
            self.assertTrue(exists(join(f, '.meta')))
            with open(join(f, '.meta'), 'r') as m:
                self.assertEqual(
                    json.load(m),
                    {
                        'projects': {
                            'GitPython': {
                                '__metarepo__': False,
                                'path': 'GitPython',
                                'tags': ['a', 'b', 'c'],
                                'url': 'https://github.com/gitpython-developers/GitPython.git'
                            },
                            'gameta': {
                                '__metarepo__': True,
                                'path': '.',
                                'tags': ['metarepo'],
                                'url': 'git@github.com:genius-systems/gameta.git'
                            },
                            'gitdb': {
                                '__metarepo__': False,
                                'path': 'core/gitdb',
                                'tags': ['a', 'c', 'd'],
                                'url': 'https://github.com/gitpython-developers/gitdb.git'
                            }
                        },
                        'commands': {
                            params['name']: {
                                'commands': params['commands'],
                                'raise_errors': params['raise_errors'],
                                'repositories': params['repositories'],
                                'shell': params['shell'],
                                'tags': params['tags'],
                                'verbose': params['verbose']
                            }
                        }
                    }
                )

    @patch('gameta.cli.click.Context.ensure_object')
    def test_command_add_nonexistent_tag(self, mock_ensure_object):
        params = {
            'name': 'hello_world',
            'commands': ['git fetch --all --tags --prune', 'git pull'],
            'tags': ['hello'],
            'repositories': [],
            'verbose': True,
            'shell': True,
            'raise_errors': True
        }
        with self.runner.isolated_filesystem() as f:
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'git.zip'), 'r') as template:
                template.extractall(f)
            copyfile(join(dirname(__file__), 'data', '.meta_other_repos'), join(f, '.meta'))
            context = GametaContext()
            context.project_dir = f
            context.load()
            mock_ensure_object.return_value = context
            result = self.runner.invoke(
                self.add,
                [
                    '-n', params['name'],
                    '-c', params['commands'][0],
                    '-c', params['commands'][1],
                    '-t', params['tags'][0],
                    '-v', '-s', '-e'
                ]
            )
            self.assertEqual(result.exit_code, 1)
            self.assertEqual(
                result.output,
                f"Error: One of the tags in {params['tags']} has not been added, please run "
                f"`gameta tags add` to add it first\n"
            )
            self.assertTrue(exists(join(f, '.meta')))
            with open(join(f, '.meta'), 'r') as m:
                self.assertEqual(
                    json.load(m),
                    {
                        'projects': {
                            'GitPython': {
                                '__metarepo__': False,
                                'path': 'GitPython',
                                'tags': ['a', 'b', 'c'],
                                'url': 'https://github.com/gitpython-developers/GitPython.git'
                            },
                            'gameta': {
                                '__metarepo__': True,
                                'path': '.',
                                'tags': ['metarepo'],
                                'url': 'git@github.com:genius-systems/gameta.git'
                            },
                            'gitdb': {
                                '__metarepo__': False,
                                'path': 'core/gitdb',
                                'tags': ['a', 'c', 'd'],
                                'url': 'https://github.com/gitpython-developers/gitdb.git'
                            }
                        }
                    }
                )

    @patch('gameta.cli.click.Context.ensure_object')
    def test_command_add_nonexistent_repository(self, mock_ensure_object):
        params = {
            'name': 'hello_world',
            'commands': ['git fetch --all --tags --prune', 'git pull'],
            'tags': [],
            'repositories': ['GitPython', 'gitdb'],
            'verbose': True,
            'shell': True,
            'raise_errors': True
        }
        with self.runner.isolated_filesystem() as f:
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'git.zip'), 'r') as template:
                template.extractall(f)
            copyfile(join(dirname(__file__), 'data', '.meta'), join(f, '.meta'))
            context = GametaContext()
            context.project_dir = f
            context.load()
            mock_ensure_object.return_value = context
            result = self.runner.invoke(
                self.add,
                [
                    '-n', params['name'],
                    '-c', params['commands'][0],
                    '-c', params['commands'][1],
                    '-r', params['repositories'][0],
                    '-r', params['repositories'][1],
                    '-v', '-s', '-e'
                ]
            )
            self.assertEqual(result.exit_code, 1)
            self.assertEqual(
                result.output,
                f"Error: One of the repositories in {params['repositories']} does not exist, please "
                f"run `gameta repo add` to add it first\n"
            )
            self.assertTrue(exists(join(f, '.meta')))
            with open(join(f, '.meta'), 'r') as m:
                self.assertEqual(
                    json.load(m),
                    {
                        'projects': {
                            'gameta': {
                                '__metarepo__': True,
                                'path': '.',
                                'tags': ['metarepo'],
                                'url': 'git@github.com:genius-systems/gameta.git'
                            }
                        }
                    }
                )

    @patch('gameta.cli.click.Context.ensure_object')
    def test_command_add_command_overwritten(self, mock_ensure_object):
        params = {
            'name': 'hello_world',
            'commands': ['git fetch --all --tags --prune', 'git pull'],
            'tags': ['a', 'b'],
            'repositories': ['gameta'],
            'verbose': True,
            'shell': True,
            'raise_errors': True
        }
        with self.runner.isolated_filesystem() as f:
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'git.zip'), 'r') as template:
                template.extractall(f)
            with open(join(dirname(__file__), 'data', '.meta_other_repos'), 'r') as m1:
                output = json.load(m1)
                with open(join(f, '.meta'), 'w') as m2:
                    output.update(
                        {
                            'commands': {
                                'hello_world': {
                                    'commands': params['commands'],
                                    'raise_errors': False,
                                    'repositories': [],
                                    'shell': True,
                                    'tags': [],
                                    'verbose': False
                                }
                            }
                        }
                    )
                    json.dump(output, m2)
            context = GametaContext()
            context.project_dir = f
            context.load()
            mock_ensure_object.return_value = context
            result = self.runner.invoke(
                self.add,
                [
                    '-n', params['name'],
                    '-c', params['commands'][0],
                    '-c', params['commands'][1],
                    '-t', params['tags'][0],
                    '-t', params['tags'][1],
                    '-r', params['repositories'][0],
                    '-v', '-s', '-e', '-o'
                ]
            )
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                f"Adding command {params['name']} with parameters ({{'commands': {params['commands']}, "
                f"'tags': {params['tags']}, 'repositories': {params['repositories']}, 'verbose': {params['verbose']}, "
                f"'shell': {params['shell']}, 'raise_errors': {params['raise_errors']}}}) "
                f"to the command store\n"
                f"Overwriting command {params['name']} in the command store\n"
                f"Successfully added command {params['name']} to the command store\n"
            )
            self.assertTrue(exists(join(f, '.meta')))
            with open(join(f, '.meta'), 'r') as m:
                self.assertEqual(
                    json.load(m),
                    {
                        'projects': {
                            'GitPython': {
                                '__metarepo__': False,
                                'path': 'GitPython',
                                'tags': ['a', 'b', 'c'],
                                'url': 'https://github.com/gitpython-developers/GitPython.git'
                            },
                            'gameta': {
                                '__metarepo__': True,
                                'path': '.',
                                'tags': ['metarepo'],
                                'url': 'git@github.com:genius-systems/gameta.git'
                            },
                            'gitdb': {
                                '__metarepo__': False,
                                'path': 'core/gitdb',
                                'tags': ['a', 'c', 'd'],
                                'url': 'https://github.com/gitpython-developers/gitdb.git'
                            }
                        },
                        'commands': {
                            params['name']: {
                                'commands': params['commands'],
                                'raise_errors': params['raise_errors'],
                                'repositories': params['repositories'],
                                'shell': params['shell'],
                                'tags': params['tags'],
                                'verbose': params['verbose']
                            }
                        }
                    }
                )


class TestCommandDelete(TestCase):
    def setUp(self) -> None:
        self.runner = CliRunner()
        self.delete = delete

    @patch('gameta.cli.click.Context.ensure_object')
    def test_command_delete_key_parameters_not_provided(self, mock_ensure_object):
        with self.runner.isolated_filesystem() as f:
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'git.zip'), 'r') as template:
                template.extractall(f)
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
    def test_command_delete_no_meta_file(self, mock_ensure_object):
        params = {
            'name': 'hello_world'
        }
        with self.runner.isolated_filesystem() as f:
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'git.zip'), 'r') as template:
                template.extractall(f)
            context = GametaContext()
            context.project_dir = f
            context.load()
            mock_ensure_object.return_value = context
            result = self.runner.invoke(self.delete, ['-n', params['name']])
            self.assertEqual(result.exit_code, 1)
            self.assertEqual(
                result.output,
                f"Deleting command {params['name']} from the command store\n"
                f"Error: Command {params['name']} does not exist in the command store\n"
            )
            self.assertFalse(exists(join(f, '.meta')))

    @patch('gameta.cli.click.Context.ensure_object')
    def test_command_delete_nonexistent_command(self, mock_ensure_object):
        params = {
            'name': 'hello_world'
        }
        with self.runner.isolated_filesystem() as f:
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'git.zip'), 'r') as template:
                template.extractall(f)
            copyfile(join(dirname(__file__), 'data', '.meta'), join(f, '.meta'))
            context = GametaContext()
            context.project_dir = f
            context.load()
            mock_ensure_object.return_value = context
            result = self.runner.invoke(self.delete, ['-n', params['name']])
            self.assertEqual(result.exit_code, 1)
            self.assertEqual(
                result.output,
                f"Deleting command {params['name']} from the command store\n"
                f"Error: Command {params['name']} does not exist in the command store\n"
            )
            self.assertTrue(exists(join(f, '.meta')))
            with open(join(f, '.meta'), 'r') as m:
                self.assertEqual(
                    json.load(m),
                    {
                        'projects': {
                            'gameta': {
                                '__metarepo__': True,
                                'path': '.',
                                'tags': ['metarepo'],
                                'url': 'git@github.com:genius-systems/gameta.git'
                            }
                        }
                    }
                )

    @patch('gameta.cli.click.Context.ensure_object')
    def test_command_delete_command_deleted(self, mock_ensure_object):
        params = {
            'name': 'hello_world',
            'commands': ['git fetch --all --tags --prune', 'git pull']
        }
        with self.runner.isolated_filesystem() as f:
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'git.zip'), 'r') as template:
                template.extractall(f)
            with open(join(dirname(__file__), 'data', '.meta'), 'r') as m1:
                output = json.load(m1)
                with open(join(f, '.meta'), 'w') as m2:
                    output.update(
                        {
                            'commands': {
                                'hello_world': {
                                    'commands': params['commands'],
                                    'raise_errors': False,
                                    'repositories': [],
                                    'shell': True,
                                    'tags': [],
                                    'verbose': False
                                }
                            }
                        }
                    )
                    json.dump(output, m2)
            context = GametaContext()
            context.project_dir = f
            context.load()
            mock_ensure_object.return_value = context
            result = self.runner.invoke(self.delete, ['-n', params['name']])
            print(result.output)
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                f"Deleting command {params['name']} from the command store\n"
                f"Successfully deleted command {params['name']} from the command store\n"
            )
            self.assertTrue(exists(join(f, '.meta')))
            with open(join(f, '.meta'), 'r') as m:
                self.assertEqual(
                    json.load(m),
                    {
                        'projects': {
                            'gameta': {
                                '__metarepo__': True,
                                'path': '.',
                                'tags': ['metarepo'],
                                'url': 'git@github.com:genius-systems/gameta.git'
                            }
                        },
                        "commands": {}
                    }
                )


class TestCommandUpdate(TestCase):
    def setUp(self) -> None:
        self.runner = CliRunner()
        self.update = update

    @patch('gameta.cli.click.Context.ensure_object')
    def test_command_update_key_parameters_not_provided(self, mock_ensure_object):
        with self.runner.isolated_filesystem() as f:
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'git.zip'), 'r') as template:
                template.extractall(f)
            copyfile(join(dirname(__file__), 'data', '.meta_other_repos'), join(f, '.meta'))
            context = GametaContext()
            context.project_dir = f
            context.load()
            mock_ensure_object.return_value = context
            result = self.runner.invoke(self.update)
            self.assertEqual(result.exit_code, 2)
            self.assertEqual(
                result.output,
                "Usage: update [OPTIONS]\n"
                "Try 'update --help' for help.\n"
                "\n"
                "Error: Missing option '--name' / '-n'.\n"
            )

    @patch('gameta.cli.click.Context.ensure_object')
    def test_command_update_no_meta_file(self, mock_ensure_object):
        params = {
            'name': 'hello_world',
            'tags': ['a', 'b'],
            'repositories': ['gameta'],
            'verbose': True,
            'shell': True,
            'raise_errors': True
        }
        with self.runner.isolated_filesystem() as f:
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'git.zip'), 'r') as template:
                template.extractall(f)
            context = GametaContext()
            context.project_dir = f
            context.load()
            mock_ensure_object.return_value = context
            result = self.runner.invoke(self.update, ['-n', params['name']])
            self.assertEqual(result.exit_code, 1)
            self.assertEqual(
                result.output,
                f"Updating command {params['name']} in the command store\n"
                f"Error: Command {params['name']} does not exist in the command store\n"
            )
            self.assertFalse(exists(join(f, '.meta')))

    @patch('gameta.cli.click.Context.ensure_object')
    def test_command_update_nonexistent_command(self, mock_ensure_object):
        params = {
            'name': 'hello_world',
            'tags': ['a', 'b'],
            'repositories': ['gameta'],
            'verbose': True,
            'shell': True,
            'raise_errors': True
        }
        with self.runner.isolated_filesystem() as f:
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'git.zip'), 'r') as template:
                template.extractall(f)
            copyfile(join(dirname(__file__), 'data', '.meta'), join(f, '.meta'))
            context = GametaContext()
            context.project_dir = f
            context.load()
            mock_ensure_object.return_value = context
            result = self.runner.invoke(self.update, ['-n', params['name']])
            self.assertEqual(result.exit_code, 1)
            self.assertEqual(
                result.output,
                f"Updating command {params['name']} in the command store\n"
                f"Error: Command {params['name']} does not exist in the command store\n"
            )
            self.assertTrue(exists(join(f, '.meta')))
            with open(join(f, '.meta'), 'r') as m:
                self.assertEqual(
                    json.load(m),
                    {
                        'projects': {
                            'gameta': {
                                '__metarepo__': True,
                                'path': '.',
                                'tags': ['metarepo'],
                                'url': 'git@github.com:genius-systems/gameta.git'
                            }
                        }
                    }
                )

    @patch('gameta.cli.click.Context.ensure_object')
    def test_command_update_full_update(self, mock_ensure_object):
        params = {
            'name': 'hello_world',
            'commands': ['git fetch --all --tags --prune', 'git pull'],
            'tags': ['a', 'b'],
            'repositories': ['gameta'],
            'verbose': True,
            'shell': True,
            'raise_errors': True
        }
        with self.runner.isolated_filesystem() as f:
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'git.zip'), 'r') as template:
                template.extractall(f)
            with open(join(dirname(__file__), 'data', '.meta_other_repos'), 'r') as m1:
                output = json.load(m1)
                with open(join(f, '.meta'), 'w') as m2:
                    output.update(
                        {
                            'commands': {
                                'hello_world': {
                                    'commands': params['commands'],
                                    'raise_errors': False,
                                    'repositories': [],
                                    'shell': True,
                                    'tags': [],
                                    'verbose': False
                                }
                            }
                        }
                    )
                    json.dump(output, m2)
            context = GametaContext()
            context.project_dir = f
            context.load()
            mock_ensure_object.return_value = context
            result = self.runner.invoke(
                self.update,
                [
                    '-n', params['name'],
                    '-t', params['tags'][0],
                    '-t', params['tags'][1],
                    '-r', params['repositories'][0],
                    '-v', '-s', '-e',
                ]
            )
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                f"Updating command {params['name']} in the command store\n"
                f"Successfully updated command {params['name']} in the command store\n"
            )
            self.assertTrue(exists(join(f, '.meta')))
            with open(join(f, '.meta'), 'r') as m:
                self.assertEqual(
                    json.load(m),
                    {
                        'projects': {
                            'GitPython': {
                                '__metarepo__': False,
                                'path': 'GitPython',
                                'tags': ['a', 'b', 'c'],
                                'url': 'https://github.com/gitpython-developers/GitPython.git'
                            },
                            'gameta': {
                                '__metarepo__': True,
                                'path': '.',
                                'tags': ['metarepo'],
                                'url': 'git@github.com:genius-systems/gameta.git'
                            },
                            'gitdb': {
                                '__metarepo__': False,
                                'path': 'core/gitdb',
                                'tags': ['a', 'c', 'd'],
                                'url': 'https://github.com/gitpython-developers/gitdb.git'
                            }
                        },
                        'commands': {
                            'hello_world': {
                                'commands': params['commands'],
                                'tags': params['tags'],
                                'repositories': params['repositories'],
                                'verbose': params['verbose'],
                                'shell': params['shell'],
                                'raise_errors': params['raise_errors']
                            }
                        }
                    }
                )

    @patch('gameta.cli.click.Context.ensure_object')
    def test_command_update_partial_update(self, mock_ensure_object):
        params = {
            'name': 'hello_world',
            'commands': ['git fetch --all --tags --prune', 'git pull'],
            'tags': ['a', 'b'],
            'repositories': [],
            'verbose': False,
            'shell': True,
            'raise_errors': False
        }
        with self.runner.isolated_filesystem() as f:
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'git.zip'), 'r') as template:
                template.extractall(f)
            with open(join(dirname(__file__), 'data', '.meta_other_repos'), 'r') as m1:
                output = json.load(m1)
                with open(join(f, '.meta'), 'w') as m2:
                    output.update(
                        {
                            'commands': {
                                'hello_world': {
                                    'commands': params['commands'],
                                    'raise_errors': params['raise_errors'],
                                    'repositories': params['repositories'],
                                    'shell': params['shell'],
                                    'tags': [],
                                    'verbose': params['verbose']
                                }
                            }
                        }
                    )
                    json.dump(output, m2)
            context = GametaContext()
            context.project_dir = f
            context.load()
            mock_ensure_object.return_value = context
            result = self.runner.invoke(
                self.update,
                [
                    '-n', params['name'],
                    '-t', params['tags'][0],
                    '-t', params['tags'][1]
                ]
            )
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                f"Updating command {params['name']} in the command store\n"
                f"Successfully updated command {params['name']} in the command store\n"
            )
            self.assertTrue(exists(join(f, '.meta')))
            with open(join(f, '.meta'), 'r') as m:
                self.assertEqual(
                    json.load(m),
                    {
                        'projects': {
                            'GitPython': {
                                '__metarepo__': False,
                                'path': 'GitPython',
                                'tags': ['a', 'b', 'c'],
                                'url': 'https://github.com/gitpython-developers/GitPython.git'
                            },
                            'gameta': {
                                '__metarepo__': True,
                                'path': '.',
                                'tags': ['metarepo'],
                                'url': 'git@github.com:genius-systems/gameta.git'
                            },
                            'gitdb': {
                                '__metarepo__': False,
                                'path': 'core/gitdb',
                                'tags': ['a', 'c', 'd'],
                                'url': 'https://github.com/gitpython-developers/gitdb.git'
                            }
                        },
                        'commands': {
                            'hello_world': {
                                'commands': params['commands'],
                                'tags': params['tags'],
                                'repositories': params['repositories'],
                                'verbose': params['verbose'],
                                'shell': params['shell'],
                                'raise_errors': params['raise_errors']
                            }
                        }
                    }
                )

    @patch('gameta.cli.click.Context.ensure_object')
    def test_command_update_invalid_tags(self, mock_ensure_object):
        params = {
            'name': 'hello_world',
            'commands': ['git fetch --all --tags --prune', 'git pull'],
            'tags': ['hello', 'b', 'a'],
            'repositories': [],
            'verbose': False,
            'shell': True,
            'raise_errors': False
        }
        with self.runner.isolated_filesystem() as f:
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'git.zip'), 'r') as template:
                template.extractall(f)
            with open(join(dirname(__file__), 'data', '.meta_other_repos'), 'r') as m1:
                output = json.load(m1)
                with open(join(f, '.meta'), 'w') as m2:
                    output.update(
                        {
                            'commands': {
                                'hello_world': {
                                    'commands': params['commands'],
                                    'raise_errors': params['raise_errors'],
                                    'repositories': params['repositories'],
                                    'shell': params['shell'],
                                    'tags': [],
                                    'verbose': params['verbose']
                                }
                            }
                        }
                    )
                    json.dump(output, m2)
            context = GametaContext()
            context.project_dir = f
            context.load()
            mock_ensure_object.return_value = context
            result = self.runner.invoke(
                self.update,
                [
                    '-n', params['name'],
                    '-t', params['tags'][0],
                    '-t', params['tags'][1],
                    '-t', params['tags'][2]
                ]
            )
            self.assertEqual(result.exit_code, 1)
            self.assertEqual(
                result.output,
                f"Updating command {params['name']} in the command store\n"
                f"Error: One of the tags in {params['tags']} has not been added, please run "
                f"`gameta tags add` to add it first\n"
            )
            self.assertTrue(exists(join(f, '.meta')))
            with open(join(f, '.meta'), 'r') as m:
                self.assertEqual(
                    json.load(m),
                    {
                        'projects': {
                            'GitPython': {
                                '__metarepo__': False,
                                'path': 'GitPython',
                                'tags': ['a', 'b', 'c'],
                                'url': 'https://github.com/gitpython-developers/GitPython.git'
                            },
                            'gameta': {
                                '__metarepo__': True,
                                'path': '.',
                                'tags': ['metarepo'],
                                'url': 'git@github.com:genius-systems/gameta.git'
                            },
                            'gitdb': {
                                '__metarepo__': False,
                                'path': 'core/gitdb',
                                'tags': ['a', 'c', 'd'],
                                'url': 'https://github.com/gitpython-developers/gitdb.git'
                            }
                        },
                        'commands': {
                            'hello_world': {
                                'commands': params['commands'],
                                'tags': [],
                                'repositories': params['repositories'],
                                'verbose': params['verbose'],
                                'shell': params['shell'],
                                'raise_errors': params['raise_errors']
                            }
                        }
                    }
                )

    @patch('gameta.cli.click.Context.ensure_object')
    def test_command_update_invalid_command_configuration(self, mock_ensure_object):
        params = {
            'name': 'hello_world',
            'commands': ['git fetch --all --tags --prune', 'git pull'],
            'tags': [],
            'repositories': ['gitdb', 'GitPython'],
            'verbose': False,
            'shell': False,
            'raise_errors': False
        }
        with self.runner.isolated_filesystem() as f:
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'git.zip'), 'r') as template:
                template.extractall(f)
            with open(join(dirname(__file__), 'data', '.meta'), 'r') as m1:
                output = json.load(m1)
                with open(join(f, '.meta'), 'w') as m2:
                    output.update(
                        {
                            'commands': {
                                'hello_world': {
                                    'commands': ['git fetch --all --tags --prune'],
                                    'raise_errors': params['raise_errors'],
                                    'repositories': [],
                                    'shell': False,
                                    'tags': params['tags'],
                                    'verbose': params['verbose']
                                }
                            }
                        }
                    )
                    json.dump(output, m2)
            context = GametaContext()
            context.project_dir = f
            context.load()
            mock_ensure_object.return_value = context
            result = self.runner.invoke(
                self.update,
                [
                    '-n', params['name'],
                    '-c', params['commands'][0],
                    '-c', params['commands'][1],
                ]
            )
            self.assertEqual(result.exit_code, 1)
            self.assertEqual(
                result.output,
                f"Updating command {params['name']} in the command store\n"
                f"Error: Multiple CLI commands requires shell param to be True\n"
            )
            self.assertTrue(exists(join(f, '.meta')))
            with open(join(f, '.meta'), 'r') as m:
                self.assertEqual(
                    json.load(m),
                    {
                        'projects': {
                            'gameta': {
                                '__metarepo__': True,
                                'path': '.',
                                'tags': ['metarepo'],
                                'url': 'git@github.com:genius-systems/gameta.git'
                            }
                        },
                        'commands': {
                            'hello_world': {
                                'commands': ['git fetch --all --tags --prune'],
                                'tags': [],
                                'repositories': [],
                                'verbose': params['verbose'],
                                'shell': params['shell'],
                                'raise_errors': params['raise_errors']
                            }
                        }
                    }
                )


class TestCommandLs(TestCase):
    def setUp(self) -> None:
        self.runner = CliRunner()
        self.ls = ls

    @patch('gameta.cli.click.Context.ensure_object')
    def test_command_ls_no_commands_in_command_store(self, mock_ensure_object):
        with self.runner.isolated_filesystem() as f:
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'git.zip'), 'r') as template:
                template.extractall(f)
            copyfile(join(dirname(__file__), 'data', '.meta'), join(f, '.meta'))
            context = GametaContext()
            context.project_dir = f
            context.load()
            mock_ensure_object.return_value = context
            result = self.runner.invoke(self.ls)
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(result.output, '')

    @patch('gameta.cli.click.Context.ensure_object')
    def test_command_ls_all_commands(self, mock_ensure_object):
        params = {
            'commands': {
                'hello_world': {
                    'commands': ['git fetch --all --tags --prune', 'git pull'],
                    'tags': [],
                    'repositories': ['gitdb', 'GitPython'],
                    'verbose': False,
                    'shell': False,
                    'raise_errors': False
                },
                'hello_world2': {
                    'commands': ['git fetch --all --tags --prune', 'git pull'],
                    'tags': [],
                    'repositories': ['gitdb', 'GitPython'],
                    'verbose': False,
                    'shell': False,
                    'raise_errors': False
                }
            }
        }
        with self.runner.isolated_filesystem() as f:
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'git.zip'), 'r') as template:
                template.extractall(f)
            with open(join(dirname(__file__), 'data', '.meta'), 'r') as m1:
                output = json.load(m1)
                with open(join(f, '.meta'), 'w') as m2:
                    output['commands'] = params['commands']
                    json.dump(output, m2)
            context = GametaContext()
            context.project_dir = f
            context.load()
            mock_ensure_object.return_value = context
            result = self.runner.invoke(self.ls)
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                "hello_world:\n"
                f"\tcommands: {' && '.join(params['commands']['hello_world']['commands'])}\n"
                f"\ttags: {', '.join(params['commands']['hello_world']['tags'])}\n"
                f"\trepositories: {', '.join(params['commands']['hello_world']['repositories'])}\n"
                f"\tverbose: {params['commands']['hello_world']['verbose']}\n"
                f"\tshell: {params['commands']['hello_world']['shell']}\n"
                f"\traise_errors: {params['commands']['hello_world']['raise_errors']}\n"
                '\n'
                "hello_world2:\n"
                f"\tcommands: {' && '.join(params['commands']['hello_world2']['commands'])}\n"
                f"\ttags: {', '.join(params['commands']['hello_world2']['tags'])}\n"
                f"\trepositories: {', '.join(params['commands']['hello_world2']['repositories'])}\n"
                f"\tverbose: {params['commands']['hello_world2']['verbose']}\n"
                f"\tshell: {params['commands']['hello_world2']['shell']}\n"
                f"\traise_errors: {params['commands']['hello_world2']['raise_errors']}\n"
                '\n'
            )


class TestCommandExec(TestCase):
    def setUp(self) -> None:
        self.runner = CliRunner()
        self.exec = exec

    @patch('gameta.cli.click.Context.ensure_object')
    def test_command_exec_key_parameters_not_provided(self, mock_ensure_object):
        with self.runner.isolated_filesystem() as f:
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'git.zip'), 'r') as template:
                template.extractall(f)
            copyfile(join(dirname(__file__), 'data', '.meta_other_repos'), join(f, '.meta'))
            context = GametaContext()
            context.project_dir = f
            context.load()
            mock_ensure_object.return_value = context
            result = self.runner.invoke(self.exec)
            self.assertEqual(result.exit_code, 2)
            self.assertEqual(
                result.output,
                "Usage: exec [OPTIONS]\n"
                "Try 'exec --help' for help.\n"
                "\n"
                "Error: Missing option '--command' / '-c'.\n"
            )

    @patch('gameta.cli.click.core.Context')
    def test_command_exec_nonexistent_command(self, mock_context):
        params = {
            'commands': ['hello_world', 'hello_world2']
        }
        with self.runner.isolated_filesystem() as f:
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'git.zip'), 'r') as template:
                template.extractall(f)
            copyfile(join(dirname(__file__), 'data', '.meta'), join(f, '.meta'))
            gameta_context = GametaContext()
            gameta_context.project_dir = f
            gameta_context.load()
            context = Context(exec, obj=gameta_context)
            mock_context.return_value = context
            result = self.runner.invoke(self.exec, ['-c', params['commands'][0], '-c', params['commands'][1]])
            self.assertEqual(result.exit_code, 1)
            self.assertEqual(
                result.output,
                f"Error: One of the commands in {list(params['commands'])} does not exist in the Gameta command store, "
                f"please run `gameta cmd add` to add it first\n"
            )
            self.assertTrue(exists(join(f, '.meta')))
            with open(join(f, '.meta'), 'r') as m:
                self.assertEqual(
                    json.load(m),
                    {
                        'projects': {
                            'gameta': {
                                '__metarepo__': True,
                                'path': '.',
                                'tags': ['metarepo'],
                                'url': 'git@github.com:genius-systems/gameta.git'
                            }
                        }
                    }
                )

    @patch('gameta.cli.click.core.Context')
    def test_command_exec_single_command(self, mock_context):
        params = {
            'commands': ['hello_world'],
            'hello_world': {
                'commands': ['git fetch --all --tags --prune'],
                'tags': ['a', 'b'],
                'repositories': ['gameta'],
                'verbose': False,
                'shell': False,
                'raise_errors': True
            },
            'actual_repositories': ['GitPython', 'gameta', 'gitdb']

        }
        with self.runner.isolated_filesystem() as f:
            copytree(join(dirname(dirname(__file__)), '.git'), join(f, '.git'))
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'gitdb.zip'), 'r') as template:
                template.extractall(join(f, 'core'))
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'gitpython.zip'), 'r') as template:
                template.extractall(f)
            with open(join(dirname(__file__), 'data', '.meta_other_repos'), 'r') as m1:
                output = json.load(m1)
                with open(join(f, '.meta'), 'w') as m2:
                    output['commands'] = {}
                    output['commands']['hello_world'] = params['hello_world']
                    json.dump(output, m2)
            gameta_context = GametaContext()
            gameta_context.project_dir = f
            gameta_context.load()
            context = Context(exec, obj=gameta_context)
            mock_context.return_value = context
            result = self.runner.invoke(self.exec, ['-c', params['commands'][0]])
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                f"Executing {params['commands']}\n"
                f"Executing Gameta command {params['commands'][0]}\n"
                f"Applying {params['hello_world']['commands']} to repos {params['actual_repositories']}\n"
                f"Executing {params['hello_world']['commands'][0]} in {params['actual_repositories'][1]}\n"
                f"Executing {params['hello_world']['commands'][0]} in {params['actual_repositories'][0]}\n"
                f"Executing {params['hello_world']['commands'][0]} in {params['actual_repositories'][2]}\n"
            )
            self.assertTrue(exists(join(f, '.meta')))
            with open(join(f, '.meta'), 'r') as m:
                self.assertEqual(
                    json.load(m),
                    {
                        'projects': {
                            'GitPython': {
                                '__metarepo__': False,
                                'path': 'GitPython',
                                'tags': ['a', 'b', 'c'],
                                'url': 'https://github.com/gitpython-developers/GitPython.git'
                            },
                            'gameta': {
                                '__metarepo__': True,
                                'path': '.',
                                'tags': ['metarepo'],
                                'url': 'git@github.com:genius-systems/gameta.git'
                            },
                            'gitdb': {
                                '__metarepo__': False,
                                'path': 'core/gitdb',
                                'tags': ['a', 'c', 'd'],
                                'url': 'https://github.com/gitpython-developers/gitdb.git'
                            }
                        },
                        'commands': {
                            'hello_world': params['hello_world']
                        }
                    }
                )

    @patch('gameta.cli.click.core.Context')
    def test_command_exec_multiple_commands(self, mock_context):
        params = {
            'commands': ['hello_world', 'hello_world2', 'hello_world3'],
            'hello_world': {
                'commands': ['git fetch --all --tags --prune'],
                'tags': ['a', 'b'],
                'repositories': ['gameta'],
                'verbose': False,
                'shell': False,
                'raise_errors': True
            },
            'hello_world2': {
                'commands': ['git fetch --all --tags --prune'],
                'tags': ['a', 'b'],
                'repositories': ['gameta'],
                'verbose': False,
                'shell': False,
                'raise_errors': True
            },
            'hello_world3': {
                'commands': ['git fetch --all --tags --prune'],
                'tags': ['a', 'b'],
                'repositories': ['gameta'],
                'verbose': False,
                'shell': False,
                'raise_errors': True
            },
            'actual_repositories': ['GitPython', 'gameta', 'gitdb']
        }
        with self.runner.isolated_filesystem() as f:
            copytree(join(dirname(dirname(__file__)), '.git'), join(f, '.git'))
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'gitdb.zip'), 'r') as template:
                template.extractall(join(f, 'core'))
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'gitpython.zip'), 'r') as template:
                template.extractall(f)
            with open(join(dirname(__file__), 'data', '.meta_other_repos'), 'r') as m1:
                output = json.load(m1)
                with open(join(f, '.meta'), 'w') as m2:
                    output['commands'] = {}
                    output['commands']['hello_world'] = params['hello_world']
                    output['commands']['hello_world2'] = params['hello_world2']
                    output['commands']['hello_world3'] = params['hello_world3']
                    json.dump(output, m2)
            gameta_context = GametaContext()
            gameta_context.project_dir = f
            gameta_context.load()
            context = Context(exec, obj=gameta_context)
            mock_context.return_value = context
            result = self.runner.invoke(
                self.exec,
                [
                    '-c', params['commands'][0],
                    '-c', params['commands'][1],
                    '-c', params['commands'][2],
                ]
            )
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                f"Executing {params['commands']}\n"
                f"Executing Gameta command {params['commands'][0]}\n"
                f"Applying {params['hello_world']['commands']} to repos {params['actual_repositories']}\n"
                f"Executing {params['hello_world']['commands'][0]} in {params['actual_repositories'][1]}\n"
                f"Executing {params['hello_world']['commands'][0]} in {params['actual_repositories'][0]}\n"
                f"Executing {params['hello_world']['commands'][0]} in {params['actual_repositories'][2]}\n"
                f"Executing Gameta command {params['commands'][1]}\n"
                f"Applying {params['hello_world2']['commands']} to repos {params['actual_repositories']}\n"
                f"Executing {params['hello_world2']['commands'][0]} in {params['actual_repositories'][1]}\n"
                f"Executing {params['hello_world2']['commands'][0]} in {params['actual_repositories'][0]}\n"
                f"Executing {params['hello_world2']['commands'][0]} in {params['actual_repositories'][2]}\n"
                f"Executing Gameta command {params['commands'][2]}\n"
                f"Applying {params['hello_world3']['commands']} to repos {params['actual_repositories']}\n"
                f"Executing {params['hello_world3']['commands'][0]} in {params['actual_repositories'][1]}\n"
                f"Executing {params['hello_world3']['commands'][0]} in {params['actual_repositories'][0]}\n"
                f"Executing {params['hello_world3']['commands'][0]} in {params['actual_repositories'][2]}\n"
            )
            self.assertTrue(exists(join(f, '.meta')))
            with open(join(f, '.meta'), 'r') as m:
                self.assertEqual(
                    json.load(m),
                    {
                        'projects': {
                            'GitPython': {
                                '__metarepo__': False,
                                'path': 'GitPython',
                                'tags': ['a', 'b', 'c'],
                                'url': 'https://github.com/gitpython-developers/GitPython.git'
                            },
                            'gameta': {
                                '__metarepo__': True,
                                'path': '.',
                                'tags': ['metarepo'],
                                'url': 'git@github.com:genius-systems/gameta.git'
                            },
                            'gitdb': {
                                '__metarepo__': False,
                                'path': 'core/gitdb',
                                'tags': ['a', 'c', 'd'],
                                'url': 'https://github.com/gitpython-developers/gitdb.git'
                            }
                        },
                        'commands': {
                            'hello_world': params['hello_world'],
                            'hello_world2': params['hello_world2'],
                            'hello_world3': params['hello_world3']
                        }
                    }
                )

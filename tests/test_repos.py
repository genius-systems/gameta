import json
import zipfile
from os import listdir
from os.path import join, dirname, exists
from shutil import copyfile
from unittest import TestCase
from unittest.mock import patch

from click import Context
from click.testing import CliRunner
from gameta import GametaContext

from gameta.repos import add


class TestAdd(TestCase):
    def setUp(self) -> None:
        self.runner = CliRunner()
        self.add = add

    @patch('gameta.click.BaseCommand.make_context')
    def test_add_repository_added_to_meta_file_and_cloned(self, mock_context):
        with self.runner.isolated_filesystem() as f:
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'git.zip'), 'r') as template:
                template.extractall(f)
            copyfile(join(dirname(__file__), 'data', '.meta'), join(f, '.meta'))
            context = Context(self.add, obj=GametaContext())
            context.params = {
                'name': 'GitPython',
                'url': 'https://github.com/gitpython-developers/GitPython.git',
                'path': 'GitPython',
                'tags': ['a', 'b', 'c'],
                'overwrite': False
            }
            context.obj.project_dir = f
            context.obj.load()
            mock_context.return_value = context
            result = self.runner.invoke(self.add)
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                f'Adding git repository {context.params["name"]}, {context.params["url"]} to '
                f'{join(f, context.params["path"])}\n'
                f'Repository {context.params["name"]} has been added locally\n'
                f'Adding {context.params["name"]} to .meta file\n'
                f'Successfully added repository {context.params["name"]}\n'
            )
            self.assertTrue(exists(join(f, 'GitPython')))
            self.assertTrue(all(i in listdir(join(f, 'GitPython')) for i in ['git', 'doc', 'test']))
            with open(join(f, '.meta'), 'r') as m:
                self.assertEqual(
                    json.load(m),
                    {
                        "projects": {
                            "gameta": {
                                "path": ".",
                                "tags": ["meta"],
                                "url": "git@github.com:genius-systems/gameta.git"
                            },
                            "GitPython": {
                                'url': 'https://github.com/gitpython-developers/GitPython.git',
                                'path': 'GitPython',
                                'tags': ['a', 'b', 'c'],
                            }
                        }
                    }
                )

    @patch('gameta.click.BaseCommand.make_context')
    def test_add_invalid_repository(self, mock_context):
        with self.runner.isolated_filesystem() as f:
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'git.zip'), 'r') as template:
                template.extractall(f)
            copyfile(join(dirname(__file__), 'data', '.meta'), join(f, '.meta'))
            context = Context(self.add, obj=GametaContext())
            context.params = {
                'name': 'GitPython',
                'url': 'https://test.git',
                'path': 'GitPython',
                'tags': ['a', 'b', 'c'],
                'overwrite': False
            }
            context.obj.project_dir = f
            context.obj.load()
            mock_context.return_value = context
            result = self.runner.invoke(self.add)
            self.assertEqual(result.exit_code, 1)
            self.assertEqual(
                result.output,
                f'Adding git repository {context.params["name"]}, {context.params["url"]} to '
                f'{join(f, context.params["path"])}\n'
                f'Error: Error cloning {context.params["name"]} into directory {context.params["path"]}: '
                f"GitCommandError.Cmd('git') failed due to: exit code(128)\n"
                f"  cmdline: git clone -v {context.params['url']} {join(f, context.params['path'])}\n"
                f"  stderr: 'Cloning into '{join(f, context.params['path'])}'...\n" +
                "fatal: unable to access '{url}': Could not resolve host: {host}\n'\n".format(
                    url=context.params["url"] + '/', host=context.params["url"].split('https://')[1]
                )
            )
            self.assertFalse(exists(join(f, 'GitPython')))
            with open(join(f, '.meta'), 'r') as m:
                self.assertEqual(
                    json.load(m),
                    {
                        "projects": {
                            "gameta": {
                                "path": ".",
                                "tags": ["meta"],
                                "url": "git@github.com:genius-systems/gameta.git"
                            }
                        }
                    }
                )

    @patch('gameta.click.BaseCommand.make_context')
    def test_add_repository_already_exists_in_meta_file(self, mock_context):
        with self.runner.isolated_filesystem() as f:
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'git.zip'), 'r') as template:
                template.extractall(f)
            with open(join(dirname(__file__), 'data', '.meta'), 'r') as m1:
                output = json.load(m1)
                with open(join(f, '.meta'), 'w+') as m2:
                    output['projects']['GitPython'] = {
                        "url": 'https://github.com/gitpython-developers/GitPython.git',
                        'path': 'GitPython',
                        'tags': ['a', 'b', 'c']
                    }
                    json.dump(output, m2)
            context = Context(self.add, obj=GametaContext())
            context.params = {
                'name': 'GitPython',
                'url': 'https://github.com/gitpython-developers/GitPython.git',
                'path': 'GitPython',
                'tags': ['a', 'b', 'c'],
                'overwrite': False
            }
            context.obj.project_dir = f
            context.obj.load()
            mock_context.return_value = context
            result = self.runner.invoke(self.add)
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                f'Adding git repository {context.params["name"]}, {context.params["url"]} to '
                f'{join(f, context.params["path"])}\n'
                f'Repository {context.params["name"]} has been added locally\n'
                f'Repository {context.params["name"]} has already been added to .meta file\n'
                f'Successfully added repository {context.params["name"]}\n'
            )
            self.assertTrue(exists(join(f, 'GitPython')))
            self.assertTrue(all(i in listdir(join(f, 'GitPython')) for i in ['git', 'doc', 'test']))
            with open(join(f, '.meta'), 'r') as m:
                self.assertEqual(
                    json.load(m),
                    {
                        "projects": {
                            "gameta": {
                                "path": ".",
                                "tags": ["meta"],
                                "url": "git@github.com:genius-systems/gameta.git"
                            },
                            "GitPython": {
                                'url': 'https://github.com/gitpython-developers/GitPython.git',
                                'path': 'GitPython',
                                'tags': ['a', 'b', 'c'],
                            }
                        }
                    }
                )

    @patch('gameta.click.BaseCommand.make_context')
    def test_add_repository_already_exists_locally(self, mock_context):
        with self.runner.isolated_filesystem() as f:
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'git.zip'), 'r') as template:
                template.extractall(f)
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'gitpython.zip'), 'r') as template:
                template.extractall(f)
            copyfile(join(dirname(__file__), 'data', '.meta'), join(f, '.meta'))
            context = Context(self.add, obj=GametaContext())
            context.params = {
                'name': 'GitPython',
                'url': 'https://github.com/gitpython-developers/GitPython.git',
                'path': 'GitPython',
                'tags': ['a', 'b', 'c'],
                'overwrite': False
            }
            context.obj.project_dir = f
            context.obj.load()
            mock_context.return_value = context
            result = self.runner.invoke(self.add)
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                f'Adding git repository {context.params["name"]}, {context.params["url"]} to '
                f'{join(f, context.params["path"])}\n'
                f'Repository {context.params["name"]} exists locally, skipping clone\n'
                f'Repository {context.params["name"]} has been added locally\n'
                f'Adding {context.params["name"]} to .meta file\n'
                f'Successfully added repository {context.params["name"]}\n'
            )
            self.assertTrue(exists(join(f, 'GitPython')))
            self.assertTrue(all(i in listdir(join(f, 'GitPython')) for i in ['git', 'doc', 'test']))
            with open(join(f, '.meta'), 'r') as m:
                self.assertEqual(
                    json.load(m),
                    {
                        "projects": {
                            "gameta": {
                                "path": ".",
                                "tags": ["meta"],
                                "url": "git@github.com:genius-systems/gameta.git"
                            },
                            "GitPython": {
                                'url': 'https://github.com/gitpython-developers/GitPython.git',
                                'path': 'GitPython',
                                'tags': ['a', 'b', 'c'],
                            }
                        }
                    }
                )

    @patch('gameta.click.BaseCommand.make_context')
    def test_add_repository_already_exists_locally_and_in_meta_file(self, mock_context):
        with self.runner.isolated_filesystem() as f:
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'git.zip'), 'r') as template:
                template.extractall(f)
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'gitpython.zip'), 'r') as template:
                template.extractall(f)
            with open(join(dirname(__file__), 'data', '.meta'), 'r') as m1:
                output = json.load(m1)
                with open(join(f, '.meta'), 'w+') as m2:
                    output['projects']['GitPython'] = {
                        "url": 'https://github.com/gitpython-developers/GitPython.git',
                        'path': 'GitPython',
                        'tags': ['a', 'b', 'c']
                    }
                    json.dump(output, m2)
            context = Context(self.add, obj=GametaContext())
            context.params = {
                'name': 'GitPython',
                'url': 'https://github.com/gitpython-developers/GitPython.git',
                'path': 'GitPython',
                'tags': ['a', 'b', 'c'],
                'overwrite': False
            }
            context.obj.project_dir = f
            context.obj.load()
            mock_context.return_value = context
            result = self.runner.invoke(self.add)
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                f'Adding git repository {context.params["name"]}, {context.params["url"]} to '
                f'{join(f, context.params["path"])}\n'
                f'Repository {context.params["name"]} exists locally, skipping clone\n'
                f'Repository {context.params["name"]} has been added locally\n'
                f'Repository {context.params["name"]} has already been added to .meta file\n'
                f'Successfully added repository {context.params["name"]}\n'
            )
            self.assertTrue(exists(join(f, 'GitPython')))
            self.assertTrue(all(i in listdir(join(f, 'GitPython')) for i in ['git', 'doc', 'test']))
            with open(join(f, '.meta'), 'r') as m:
                self.assertEqual(
                    json.load(m),
                    {
                        "projects": {
                            "gameta": {
                                "path": ".",
                                "tags": ["meta"],
                                "url": "git@github.com:genius-systems/gameta.git"
                            },
                            "GitPython": {
                                'url': 'https://github.com/gitpython-developers/GitPython.git',
                                'path': 'GitPython',
                                'tags': ['a', 'b', 'c'],
                            }
                        }
                    }
                )

    @patch('gameta.click.BaseCommand.make_context')
    def test_add_repository_already_exists_locally_parameters_differ(self, mock_context):
        with self.runner.isolated_filesystem() as f:
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'git.zip'), 'r') as template:
                template.extractall(f)
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'gitpython.zip'), 'r') as template:
                template.extractall(f)
            copyfile(join(dirname(__file__), 'data', '.meta'), join(f, '.meta'))
            context = Context(self.add, obj=GametaContext())
            context.params = {
                'name': 'GitPython',
                'url': 'https://test.git',
                'path': 'GitPython',
                'tags': ['a', 'b', 'c'],
                'overwrite': False
            }
            context.obj.project_dir = f
            context.obj.load()
            mock_context.return_value = context
            result = self.runner.invoke(self.add)
            self.assertEqual(result.exit_code, 1)
            self.assertEqual(
                result.output,
                f'Adding git repository {context.params["name"]}, {context.params["url"]} to '
                f'{join(f, context.params["path"])}\n'
                f'Error: URL of repository at {join(f, context.params["name"])} '
                f'(https://github.com/gitpython-developers/GitPython.git) '
                f'does not match the requested url {context.params["url"]}\n'
            )
            with open(join(f, '.meta'), 'r') as m:
                self.assertEqual(
                    json.load(m),
                    {
                        "projects": {
                            "gameta": {
                                "path": ".",
                                "tags": ["meta"],
                                "url": "git@github.com:genius-systems/gameta.git"
                            }
                        }
                    }
                )

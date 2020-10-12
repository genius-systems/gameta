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

from gameta.repos import add, delete, ls, update


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
                                "tags": ["metarepo"],
                                "url": "git@github.com:genius-systems/gameta.git"
                            },
                            "GitPython": {
                                'url': 'https://github.com/gitpython-developers/GitPython.git',
                                'path': 'GitPython',
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
                f'Error: Error cloning {context.params["name"]} into directory {join(f, context.params["path"])}: '
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
                                "tags": ["metarepo"],
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
                        "tags": ['a', 'b', 'c']
                    }
                    json.dump(output, m2)
            context = Context(self.add, obj=GametaContext())
            context.params = {
                'name': 'GitPython',
                'url': 'https://github.com/gitpython-developers/GitPython.git',
                'path': 'GitPython',
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
                                "tags": ["metarepo"],
                                "url": "git@github.com:genius-systems/gameta.git"
                            },
                            "GitPython": {
                                'url': 'https://github.com/gitpython-developers/GitPython.git',
                                'path': 'GitPython',
                                "tags": ['a', 'b', 'c']
                            }
                        }
                    }
                )

    @patch('gameta.click.BaseCommand.make_context')
    def test_add_repository_already_exists_in_meta_file_overwritten(self, mock_context):
        with self.runner.isolated_filesystem() as f:
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'git.zip'), 'r') as template:
                template.extractall(f)
            with open(join(dirname(__file__), 'data', '.meta'), 'r') as m1:
                output = json.load(m1)
                with open(join(f, '.meta'), 'w+') as m2:
                    output['projects']['GitPython'] = {
                        "url": 'https://github.com/gitpython-developers/GitPython.git',
                        'path': 'GitPython',
                    }
                    json.dump(output, m2)
            context = Context(self.add, obj=GametaContext())
            context.params = {
                'name': 'GitPython',
                'url': 'https://github.com/gitpython-developers/gitdb.git',
                'path': 'GitPython',
                'overwrite': True
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
                f'Overwriting repository {context.params["name"]} in .meta file\n'
                f'Successfully added repository {context.params["name"]}\n'
            )
            self.assertTrue(exists(join(f, 'GitPython')))
            self.assertTrue(all(i in listdir(join(f, 'GitPython')) for i in ['gitdb', 'doc', 'setup.py']))
            with open(join(f, '.meta'), 'r') as m:
                self.assertEqual(
                    json.load(m),
                    {
                        "projects": {
                            "gameta": {
                                "path": ".",
                                "tags": ["metarepo"],
                                "url": "git@github.com:genius-systems/gameta.git"
                            },
                            "GitPython": {
                                'url': 'https://github.com/gitpython-developers/gitdb.git',
                                'path': 'GitPython',
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
                                "tags": ["metarepo"],
                                "url": "git@github.com:genius-systems/gameta.git"
                            },
                            "GitPython": {
                                'url': 'https://github.com/gitpython-developers/GitPython.git',
                                'path': 'GitPython',
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
                    }
                    json.dump(output, m2)
            context = Context(self.add, obj=GametaContext())
            context.params = {
                'name': 'GitPython',
                'url': 'https://github.com/gitpython-developers/GitPython.git',
                'path': 'GitPython',
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
                                "tags": ["metarepo"],
                                "url": "git@github.com:genius-systems/gameta.git"
                            },
                            "GitPython": {
                                'url': 'https://github.com/gitpython-developers/GitPython.git',
                                'path': 'GitPython',
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
                                "tags": ["metarepo"],
                                "url": "git@github.com:genius-systems/gameta.git"
                            }
                        }
                    }
                )


class TestDelete(TestCase):
    def setUp(self) -> None:
        self.runner = CliRunner()
        self.delete = delete

    @patch('gameta.click.BaseCommand.make_context')
    def test_delete_repository_deleted_and_cleared(self, mock_context):
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
            context = Context(self.delete, obj=GametaContext())
            context.params = {
                'name': 'GitPython',
                'clear': True
            }
            context.obj.project_dir = f
            context.obj.load()
            mock_context.return_value = context
            result = self.runner.invoke(self.delete)
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                f"Deleting repository {context.params['name']} from .meta file\n"
                f"Clearing repository {context.params['name']} locally\n"
                f"Repository {context.params['name']} successfully deleted\n"
            )
            self.assertFalse(exists(join(f, 'GitPython')))
            with open(join(f, '.meta'), 'r') as m:
                self.assertEqual(
                    json.load(m),
                    {
                        "projects": {
                            "gameta": {
                                "path": ".",
                                "tags": ["metarepo"],
                                "url": "git@github.com:genius-systems/gameta.git"
                            }
                        }
                    }
                )

    @patch('gameta.click.BaseCommand.make_context')
    def test_delete_repository_deleted_but_not_cleared(self, mock_context):
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
            context = Context(self.delete, obj=GametaContext())
            context.params = {
                'name': 'GitPython',
                'clear': False
            }
            context.obj.project_dir = f
            context.obj.load()
            mock_context.return_value = context
            result = self.runner.invoke(self.delete)
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                f"Deleting repository {context.params['name']} from .meta file\n"
                f"Repository {context.params['name']} successfully deleted\n"
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
                                "tags": ["metarepo"],
                                "url": "git@github.com:genius-systems/gameta.git"
                            }
                        }
                    }
                )

    @patch('gameta.click.BaseCommand.make_context')
    def test_delete_repository_does_not_exist(self, mock_context):
        with self.runner.isolated_filesystem() as f:
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'git.zip'), 'r') as template:
                template.extractall(f)
            copyfile(join(dirname(__file__), 'data', '.meta'), join(f, '.meta'))
            context = Context(self.delete, obj=GametaContext())
            context.params = {
                'name': 'GitPython',
                'clear': True
            }
            context.obj.project_dir = f
            context.obj.load()
            mock_context.return_value = context
            result = self.runner.invoke(self.delete)
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                f"Deleting repository {context.params['name']} from .meta file\n"
                f"Repository {context.params['name']} does not exist in the .meta file, ignoring\n"
            )
            with open(join(f, '.meta'), 'r') as m:
                self.assertEqual(
                    json.load(m),
                    {
                        "projects": {
                            "gameta": {
                                "path": ".",
                                "tags": ["metarepo"],
                                "url": "git@github.com:genius-systems/gameta.git"
                            }
                        }
                    }
                )


class TestLs(TestCase):
    def setUp(self) -> None:
        self.runner = CliRunner()
        self.ls = ls

    @patch('gameta.click.BaseCommand.make_context')
    def test_ls_repositories_available(self, mock_context):
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
                    output['projects']['genisys'] = {
                        "url": 'https://github.com/test/genisys.git',
                        "path": "core/genisys",
                        'tags': ['c', 'd', 'e']
                    }
                    json.dump(output, m2)
            context = Context(self.ls, obj=GametaContext())
            context.obj.project_dir = f
            context.obj.load()
            mock_context.return_value = context
            result = self.runner.invoke(self.ls)
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                f"Listing repositories managed in metarepo {f}\n"
                "gameta\n"
                "GitPython\n"
                "genisys\n"
            )

    @patch('gameta.click.BaseCommand.make_context')
    def test_ls_no_repositories_available(self, mock_context):
        with self.runner.isolated_filesystem() as f:
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'git.zip'), 'r') as template:
                template.extractall(f)
            with open(join(f, '.meta'), 'w') as m:
                json.dump(
                    {
                        'projects': {}
                    }, m
                )
            context = Context(self.ls, obj=GametaContext())
            context.obj.project_dir = f
            context.obj.load()
            mock_context.return_value = context
            result = self.runner.invoke(self.ls)
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                f"Listing repositories managed in metarepo {f}\n"
            )


class TestUpdate(TestCase):
    def setUp(self) -> None:
        self.runner = CliRunner()
        self.update = update

    @patch('gameta.click.BaseCommand.make_context')
    def test_update_no_name_specified(self, mock_context):
        with self.runner.isolated_filesystem() as f:
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'git.zip'), 'r') as template:
                template.extractall(f)
            copyfile(join(dirname(__file__), 'data', '.meta_other_repos'), join(f, '.meta'))
            context = Context(self.update, obj=GametaContext())
            context.params = {
                'new_name': None,
                'new_url': None,
                'new_path': None
            }
            context.obj.project_dir = f
            context.obj.load()
            mock_context.return_value = context
            result = self.runner.invoke(self.update)
            self.assertEqual(result.exit_code, 1)

    @patch('gameta.click.BaseCommand.make_context')
    def test_update_name_does_not_exist_in_repo(self, mock_context):
        with self.runner.isolated_filesystem() as f:
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'git.zip'), 'r') as template:
                template.extractall(f)
            copyfile(join(dirname(__file__), 'data', '.meta_other_repos'), join(f, '.meta'))
            context = Context(self.update, obj=GametaContext())
            context.params = {
                'name': 'test',
                'new_name': None,
                'new_url': None,
                'new_path': None,
                'sync': False
            }
            context.obj.project_dir = f
            context.obj.load()
            mock_context.return_value = context
            result = self.runner.invoke(self.update)
            self.assertEqual(result.exit_code, 1)
            self.assertEqual(
                result.output,
                f'Error: Repository {context.params["name"]} does not exist in the .meta file, please add it first\n'
            )

    @patch('gameta.click.BaseCommand.make_context')
    def test_update_all_parameters_updated(self, mock_context):
        with self.runner.isolated_filesystem() as f:
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'git.zip'), 'r') as template:
                template.extractall(f)
            copyfile(join(dirname(__file__), 'data', '.meta_other_repos'), join(f, '.meta'))
            context = Context(self.update, obj=GametaContext())
            context.params = {
                'name': 'GitPython',
                'new_name': 'test',
                'new_url': 'https://github.com/jantman/GitPython.git',
                'new_path': 'core/GitPython',
                'sync': False
            }
            context.obj.project_dir = f
            context.obj.load()
            mock_context.return_value = context
            result = self.runner.invoke(self.update)
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                f'Updating repository GitPython with new details (name: {context.params["new_name"]}, '
                f'url: {context.params["new_url"]}, path: {context.params["new_path"]})\n'
                f'Successfully updated repository {context.params["new_name"]} with new details\n'
            )
            with open(join(f, '.meta')) as m:
                self.assertEqual(
                    json.load(m),
                    {
                        'projects': {
                            "gameta": {
                                "path": ".",
                                "tags": ["metarepo"],
                                "url": "git@github.com:genius-systems/gameta.git"
                            },
                            "test": {
                                "path": "core/GitPython",
                                "tags": ["a", "b", "c"],
                                "url": "https://github.com/jantman/GitPython.git"
                            },
                            "gitdb": {
                                "path": "core/gitdb",
                                "tags": ["a", "c", "d"],
                                "url": "https://github.com/gitpython-developers/gitdb.git"
                            }
                        }
                    }
                )

    @patch('gameta.click.BaseCommand.make_context')
    def test_update_all_parameters_updated_with_physical_sync(self, mock_context):
        with self.runner.isolated_filesystem() as f:
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'git.zip'), 'r') as template:
                template.extractall(f)
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'gitpython.zip'), 'r') as template:
                template.extractall(f)
            copyfile(join(dirname(__file__), 'data', '.meta_other_repos'), join(f, '.meta'))
            context = Context(self.update, obj=GametaContext())
            context.params = {
                'name': 'GitPython',
                'new_name': 'test',
                'new_url': 'https://github.com/jantman/GitPython.git',
                'new_path': 'core/GitPython',
                'sync': True
            }
            context.obj.project_dir = f
            context.obj.load()
            mock_context.return_value = context
            result = self.runner.invoke(self.update)
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                f'Updating repository GitPython with new details (name: {context.params["new_name"]}, '
                f'url: {context.params["new_url"]}, path: {context.params["new_path"]})\n'
                "Performing a physical sync\n"
                f"Cloning repository from new URL: {context.params['new_url']}\n"
                "Sync complete\n"
                f'Successfully updated repository {context.params["new_name"]} with new details\n'
            )
            with open(join(f, '.meta')) as m:
                self.assertEqual(
                    json.load(m),
                    {
                        'projects': {
                            "gameta": {
                                "path": ".",
                                "tags": ["metarepo"],
                                "url": "git@github.com:genius-systems/gameta.git"
                            },
                            "test": {
                                "path": "core/GitPython",
                                "tags": ["a", "b", "c"],
                                "url": "https://github.com/jantman/GitPython.git"
                            },
                            "gitdb": {
                                "path": "core/gitdb",
                                "tags": ["a", "c", "d"],
                                "url": "https://github.com/gitpython-developers/gitdb.git"
                            }
                        }
                    }
                )
            self.assertFalse(exists(join(f, 'GitPython')))
            self.assertTrue(exists(join(f, 'core', 'GitPython')))
            self.assertTrue(all(i in listdir(join(f, 'core', 'GitPython')) for i in ['git', 'doc']))

    @patch('gameta.click.BaseCommand.make_context')
    def test_update_no_new_path_updated_with_physical_sync(self, mock_context):
        with self.runner.isolated_filesystem() as f:
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'git.zip'), 'r') as template:
                template.extractall(f)
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'gitpython.zip'), 'r') as template:
                template.extractall(f)
            copyfile(join(dirname(__file__), 'data', '.meta_other_repos'), join(f, '.meta'))
            context = Context(self.update, obj=GametaContext())
            context.params = {
                'name': 'GitPython',
                'new_name': 'test',
                'new_path': None,
                'new_url': 'https://github.com/jantman/GitPython.git',
                'sync': True
            }
            context.obj.project_dir = f
            context.obj.load()
            mock_context.return_value = context
            result = self.runner.invoke(self.update)
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                f'Updating repository GitPython with new details (name: {context.params["new_name"]}, '
                f'url: {context.params["new_url"]}, path: {context.params["new_path"]})\n'
                "Performing a physical sync\n"
                f"Cloning repository from new URL: {context.params['new_url']}\n"
                "Sync complete\n"
                f'Successfully updated repository {context.params["new_name"]} with new details\n'
            )
            with open(join(f, '.meta')) as m:
                self.assertEqual(
                    json.load(m),
                    {
                        'projects': {
                            "gameta": {
                                "path": ".",
                                "tags": ["metarepo"],
                                "url": "git@github.com:genius-systems/gameta.git"
                            },
                            "test": {
                                "path": "GitPython",
                                "tags": ["a", "b", "c"],
                                "url": "https://github.com/jantman/GitPython.git"
                            },
                            "gitdb": {
                                "path": "core/gitdb",
                                "tags": ["a", "c", "d"],
                                "url": "https://github.com/gitpython-developers/gitdb.git"
                            }
                        }
                    }
                )
            self.assertTrue(exists(join(f, 'GitPython')))
            self.assertTrue(all(i in listdir(join(f, 'GitPython')) for i in ['git', 'doc']))

    @patch('gameta.click.BaseCommand.make_context')
    def test_update_no_new_url_updated_with_physical_sync(self, mock_context):
        with self.runner.isolated_filesystem() as f:
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'git.zip'), 'r') as template:
                template.extractall(f)
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'gitpython.zip'), 'r') as template:
                template.extractall(f)
            copyfile(join(dirname(__file__), 'data', '.meta_other_repos'), join(f, '.meta'))
            context = Context(self.update, obj=GametaContext())
            context.params = {
                'name': 'GitPython',
                'new_name': 'test',
                'new_path': 'core/gitpython',
                'new_url': None,
                'sync': True
            }
            context.obj.project_dir = f
            context.obj.load()
            mock_context.return_value = context
            result = self.runner.invoke(self.update)
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                f'Updating repository GitPython with new details (name: {context.params["new_name"]}, '
                f'url: {context.params["new_url"]}, path: {context.params["new_path"]})\n'
                "Performing a physical sync\n"
                f"Copying repository to new path: {context.params['new_path']}\n"
                "Sync complete\n"
                f'Successfully updated repository {context.params["new_name"]} with new details\n'
            )
            with open(join(f, '.meta')) as m:
                self.assertEqual(
                    json.load(m),
                    {
                        'projects': {
                            "gameta": {
                                "path": ".",
                                "tags": ["metarepo"],
                                "url": "git@github.com:genius-systems/gameta.git"
                            },
                            "test": {
                                "path": "core/gitpython",
                                "tags": ["a", "b", "c"],
                                "url": "https://github.com/gitpython-developers/GitPython.git"
                            },
                            "gitdb": {
                                "path": "core/gitdb",
                                "tags": ["a", "c", "d"],
                                "url": "https://github.com/gitpython-developers/gitdb.git"
                            }
                        }
                    }
                )
            self.assertFalse(exists(join(f, 'GitPython')))
            self.assertTrue(exists(join(f, 'core', 'gitpython')))
            self.assertTrue(all(i in listdir(join(f, 'core', 'gitpython')) for i in ['git', 'doc', 'test']))

    @patch('gameta.click.BaseCommand.make_context')
    def test_update_only_name_change_updated_with_physical_sync(self, mock_context):
        with self.runner.isolated_filesystem() as f:
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'git.zip'), 'r') as template:
                template.extractall(f)
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'gitpython.zip'), 'r') as template:
                template.extractall(f)
            copyfile(join(dirname(__file__), 'data', '.meta_other_repos'), join(f, '.meta'))
            context = Context(self.update, obj=GametaContext())
            context.params = {
                'name': 'GitPython',
                'new_name': 'test',
                'new_path': None,
                'new_url': None,
                'sync': True
            }
            context.obj.project_dir = f
            context.obj.load()
            mock_context.return_value = context
            result = self.runner.invoke(self.update)
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                f'Updating repository GitPython with new details (name: {context.params["new_name"]}, '
                f'url: {context.params["new_url"]}, path: {context.params["new_path"]})\n'
                "Performing a physical sync\n"
                "No physical changes\n"
                "Sync complete\n"
                f'Successfully updated repository {context.params["new_name"]} with new details\n'
            )
            with open(join(f, '.meta')) as m:
                self.assertEqual(
                    json.load(m),
                    {
                        'projects': {
                            "gameta": {
                                "path": ".",
                                "tags": ["metarepo"],
                                "url": "git@github.com:genius-systems/gameta.git"
                            },
                            "test": {
                                "path": "GitPython",
                                "tags": ["a", "b", "c"],
                                "url": "https://github.com/gitpython-developers/GitPython.git"
                            },
                            "gitdb": {
                                "path": "core/gitdb",
                                "tags": ["a", "c", "d"],
                                "url": "https://github.com/gitpython-developers/gitdb.git"
                            }
                        }
                    }
                )
            self.assertTrue(exists(join(f, 'GitPython')))
            self.assertTrue(all(i in listdir(join(f, 'GitPython')) for i in ['git', 'doc', 'test']))

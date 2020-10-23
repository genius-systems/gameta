import json
import zipfile
from os.path import join, dirname
from shutil import copyfile
from unittest import TestCase
from unittest.mock import patch

from click import Context
from click.testing import CliRunner
from gameta import GametaContext

from gameta.tags import add, delete


class TestAdd(TestCase):
    def setUp(self) -> None:
        self.runner = CliRunner()
        self.add = add

    @patch('gameta.click.Context.ensure_object')
    def test_add_key_parameters_not_provided(self, mock_ensure_object):
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

    @patch('gameta.click.Context.ensure_object')
    def test_add_empty_meta_file(self, mock_ensure_object):
        params = {
            'name': 'GitPython',
            'tags': ('a', 'b', 'c')
        }
        with self.runner.isolated_filesystem() as f:
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'git.zip'), 'r') as template:
                template.extractall(f)
            with open(join(f, '.meta'), 'w+') as m:
                json.dump({
                    'projects': {}
                }, m)
            context = GametaContext()
            context.project_dir = f
            context.load()
            mock_ensure_object.return_value = context
            result = self.runner.invoke(
                self.add,
                ['--name', params['name'], '-t', params['tags'][0], '-t', params['tags'][1], '-t', params['tags'][2]]
            )
            self.assertEqual(result.exit_code, 1)
            self.assertEqual(
                result.output,
                f"Adding tags {params['tags']} to {params['name']}\n"
                f"Error: Repository {params['name']} does not exist in .meta file\n"
            )

    @patch('gameta.click.Context.ensure_object')
    def test_add_nonexistent_repository(self, mock_ensure_object):
        params = {
            'name': 'GitPython',
            'tags': ('a', 'b', 'c')
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
                ['--name', params['name'], '-t', params['tags'][0], '-t', params['tags'][1], '-t', params['tags'][2]]
            )
            self.assertEqual(result.exit_code, 1)
            self.assertEqual(
                result.output,
                f"Adding tags {params['tags']} to {params['name']}\n"
                f"Error: Repository {params['name']} does not exist in .meta file\n"
            )

    @patch('gameta.click.Context.ensure_object')
    def test_add_repository_with_no_tags_initially(self, mock_ensure_object):
        params = {
            'name': 'GitPython',
            'tags': ('a', 'b', 'c')
        }
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
            context = GametaContext()
            context.project_dir = f
            context.load()
            mock_ensure_object.return_value = context
            result = self.runner.invoke(
                self.add,
                ['--name', params['name'], '-t', params['tags'][0], '-t', params['tags'][1], '-t', params['tags'][2]]
            )
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                f"Adding tags {params['tags']} to {params['name']}\n"
                f"Successfully added tags to repository {params['name']}\n"
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
                            },
                            'GitPython': {
                                "url": 'https://github.com/gitpython-developers/GitPython.git',
                                'path': 'GitPython',
                                'tags': ['a', 'b', 'c']
                            }
                        }
                    }
                )

    @patch('gameta.click.Context.ensure_object')
    def test_add_repository_with_disjoint_set_of_tags(self, mock_ensure_object):
        params = {
            'name': 'GitPython',
            'tags': ('a', 'b', 'c')
        }
        with self.runner.isolated_filesystem() as f:
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'git.zip'), 'r') as template:
                template.extractall(f)
            with open(join(dirname(__file__), 'data', '.meta'), 'r') as m1:
                output = json.load(m1)
                with open(join(f, '.meta'), 'w+') as m2:
                    output['projects']['GitPython'] = {
                        "url": 'https://github.com/gitpython-developers/GitPython.git',
                        'path': 'GitPython',
                        'tags': ['d', 'e', 'f']
                    }
                    json.dump(output, m2)
            context = GametaContext()
            context.project_dir = f
            context.load()
            mock_ensure_object.return_value = context
            result = self.runner.invoke(
                self.add,
                ['--name', params['name'], '-t', params['tags'][0], '-t', params['tags'][1], '-t', params['tags'][2]]
            )
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                f"Adding tags {params['tags']} to {params['name']}\n"
                f"Successfully added tags to repository {params['name']}\n"
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
                            },
                            'GitPython': {
                                "url": 'https://github.com/gitpython-developers/GitPython.git',
                                'path': 'GitPython',
                                'tags': ['a', 'b', 'c', 'd', 'e', 'f']
                            }
                        }
                    }
                )

    @patch('gameta.click.Context.ensure_object')
    def test_add_repository_with_duplicate_tags(self, mock_ensure_object):
        params = {
            'name': 'GitPython',
            'tags': ('a', 'b', 'c')
        }
        with self.runner.isolated_filesystem() as f:
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'git.zip'), 'r') as template:
                template.extractall(f)
            with open(join(dirname(__file__), 'data', '.meta'), 'r') as m1:
                output = json.load(m1)
                with open(join(f, '.meta'), 'w+') as m2:
                    output['projects']['GitPython'] = {
                        "url": 'https://github.com/gitpython-developers/GitPython.git',
                        'path': 'GitPython',
                        'tags': ['c', 'b', 'f']
                    }
                    json.dump(output, m2)
            context = GametaContext()
            context.project_dir = f
            context.load()
            mock_ensure_object.return_value = context
            result = self.runner.invoke(
                self.add,
                ['--name', params['name'], '-t', params['tags'][0], '-t', params['tags'][1], '-t', params['tags'][2]]
            )
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                f"Adding tags {params['tags']} to {params['name']}\n"
                f"Successfully added tags to repository {params['name']}\n"
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
                            },
                            'GitPython': {
                                "url": 'https://github.com/gitpython-developers/GitPython.git',
                                'path': 'GitPython',
                                'tags': ['a', 'b', 'c', 'f']
                            }
                        }
                    }
                )


class TestDelete(TestCase):
    def setUp(self) -> None:
        self.runner = CliRunner()
        self.delete = delete

    @patch('gameta.click.Context.ensure_object')
    def test_delete_key_parameters_not_provided(self, mock_ensure_object):
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

    @patch('gameta.click.Context.ensure_object')
    def test_delete_empty_meta_file(self, mock_ensure_object):
        params = {
            'name': 'GitPython',
            'tags': ('a', 'b', 'c')
        }
        with self.runner.isolated_filesystem() as f:
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'git.zip'), 'r') as template:
                template.extractall(f)
            with open(join(f, '.meta'), 'w+') as m:
                json.dump({
                    'projects': {}
                }, m)
            context = GametaContext()
            context.project_dir = f
            context.load()
            mock_ensure_object.return_value = context
            result = self.runner.invoke(
                self.delete,
                ['--name', params['name'], '-t', params['tags'][0], '-t', params['tags'][1], '-t', params['tags'][2]]
            )
            self.assertEqual(result.exit_code, 1)
            self.assertEqual(
                result.output,
                f"Deleting tags {params['tags']} from {params['name']}\n"
                f"Error: Repository {params['name']} does not exist in .meta file\n"
            )

    @patch('gameta.click.Context.ensure_object')
    def test_delete_nonexistent_repository(self, mock_ensure_object):
        params = {
            'name': 'GitPython',
            'tags': ('a', 'b', 'c')
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
                self.delete,
                ['--name', params['name'], '-t', params['tags'][0], '-t', params['tags'][1], '-t', params['tags'][2]]
            )
            self.assertEqual(result.exit_code, 1)
            self.assertEqual(
                result.output,
                f"Deleting tags {params['tags']} from {params['name']}\n"
                f"Error: Repository {params['name']} does not exist in .meta file\n"
            )

    @patch('gameta.click.Context.ensure_object')
    def test_delete_repository_with_no_tags(self, mock_ensure_object):
        params = {
            'name': 'GitPython',
            'tags': ('a', 'b', 'c')
        }
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
            context = GametaContext()
            context.project_dir = f
            context.load()
            mock_ensure_object.return_value = context
            result = self.runner.invoke(
                self.delete,
                ['--name', params['name'], '-t', params['tags'][0], '-t', params['tags'][1], '-t', params['tags'][2]]
            )
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                f"Deleting tags {params['tags']} from {params['name']}\n"
                f"Successfully deleted tags from repository {params['name']}\n"
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
                            },
                            'GitPython': {
                                "url": 'https://github.com/gitpython-developers/GitPython.git',
                                'path': 'GitPython',
                                'tags': []
                            }
                        }
                    }
                )

    @patch('gameta.click.Context.ensure_object')
    def test_delete_repository_with_disjoint_set_of_tags(self, mock_ensure_object):
        params = {
            'name': 'GitPython',
            'tags': ('a', 'b', 'c')
        }
        with self.runner.isolated_filesystem() as f:
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'git.zip'), 'r') as template:
                template.extractall(f)
            with open(join(dirname(__file__), 'data', '.meta'), 'r') as m1:
                output = json.load(m1)
                with open(join(f, '.meta'), 'w+') as m2:
                    output['projects']['GitPython'] = {
                        "url": 'https://github.com/gitpython-developers/GitPython.git',
                        'path': 'GitPython',
                        'tags': ['d', 'e', 'f']
                    }
                    json.dump(output, m2)
            context = GametaContext()
            context.project_dir = f
            context.load()
            mock_ensure_object.return_value = context
            result = self.runner.invoke(
                self.delete,
                ['--name', params['name'], '-t', params['tags'][0], '-t', params['tags'][1], '-t', params['tags'][2]]
            )
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                f"Deleting tags {params['tags']} from {params['name']}\n"
                f"Successfully deleted tags from repository {params['name']}\n"
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
                            },
                            'GitPython': {
                                "url": 'https://github.com/gitpython-developers/GitPython.git',
                                'path': 'GitPython',
                                'tags': ['d', 'e', 'f']
                            }
                        }
                    }
                )

    @patch('gameta.click.Context.ensure_object')
    def test_delete_repository_with_duplicate_tags(self, mock_ensure_object):
        params = {
            'name': 'GitPython',
            'tags': ('a', 'b', 'c')
        }
        with self.runner.isolated_filesystem() as f:
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'git.zip'), 'r') as template:
                template.extractall(f)
            with open(join(dirname(__file__), 'data', '.meta'), 'r') as m1:
                output = json.load(m1)
                with open(join(f, '.meta'), 'w+') as m2:
                    output['projects']['GitPython'] = {
                        "url": 'https://github.com/gitpython-developers/GitPython.git',
                        'path': 'GitPython',
                        'tags': ['c', 'b', 'f']
                    }
                    json.dump(output, m2)
            context = GametaContext()
            context.project_dir = f
            context.load()
            mock_ensure_object.return_value = context
            result = self.runner.invoke(
                self.delete,
                ['--name', params['name'], '-t', params['tags'][0], '-t', params['tags'][1], '-t', params['tags'][2]]
            )
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                f"Deleting tags {params['tags']} from {params['name']}\n"
                f"Successfully deleted tags from repository {params['name']}\n"
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
                            },
                            'GitPython': {
                                "url": 'https://github.com/gitpython-developers/GitPython.git',
                                'path': 'GitPython',
                                'tags': ['f']
                            }
                        }
                    }
                )

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

    @patch('gameta.click.BaseCommand.make_context')
    def test_add_empty_meta_file(self, mock_context):
        with self.runner.isolated_filesystem() as f:
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'git.zip'), 'r') as template:
                template.extractall(f)
            with open(join(f, '.meta'), 'w+') as m:
                json.dump({
                    'projects': {}
                }, m)
            context = Context(self.add, obj=GametaContext())
            context.params = {
                'name': 'GitPython',
                'tags': ['a', 'b', 'c']
            }
            context.obj.project_dir = f
            context.obj.load()
            mock_context.return_value = context
            result = self.runner.invoke(self.add)
            self.assertEqual(result.exit_code, 1)
            self.assertEqual(
                result.output,
                f"Adding tags {context.params['tags']} to {context.params['name']}\n"
                f"Error: Repository {context.params['name']} does not exist in .meta file\n"
            )

    @patch('gameta.click.BaseCommand.make_context')
    def test_add_nonexistent_repository(self, mock_context):
        with self.runner.isolated_filesystem() as f:
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'git.zip'), 'r') as template:
                template.extractall(f)
            copyfile(join(dirname(__file__), 'data', '.meta'), join(f, '.meta'))
            context = Context(self.add, obj=GametaContext())
            context.params = {
                'name': 'GitPython',
                'tags': ['a', 'b', 'c']
            }
            context.obj.project_dir = f
            context.obj.load()
            mock_context.return_value = context
            result = self.runner.invoke(self.add)
            self.assertEqual(result.exit_code, 1)
            self.assertEqual(
                result.output,
                f"Adding tags {context.params['tags']} to {context.params['name']}\n"
                f"Error: Repository {context.params['name']} does not exist in .meta file\n"
            )

    @patch('gameta.click.BaseCommand.make_context')
    def test_add_repository_with_no_tags_initially(self, mock_context):
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
                'tags': ['a', 'b', 'c']
            }
            context.obj.project_dir = f
            context.obj.load()
            mock_context.return_value = context
            result = self.runner.invoke(self.add)
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                f"Adding tags {context.params['tags']} to {context.params['name']}\n"
                f"Successfully added tags to repository {context.params['name']}\n"
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

    @patch('gameta.click.BaseCommand.make_context')
    def test_add_repository_with_disjoint_set_of_tags(self, mock_context):
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
            context = Context(self.add, obj=GametaContext())
            context.params = {
                'name': 'GitPython',
                'tags': ['a', 'b', 'c']
            }
            context.obj.project_dir = f
            context.obj.load()
            mock_context.return_value = context
            result = self.runner.invoke(self.add)
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                f"Adding tags {context.params['tags']} to {context.params['name']}\n"
                f"Successfully added tags to repository {context.params['name']}\n"
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

    @patch('gameta.click.BaseCommand.make_context')
    def test_add_repository_with_duplicate_tags(self, mock_context):
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
            context = Context(self.add, obj=GametaContext())
            context.params = {
                'name': 'GitPython',
                'tags': ['a', 'b', 'c']
            }
            context.obj.project_dir = f
            context.obj.load()
            mock_context.return_value = context
            result = self.runner.invoke(self.add)
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                f"Adding tags {context.params['tags']} to {context.params['name']}\n"
                f"Successfully added tags to repository {context.params['name']}\n"
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

    @patch('gameta.click.BaseCommand.make_context')
    def test_delete_empty_meta_file(self, mock_context):
        with self.runner.isolated_filesystem() as f:
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'git.zip'), 'r') as template:
                template.extractall(f)
            with open(join(f, '.meta'), 'w+') as m:
                json.dump({
                    'projects': {}
                }, m)
            context = Context(self.delete, obj=GametaContext())
            context.params = {
                'name': 'GitPython',
                'tags': ['a', 'b', 'c']
            }
            context.obj.project_dir = f
            context.obj.load()
            mock_context.return_value = context
            result = self.runner.invoke(self.delete)
            self.assertEqual(result.exit_code, 1)
            self.assertEqual(
                result.output,
                f"Deleting tags {context.params['tags']} from {context.params['name']}\n"
                f"Error: Repository {context.params['name']} does not exist in .meta file\n"
            )

    @patch('gameta.click.BaseCommand.make_context')
    def test_delete_nonexistent_repository(self, mock_context):
        with self.runner.isolated_filesystem() as f:
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'git.zip'), 'r') as template:
                template.extractall(f)
            copyfile(join(dirname(__file__), 'data', '.meta'), join(f, '.meta'))
            context = Context(self.delete, obj=GametaContext())
            context.params = {
                'name': 'GitPython',
                'tags': ['a', 'b', 'c']
            }
            context.obj.project_dir = f
            context.obj.load()
            mock_context.return_value = context
            result = self.runner.invoke(self.delete)
            self.assertEqual(result.exit_code, 1)
            self.assertEqual(
                result.output,
                f"Deleting tags {context.params['tags']} from {context.params['name']}\n"
                f"Error: Repository {context.params['name']} does not exist in .meta file\n"
            )

    @patch('gameta.click.BaseCommand.make_context')
    def test_delete_repository_with_no_tags(self, mock_context):
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
            context = Context(self.delete, obj=GametaContext())
            context.params = {
                'name': 'GitPython',
                'tags': ['a', 'b', 'c']
            }
            context.obj.project_dir = f
            context.obj.load()
            mock_context.return_value = context
            result = self.runner.invoke(self.delete)
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                f"Deleting tags {context.params['tags']} from {context.params['name']}\n"
                f"Successfully deleted tags from repository {context.params['name']}\n"
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

    @patch('gameta.click.BaseCommand.make_context')
    def test_delete_repository_with_disjoint_set_of_tags(self, mock_context):
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
            context = Context(self.delete, obj=GametaContext())
            context.params = {
                'name': 'GitPython',
                'tags': ['a', 'b', 'c']
            }
            context.obj.project_dir = f
            context.obj.load()
            mock_context.return_value = context
            result = self.runner.invoke(self.delete)
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                f"Deleting tags {context.params['tags']} from {context.params['name']}\n"
                f"Successfully deleted tags from repository {context.params['name']}\n"
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

    @patch('gameta.click.BaseCommand.make_context')
    def test_delete_repository_with_duplicate_tags(self, mock_context):
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
            context = Context(self.delete, obj=GametaContext())
            context.params = {
                'name': 'GitPython',
                'tags': ['a', 'b', 'c']
            }
            context.obj.project_dir = f
            context.obj.load()
            mock_context.return_value = context
            result = self.runner.invoke(self.delete)
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                f"Deleting tags {context.params['tags']} from {context.params['name']}\n"
                f"Successfully deleted tags from repository {context.params['name']}\n"
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

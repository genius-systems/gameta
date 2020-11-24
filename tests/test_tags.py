import json
import zipfile
from os.path import join, dirname
from shutil import copyfile
from unittest import TestCase
from unittest.mock import patch

from click.testing import CliRunner

from gameta.context import GametaContext
from gameta.tags import add, delete


class TestTagsAdd(TestCase):
    def setUp(self) -> None:
        self.runner = CliRunner()
        self.add = add

    @patch('gameta.cli.click.Context.ensure_object')
    def test_tags_add_key_parameters_not_provided(self, mock_ensure_object):
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
    def test_tags_add_empty_meta_file(self, mock_ensure_object):
        params = {
            'name': 'GitPython',
            'tags': ['a', 'b', 'c']
        }
        with self.runner.isolated_filesystem() as f:
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'git.zip'), 'r') as template:
                template.extractall(f)
            with open(join(f, '.meta'), 'w+') as m:
                json.dump({
                    'repositories': {}
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

    @patch('gameta.cli.click.Context.ensure_object')
    def test_tags_add_tags_to_nonexistent_repository(self, mock_ensure_object):
        params = {
            'name': 'GitPython',
            'tags': ['a', 'b', 'c']
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

    @patch('gameta.cli.click.Context.ensure_object')
    def test_tags_add_no_tags_initially(self, mock_ensure_object):
        params = {
            'name': 'GitPython',
            'tags': ['a', 'b', 'c']
        }
        with self.runner.isolated_filesystem() as f:
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'git.zip'), 'r') as template:
                template.extractall(f)
            with open(join(dirname(__file__), 'data', '.meta'), 'r') as m1:
                output = json.load(m1)
                with open(join(f, '.meta'), 'w+') as m2:
                    output['repositories']['GitPython'] = {
                        "url": 'https://github.com/gitpython-developers/GitPython.git',
                        'path': 'GitPython',
                        '__metarepo__': False
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
                        "repositories": {
                            "gameta": {
                                "path": ".",
                                "tags": ["metarepo"],
                                "url": "git@github.com:genius-systems/gameta.git",
                                '__metarepo__': True
                            },
                            'GitPython': {
                                "url": 'https://github.com/gitpython-developers/GitPython.git',
                                'path': 'GitPython',
                                'tags': ['a', 'b', 'c'],
                                '__metarepo__': False
                            }
                        }
                    }
                )

    @patch('gameta.cli.click.Context.ensure_object')
    def test_tags_add_disjoint_set_of_tags(self, mock_ensure_object):
        params = {
            'name': 'GitPython',
            'tags': ['a', 'b', 'c']
        }
        with self.runner.isolated_filesystem() as f:
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'git.zip'), 'r') as template:
                template.extractall(f)
            with open(join(dirname(__file__), 'data', '.meta'), 'r') as m1:
                output = json.load(m1)
                with open(join(f, '.meta'), 'w+') as m2:
                    output['repositories']['GitPython'] = {
                        "url": 'https://github.com/gitpython-developers/GitPython.git',
                        'path': 'GitPython',
                        'tags': ['d', 'e', 'f'],
                        '__metarepo__': False
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
                        "repositories": {
                            "gameta": {
                                "path": ".",
                                "tags": ["metarepo"],
                                "url": "git@github.com:genius-systems/gameta.git",
                                '__metarepo__': True
                            },
                            'GitPython': {
                                "url": 'https://github.com/gitpython-developers/GitPython.git',
                                'path': 'GitPython',
                                'tags': ['a', 'b', 'c', 'd', 'e', 'f'],
                                '__metarepo__': False
                            }
                        }
                    }
                )

    @patch('gameta.cli.click.Context.ensure_object')
    def test_tags_add_duplicate_tags(self, mock_ensure_object):
        params = {
            'name': 'GitPython',
            'tags': ['a', 'b', 'c']
        }
        with self.runner.isolated_filesystem() as f:
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'git.zip'), 'r') as template:
                template.extractall(f)
            with open(join(dirname(__file__), 'data', '.meta'), 'r') as m1:
                output = json.load(m1)
                with open(join(f, '.meta'), 'w+') as m2:
                    output['repositories']['GitPython'] = {
                        "url": 'https://github.com/gitpython-developers/GitPython.git',
                        'path': 'GitPython',
                        'tags': ['c', 'b', 'f'],
                        '__metarepo__': False
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
                        "repositories": {
                            "gameta": {
                                "path": ".",
                                "tags": ["metarepo"],
                                "url": "git@github.com:genius-systems/gameta.git",
                                '__metarepo__': True
                            },
                            'GitPython': {
                                "url": 'https://github.com/gitpython-developers/GitPython.git',
                                'path': 'GitPython',
                                'tags': ['a', 'b', 'c', 'f'],
                                '__metarepo__': False
                            }
                        }
                    }
                )


class TestTagsDelete(TestCase):
    def setUp(self) -> None:
        self.runner = CliRunner()
        self.delete = delete

    @patch('gameta.cli.click.Context.ensure_object')
    def test_tags_delete_key_parameters_not_provided(self, mock_ensure_object):
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
    def test_tags_delete_empty_meta_file(self, mock_ensure_object):
        params = {
            'name': 'GitPython',
            'tags': ['a', 'b', 'c']
        }
        with self.runner.isolated_filesystem() as f:
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'git.zip'), 'r') as template:
                template.extractall(f)
            with open(join(f, '.meta'), 'w+') as m:
                json.dump({
                    'repositories': {}
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

    @patch('gameta.cli.click.Context.ensure_object')
    def test_tags_delete_tags_from_nonexistent_repository(self, mock_ensure_object):
        params = {
            'name': 'GitPython',
            'tags': ['a', 'b', 'c']
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

    @patch('gameta.cli.click.Context.ensure_object')
    def test_tags_delete_no_tags(self, mock_ensure_object):
        params = {
            'name': 'GitPython',
            'tags': ['a', 'b', 'c']
        }
        with self.runner.isolated_filesystem() as f:
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'git.zip'), 'r') as template:
                template.extractall(f)
            with open(join(dirname(__file__), 'data', '.meta'), 'r') as m1:
                output = json.load(m1)
                with open(join(f, '.meta'), 'w+') as m2:
                    output['repositories']['GitPython'] = {
                        "url": 'https://github.com/gitpython-developers/GitPython.git',
                        'path': 'GitPython',
                        '__metarepo__': False
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
                        "repositories": {
                            "gameta": {
                                "path": ".",
                                "tags": ["metarepo"],
                                "url": "git@github.com:genius-systems/gameta.git",
                                '__metarepo__': True
                            },
                            'GitPython': {
                                "url": 'https://github.com/gitpython-developers/GitPython.git',
                                'path': 'GitPython',
                                'tags': [],
                                '__metarepo__': False
                            }
                        }
                    }
                )

    @patch('gameta.cli.click.Context.ensure_object')
    def test_tags_delete_disjoint_set_of_tags(self, mock_ensure_object):
        params = {
            'name': 'GitPython',
            'tags': ['a', 'b', 'c']
        }
        with self.runner.isolated_filesystem() as f:
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'git.zip'), 'r') as template:
                template.extractall(f)
            with open(join(dirname(__file__), 'data', '.meta'), 'r') as m1:
                output = json.load(m1)
                with open(join(f, '.meta'), 'w+') as m2:
                    output['repositories']['GitPython'] = {
                        "url": 'https://github.com/gitpython-developers/GitPython.git',
                        'path': 'GitPython',
                        'tags': ['d', 'e', 'f'],
                        '__metarepo__': False
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
                        "repositories": {
                            "gameta": {
                                "path": ".",
                                "tags": ["metarepo"],
                                "url": "git@github.com:genius-systems/gameta.git",
                                '__metarepo__': True
                            },
                            'GitPython': {
                                "url": 'https://github.com/gitpython-developers/GitPython.git',
                                'path': 'GitPython',
                                'tags': ['d', 'e', 'f'],
                                '__metarepo__': False
                            }
                        }
                    }
                )

    @patch('gameta.cli.click.Context.ensure_object')
    def test_tags_delete_duplicate_tags(self, mock_ensure_object):
        params = {
            'name': 'GitPython',
            'tags': ['a', 'b', 'c']
        }
        with self.runner.isolated_filesystem() as f:
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'git.zip'), 'r') as template:
                template.extractall(f)
            with open(join(dirname(__file__), 'data', '.meta'), 'r') as m1:
                output = json.load(m1)
                with open(join(f, '.meta'), 'w+') as m2:
                    output['repositories']['GitPython'] = {
                        "url": 'https://github.com/gitpython-developers/GitPython.git',
                        'path': 'GitPython',
                        'tags': ['c', 'b', 'f'],
                        '__metarepo__': False
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
                        "repositories": {
                            "gameta": {
                                "path": ".",
                                "tags": ["metarepo"],
                                "url": "git@github.com:genius-systems/gameta.git",
                                '__metarepo__': True
                            },
                            'GitPython': {
                                "url": 'https://github.com/gitpython-developers/GitPython.git',
                                'path': 'GitPython',
                                'tags': ['f'],
                                '__metarepo__': False
                            }
                        }
                    }
                )

    @patch('gameta.cli.click.Context.ensure_object')
    def test_tags_delete_attempt_to_delete_metarepo_tag(self, mock_ensure_object):
        params = {
            'name': 'gameta',
            'tags': ['metarepo', 'b', 'c']
        }
        with self.runner.isolated_filesystem() as f:
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'git.zip'), 'r') as template:
                template.extractall(f)
            with open(join(dirname(__file__), 'data', '.meta'), 'r') as m1:
                output = json.load(m1)
                with open(join(f, '.meta'), 'w+') as m2:
                    output['repositories']['gameta'].update({
                        'tags': ['metarepo', 'a', 'b', 'c']
                    })
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
                "Unable to delete the metarepo tag from metarepo, removing it before deleting other tags\n"
                f"Successfully deleted tags from repository {params['name']}\n"
            )
            with open(join(f, '.meta'), 'r') as m:
                self.assertCountEqual(
                    json.load(m),
                    {
                        "repositories": {
                            "gameta": {
                                "path": ".",
                                "tags": ["metarepo", "a"],
                                "url": "git@github.com:genius-systems/gameta.git",
                                '__metarepo__': True
                            }
                        }
                    }
                )

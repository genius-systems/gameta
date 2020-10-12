import zipfile
from os import getenv
from os.path import join, dirname
from shutil import copyfile, copytree
from unittest import TestCase
from unittest.mock import patch

from click import Context
from click.testing import CliRunner
from gameta import GametaContext

from gameta.apply import apply


class TestApply(TestCase):
    def setUp(self) -> None:
        self.runner = CliRunner()
        self.apply = apply

    @patch('gameta.click.BaseCommand.make_context')
    def test_apply_command_to_all_repositories(self, mock_context):
        with self.runner.isolated_filesystem() as f:
            copytree(join(dirname(dirname(__file__)), '.git'), join(f, '.git'))
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'gitpython.zip'), 'r') as template:
                template.extractall(f)
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'gitdb.zip'), 'r') as template:
                template.extractall(join(f, 'core'))
            copyfile(join(dirname(__file__), 'data', '.meta_other_repos'), join(f, '.meta'))
            context = Context(self.apply, obj=GametaContext())
            context.params = {
                'command': 'git fetch --all --tags --prune',
                'tags': [],
                'repositories': [],
                'shell': False,
                'raise_errors': False
            }
            context.obj.project_dir = f
            context.obj.load()
            mock_context.return_value = context
            result = self.runner.invoke(self.apply)
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                "Applying 'git fetch --all --tags --prune' to repos ['gameta', 'GitPython', 'gitdb']\n"
                "Executing git fetch --all --tags --prune in gameta\n"
                "Executing git fetch --all --tags --prune in GitPython\n"
                "Executing git fetch --all --tags --prune in gitdb\n"
            )

    @patch('gameta.click.BaseCommand.make_context')
    def test_apply_command_to_tagged_repositories(self, mock_context):
        with self.runner.isolated_filesystem() as f:
            copytree(join(dirname(dirname(__file__)), '.git'), join(f, '.git'))
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'gitpython.zip'), 'r') as template:
                template.extractall(f)
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'gitdb.zip'), 'r') as template:
                template.extractall(join(f, 'core'))
            copyfile(join(dirname(__file__), 'data', '.meta_other_repos'), join(f, '.meta'))
            context = Context(self.apply, obj=GametaContext())
            context.params = {
                'command': 'git fetch --all --tags --prune',
                'tags': ['c'],
                'repositories': [],
                'shell': False,
                'raise_errors': False
            }
            context.obj.project_dir = f
            context.obj.load()
            mock_context.return_value = context
            result = self.runner.invoke(self.apply)
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                "Applying 'git fetch --all --tags --prune' to repos ['GitPython', 'gitdb']\n"
                "Executing git fetch --all --tags --prune in GitPython\n"
                "Executing git fetch --all --tags --prune in gitdb\n"
            )

    @patch('gameta.click.BaseCommand.make_context')
    def test_apply_command_to_tagged_repositories_that_do_not_exist(self, mock_context):
        with self.runner.isolated_filesystem() as f:
            copytree(join(dirname(dirname(__file__)), '.git'), join(f, '.git'))
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'gitpython.zip'), 'r') as template:
                template.extractall(f)
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'gitdb.zip'), 'r') as template:
                template.extractall(join(f, 'core'))
            copyfile(join(dirname(__file__), 'data', '.meta_other_repos'), join(f, '.meta'))
            context = Context(self.apply, obj=GametaContext())
            context.params = {
                'command': 'git fetch --all --tags --prune',
                'tags': ['hello', 'world'],
                'repositories': [],
                'shell': False,
                'raise_errors': False
            }
            context.obj.project_dir = f
            context.obj.load()
            mock_context.return_value = context
            result = self.runner.invoke(self.apply)
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                "Applying 'git fetch --all --tags --prune' to repos ['gameta', 'GitPython', 'gitdb']\n"
                "Executing git fetch --all --tags --prune in gameta\n"
                "Executing git fetch --all --tags --prune in GitPython\n"
                "Executing git fetch --all --tags --prune in gitdb\n"
            )

    @patch('gameta.click.BaseCommand.make_context')
    def test_apply_command_to_specified_repositories(self, mock_context):
        with self.runner.isolated_filesystem() as f:
            copytree(join(dirname(dirname(__file__)), '.git'), join(f, '.git'))
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'gitpython.zip'), 'r') as template:
                template.extractall(f)
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'gitdb.zip'), 'r') as template:
                template.extractall(join(f, 'core'))
            copyfile(join(dirname(__file__), 'data', '.meta_other_repos'), join(f, '.meta'))
            context = Context(self.apply, obj=GametaContext())
            context.params = {
                'command': 'git fetch --all --tags --prune',
                'tags': [],
                'repositories': ['GitPython'],
                'shell': False,
                'raise_errors': False
            }
            context.obj.project_dir = f
            context.obj.load()
            mock_context.return_value = context
            result = self.runner.invoke(self.apply)
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                "Applying 'git fetch --all --tags --prune' to repos ['GitPython']\n"
                "Executing git fetch --all --tags --prune in GitPython\n"
            )

    @patch('gameta.click.BaseCommand.make_context')
    def test_apply_command_to_specified_repositories_that_do_not_exist(self, mock_context):
        with self.runner.isolated_filesystem() as f:
            copytree(join(dirname(dirname(__file__)), '.git'), join(f, '.git'))
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'gitpython.zip'), 'r') as template:
                template.extractall(f)
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'gitdb.zip'), 'r') as template:
                template.extractall(join(f, 'core'))
            copyfile(join(dirname(__file__), 'data', '.meta_other_repos'), join(f, '.meta'))
            context = Context(self.apply, obj=GametaContext())
            context.params = {
                'command': 'git fetch --all --tags --prune',
                'tags': [],
                'repositories': ['hello', 'world'],
                'shell': False,
                'raise_errors': False
            }
            context.obj.project_dir = f
            context.obj.load()
            mock_context.return_value = context
            result = self.runner.invoke(self.apply)
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                "Applying 'git fetch --all --tags --prune' to repos ['gameta', 'GitPython', 'gitdb']\n"
                "Executing git fetch --all --tags --prune in gameta\n"
                "Executing git fetch --all --tags --prune in GitPython\n"
                "Executing git fetch --all --tags --prune in gitdb\n"
            )

    @patch('gameta.click.BaseCommand.make_context')
    def test_apply_command_to_merged_tags_and_repos(self, mock_context):
        with self.runner.isolated_filesystem() as f:
            copytree(join(dirname(dirname(__file__)), '.git'), join(f, '.git'))
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'gitpython.zip'), 'r') as template:
                template.extractall(f)
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'gitdb.zip'), 'r') as template:
                template.extractall(join(f, 'core'))
            copyfile(join(dirname(__file__), 'data', '.meta_other_repos'), join(f, '.meta'))
            context = Context(self.apply, obj=GametaContext())
            context.params = {
                'command': 'git fetch --all --tags --prune',
                'tags': ['metarepo'],
                'repositories': ['gitdb'],
                'shell': False,
                'raise_errors': False
            }
            context.obj.project_dir = f
            context.obj.load()
            mock_context.return_value = context
            result = self.runner.invoke(self.apply)
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                "Applying 'git fetch --all --tags --prune' to repos ['gameta', 'gitdb']\n"
                "Executing git fetch --all --tags --prune in gameta\n"
                "Executing git fetch --all --tags --prune in gitdb\n"
            )

    @patch('gameta.click.BaseCommand.make_context')
    def test_apply_command_in_separate_shell(self, mock_context):
        with self.runner.isolated_filesystem() as f:
            copytree(join(dirname(dirname(__file__)), '.git'), join(f, '.git'))
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'gitpython.zip'), 'r') as template:
                template.extractall(f)
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'gitdb.zip'), 'r') as template:
                template.extractall(join(f, 'core'))
            copyfile(join(dirname(__file__), 'data', '.meta_other_repos'), join(f, '.meta'))
            context = Context(self.apply, obj=GametaContext())
            context.params = {
                'command': 'git fetch --all --tags --prune',
                'tags': [],
                'repositories': [],
                'shell': True,
                'raise_errors': False
            }
            context.obj.project_dir = f
            context.obj.load()
            mock_context.return_value = context
            result = self.runner.invoke(self.apply)
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                "Applying 'git fetch --all --tags --prune' to repos ['gameta', 'GitPython', 'gitdb']\n"
                "Executing git fetch --all --tags --prune in gameta\n"
                "Executing git fetch --all --tags --prune in GitPython\n"
                "Executing git fetch --all --tags --prune in gitdb\n"
            )

    @patch('gameta.click.BaseCommand.make_context')
    def test_apply_raise_errors(self, mock_context):
        with self.runner.isolated_filesystem() as f:
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'git.zip'), 'r') as template:
                template.extractall(f)
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'gitpython.zip'), 'r') as template:
                template.extractall(f)
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'gitdb.zip'), 'r') as template:
                template.extractall(join(f, 'core'))
            copyfile(join(dirname(__file__), 'data', '.meta_other_repos'), join(f, '.meta'))
            context = Context(self.apply, obj=GametaContext())
            context.params = {
                'command': 'git fetch --all --tags --prune',
                'tags': [],
                'repositories': [],
                'shell': False,
                'raise_errors': True
            }
            context.obj.project_dir = f
            context.obj.load()
            mock_context.return_value = context
            result = self.runner.invoke(self.apply)
            self.assertEqual(result.exit_code, 1)

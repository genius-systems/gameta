import zipfile
from os.path import join, dirname
from shutil import copyfile, copytree
from unittest import TestCase
from unittest.mock import patch

from click.testing import CliRunner
from gameta import GametaContext

from gameta.apply import apply


class TestApply(TestCase):
    def setUp(self) -> None:
        self.runner = CliRunner()
        self.apply = apply

    @patch('gameta.click.Context.ensure_object')
    def test_apply_key_parameters_not_provided(self, mock_ensure_object):
        with self.runner.isolated_filesystem() as f:
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'git.zip'), 'r') as template:
                template.extractall(f)
            copyfile(join(dirname(__file__), 'data', '.meta_other_repos'), join(f, '.meta'))
            context = GametaContext()
            context.project_dir = f
            context.load()
            mock_ensure_object.return_value = context
            result = self.runner.invoke(self.apply)
            self.assertEqual(result.exit_code, 2)
            self.assertEqual(
                result.output,
                "Usage: apply [OPTIONS]\n"
                "Try 'apply --help' for help.\n"
                "\n"
                "Error: Missing option '--command' / '-c'.\n"
            )

    @patch('gameta.click.Context.ensure_object')
    def test_apply_command_to_all_repositories(self, mock_ensure_object):
        params = {
            'command': 'git fetch --all --tags --prune'
        }
        with self.runner.isolated_filesystem() as f:
            copytree(join(dirname(dirname(__file__)), '.git'), join(f, '.git'))
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'gitpython.zip'), 'r') as template:
                template.extractall(f)
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'gitdb.zip'), 'r') as template:
                template.extractall(join(f, 'core'))
            copyfile(join(dirname(__file__), 'data', '.meta_other_repos'), join(f, '.meta'))
            context = GametaContext()
            context.project_dir = f
            context.load()
            mock_ensure_object.return_value = context
            result = self.runner.invoke(self.apply, ['--command', params['command']])
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                f"Applying '{params['command']}' to repos ['gameta', 'GitPython', 'gitdb']\n"
                "Executing git fetch --all --tags --prune in gameta\n"
                "Executing git fetch --all --tags --prune in GitPython\n"
                "Executing git fetch --all --tags --prune in gitdb\n"
            )

    @patch('gameta.click.Context.ensure_object')
    def test_apply_command_to_tagged_repositories(self, mock_ensure_object):
        params = {
            'command': 'git fetch --all --tags --prune',
            'tags': ('c', )
        }
        with self.runner.isolated_filesystem() as f:
            copytree(join(dirname(dirname(__file__)), '.git'), join(f, '.git'))
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'gitpython.zip'), 'r') as template:
                template.extractall(f)
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'gitdb.zip'), 'r') as template:
                template.extractall(join(f, 'core'))
            copyfile(join(dirname(__file__), 'data', '.meta_other_repos'), join(f, '.meta'))
            context = GametaContext()
            context.project_dir = f
            context.load()
            mock_ensure_object.return_value = context
            result = self.runner.invoke(self.apply, ['--command', params['command'], '-t', params['tags'][0]])
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                f"Applying '{params['command']}' to repos ['GitPython', 'gitdb']\n"
                "Executing git fetch --all --tags --prune in GitPython\n"
                "Executing git fetch --all --tags --prune in gitdb\n"
            )

    @patch('gameta.click.Context.ensure_object')
    def test_apply_command_to_tagged_repositories_that_do_not_exist(self, mock_ensure_object):
        params = {
            'command': 'git fetch --all --tags --prune',
            'tags': ('hello', 'world')
        }
        with self.runner.isolated_filesystem() as f:
            copytree(join(dirname(dirname(__file__)), '.git'), join(f, '.git'))
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'gitpython.zip'), 'r') as template:
                template.extractall(f)
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'gitdb.zip'), 'r') as template:
                template.extractall(join(f, 'core'))
            copyfile(join(dirname(__file__), 'data', '.meta_other_repos'), join(f, '.meta'))
            context = GametaContext()
            context.project_dir = f
            context.load()
            mock_ensure_object.return_value = context
            result = self.runner.invoke(
                self.apply, ['--command', params['command'], '-t', params['tags'][0], '-t', params['tags'][1]]
            )
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                f"Applying '{params['command']}' to repos ['gameta', 'GitPython', 'gitdb']\n"
                "Executing git fetch --all --tags --prune in gameta\n"
                "Executing git fetch --all --tags --prune in GitPython\n"
                "Executing git fetch --all --tags --prune in gitdb\n"
            )

    @patch('gameta.click.Context.ensure_object')
    def test_apply_command_to_specified_repositories(self, mock_ensure_object):
        params = {
            'command': 'git fetch --all --tags --prune',
            'repositories': ('GitPython', )
        }
        with self.runner.isolated_filesystem() as f:
            copytree(join(dirname(dirname(__file__)), '.git'), join(f, '.git'))
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'gitpython.zip'), 'r') as template:
                template.extractall(f)
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'gitdb.zip'), 'r') as template:
                template.extractall(join(f, 'core'))
            copyfile(join(dirname(__file__), 'data', '.meta_other_repos'), join(f, '.meta'))
            context = GametaContext()
            context.project_dir = f
            context.load()
            mock_ensure_object.return_value = context
            result = self.runner.invoke(self.apply, ['--command', params['command'], '-r', params['repositories'][0]])
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                f"Applying '{params['command']}' to repos ['GitPython']\n"
                "Executing git fetch --all --tags --prune in GitPython\n"
            )

    @patch('gameta.click.Context.ensure_object')
    def test_apply_command_to_specified_repositories_that_do_not_exist(self, mock_ensure_object):
        params = {
            'command': 'git fetch --all --tags --prune',
            'repositories': ('hello', 'world')
        }
        with self.runner.isolated_filesystem() as f:
            copytree(join(dirname(dirname(__file__)), '.git'), join(f, '.git'))
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'gitpython.zip'), 'r') as template:
                template.extractall(f)
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'gitdb.zip'), 'r') as template:
                template.extractall(join(f, 'core'))
            copyfile(join(dirname(__file__), 'data', '.meta_other_repos'), join(f, '.meta'))
            context = GametaContext()
            context.project_dir = f
            context.load()
            mock_ensure_object.return_value = context
            result = self.runner.invoke(
                self.apply,
                ['--command', params['command'], '-r', params['repositories'][0], '-r', params['repositories'][1]]
            )
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                f"Applying '{params['command']}' to repos ['gameta', 'GitPython', 'gitdb']\n"
                "Executing git fetch --all --tags --prune in gameta\n"
                "Executing git fetch --all --tags --prune in GitPython\n"
                "Executing git fetch --all --tags --prune in gitdb\n"
            )

    @patch('gameta.click.Context.ensure_object')
    def test_apply_command_to_merged_tags_and_repos(self, mock_ensure_object):
        params = {
            'command': 'git fetch --all --tags --prune',
            'tags': ('metarepo', ),
            'repositories': ('gitdb', )
        }
        with self.runner.isolated_filesystem() as f:
            copytree(join(dirname(dirname(__file__)), '.git'), join(f, '.git'))
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'gitpython.zip'), 'r') as template:
                template.extractall(f)
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'gitdb.zip'), 'r') as template:
                template.extractall(join(f, 'core'))
            copyfile(join(dirname(__file__), 'data', '.meta_other_repos'), join(f, '.meta'))
            context = GametaContext()
            context.project_dir = f
            context.load()
            mock_ensure_object.return_value = context
            result = self.runner.invoke(
                self.apply, ['--command', params['command'], '-t', params['tags'][0], '-r', params['repositories'][0]]
            )
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                f"Applying '{params['command']}' to repos ['gameta', 'gitdb']\n"
                "Executing git fetch --all --tags --prune in gameta\n"
                "Executing git fetch --all --tags --prune in gitdb\n"
            )

    @patch('gameta.click.Context.ensure_object')
    def test_apply_command_in_separate_shell(self, mock_ensure_object):
        params = {
            'command': 'git fetch --all --tags --prune',
        }
        with self.runner.isolated_filesystem() as f:
            copytree(join(dirname(dirname(__file__)), '.git'), join(f, '.git'))
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'gitpython.zip'), 'r') as template:
                template.extractall(f)
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'gitdb.zip'), 'r') as template:
                template.extractall(join(f, 'core'))
            copyfile(join(dirname(__file__), 'data', '.meta_other_repos'), join(f, '.meta'))
            context = GametaContext()
            context.project_dir = f
            context.load()
            mock_ensure_object.return_value = context
            result = self.runner.invoke(self.apply, ['--command', params['command'], '-s'])
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                f"Applying '{params['command']}' to repos ['gameta', 'GitPython', 'gitdb'] in a separate shell\n"
                "Executing git fetch --all --tags --prune in gameta\n"
                "Executing git fetch --all --tags --prune in GitPython\n"
                "Executing git fetch --all --tags --prune in gitdb\n"
            )

    @patch('gameta.click.Context.ensure_object')
    def test_apply_raise_errors(self, mock_ensure_object):
        params = {
            'command': 'git fetch --all --tags --prune'
        }
        with self.runner.isolated_filesystem() as f:
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'git.zip'), 'r') as template:
                template.extractall(f)
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'gitpython.zip'), 'r') as template:
                template.extractall(f)
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'gitdb.zip'), 'r') as template:
                template.extractall(join(f, 'core'))
            copyfile(join(dirname(__file__), 'data', '.meta_other_repos'), join(f, '.meta'))
            context = GametaContext()
            context.project_dir = f
            context.load()
            mock_ensure_object.return_value = context
            result = self.runner.invoke(self.apply, ['--command', params['command'], '-e'])
            self.assertEqual(result.exit_code, 1)

    @patch('gameta.click.Context.ensure_object')
    def test_apply_verbose(self, mock_ensure_object):
        params = {
            'command': 'git fetch --all --tags --prune'
        }
        with self.runner.isolated_filesystem() as f:
            copytree(join(dirname(dirname(__file__)), '.git'), join(f, '.git'))
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'gitpython.zip'), 'r') as template:
                template.extractall(f)
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'gitdb.zip'), 'r') as template:
                template.extractall(join(f, 'core'))
            copyfile(join(dirname(__file__), 'data', '.meta_other_repos'), join(f, '.meta'))
            context = GametaContext()
            context.project_dir = f
            context.load()
            mock_ensure_object.return_value = context
            result = self.runner.invoke(self.apply, ['--command', params['command'], '-v'])
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                f"Applying '{params['command']}' to repos ['gameta', 'GitPython', 'gitdb']\n"
                "Executing git fetch --all --tags --prune in gameta\n"
                "Fetching origin\n"
                "\n"
                "Executing git fetch --all --tags --prune in GitPython\n"
                "Fetching origin\n"
                "\n"
                "Executing git fetch --all --tags --prune in gitdb\n"
                "Fetching origin\n"
                "\n"
            )

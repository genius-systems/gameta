import json
import zipfile
from os.path import join, dirname
from shutil import copyfile, copytree
from unittest import TestCase
from unittest.mock import patch

from click.testing import CliRunner

from gameta.context import GametaContext, SHELL
from gameta.apply import apply


class TestApply(TestCase):
    def setUp(self) -> None:
        self.runner = CliRunner()
        self.apply = apply

    @patch('gameta.cli.click.Context.ensure_object')
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

    @patch('gameta.cli.click.Context.ensure_object')
    def test_apply_command_to_all_repositories(self, mock_ensure_object):
        params = {
            'commands': ('git fetch --all --tags --prune', ),
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
            result = self.runner.invoke(self.apply, ['--command', params['commands'][0]])
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                f"Applying '{params['commands']}' to repos ['gameta', 'GitPython', 'gitdb']\n"
                "Executing git fetch --all --tags --prune in gameta\n"
                "Executing git fetch --all --tags --prune in GitPython\n"
                "Executing git fetch --all --tags --prune in gitdb\n"
            )

    @patch('gameta.cli.click.Context.ensure_object')
    def test_apply_multiple_commands_to_all_repositories(self, mock_ensure_object):
        params = {
            'commands': (
                'git fetch --all --tags --prune origin',
                'git checkout {branch}'
            )
        }
        with self.runner.isolated_filesystem() as f:
            copytree(join(dirname(dirname(__file__)), '.git'), join(f, '.git'))
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'gitpython.zip'), 'r') as template:
                template.extractall(f)
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'gitdb.zip'), 'r') as template:
                template.extractall(join(f, 'core'))
            with open(join(dirname(__file__), 'data', '.meta_other_repos'), 'r') as m1:
                output = json.load(m1)
                with open(join(f, '.meta'), 'w+') as m2:
                    output['projects']['gameta'].update({"branch": "master"})
                    output['projects']['gitdb'].update({'branch': 'gitdb2'})
                    output['projects']['GitPython'].update({'branch': 'py2'})
                    json.dump(output, m2)
            context = GametaContext()
            context.project_dir = f
            context.load()
            mock_ensure_object.return_value = context
            result = self.runner.invoke(
                self.apply, ['--command', params['commands'][0], '--command', params['commands'][1], '-v']
            )
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                f"Applying '{params['commands']}' to repos ['gameta', 'GitPython', 'gitdb']\n"
                "Executing git fetch --all --tags --prune in gameta\n"
                "Executing git fetch --all --tags --prune in GitPython\n"
                "Executing git fetch --all --tags --prune in gitdb\n"
            )

    @patch('gameta.cli.click.Context.ensure_object')
    def test_apply_command_to_tagged_repositories(self, mock_ensure_object):
        params = {
            'commands': ('git fetch --all --tags --prune', ),
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
            result = self.runner.invoke(self.apply, ['--command', params['commands'][0], '-t', params['tags'][0]])
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                f"Applying '{params['commands']}' to repos ['GitPython', 'gitdb']\n"
                "Executing git fetch --all --tags --prune in GitPython\n"
                "Executing git fetch --all --tags --prune in gitdb\n"
            )

    @patch('gameta.cli.click.Context.ensure_object')
    def test_apply_command_to_tagged_repositories_that_do_not_exist(self, mock_ensure_object):
        params = {
            'commands': ('git fetch --all --tags --prune', ),
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
                self.apply, ['--command', params['commands'][0], '-t', params['tags'][0], '-t', params['tags'][1]]
            )
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                f"Applying '{params['commands']}' to repos ['gameta', 'GitPython', 'gitdb']\n"
                "Executing git fetch --all --tags --prune in gameta\n"
                "Executing git fetch --all --tags --prune in GitPython\n"
                "Executing git fetch --all --tags --prune in gitdb\n"
            )

    @patch('gameta.cli.click.Context.ensure_object')
    def test_apply_command_to_specified_repositories(self, mock_ensure_object):
        params = {
            'commands': ('git fetch --all --tags --prune', ),
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
            result = self.runner.invoke(
                self.apply, ['--command', params['commands'][0], '-r', params['repositories'][0]]
            )
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                f"Applying '{params['commands']}' to repos ['GitPython']\n"
                "Executing git fetch --all --tags --prune in GitPython\n"
            )

    @patch('gameta.cli.click.Context.ensure_object')
    def test_apply_command_to_specified_repositories_that_do_not_exist(self, mock_ensure_object):
        params = {
            'commands': ('git fetch --all --tags --prune', ),
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
                ['--command', params['commands'][0], '-r', params['repositories'][0], '-r', params['repositories'][1]]
            )
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                f"Applying '{params['commands']}' to repos ['gameta', 'GitPython', 'gitdb']\n"
                "Executing git fetch --all --tags --prune in gameta\n"
                "Executing git fetch --all --tags --prune in GitPython\n"
                "Executing git fetch --all --tags --prune in gitdb\n"
            )

    @patch('gameta.cli.click.Context.ensure_object')
    def test_apply_command_to_merged_tags_and_repos(self, mock_ensure_object):
        params = {
            'commands': ('git fetch --all --tags --prune', ),
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
                self.apply,
                ['--command', params['commands'][0], '-t', params['tags'][0], '-r', params['repositories'][0]]
            )
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                f"Applying '{params['commands']}' to repos ['gameta', 'gitdb']\n"
                "Executing git fetch --all --tags --prune in gameta\n"
                "Executing git fetch --all --tags --prune in gitdb\n"
            )

    @patch('gameta.cli.click.Context.ensure_object')
    def test_apply_command_in_separate_shell(self, mock_ensure_object):
        params = {
            'commands': ('git fetch --all --tags --prune', ),
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
            result = self.runner.invoke(self.apply, ['--command', params['commands'][0], '-s'])
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                f"Applying '{params['commands']}' to repos ['gameta', 'GitPython', 'gitdb'] in a separate shell\n"
                f"Executing {SHELL} -c  git fetch --all --tags --prune in gameta\n"
                f"Executing {SHELL} -c  git fetch --all --tags --prune in GitPython\n"
                f"Executing {SHELL} -c  git fetch --all --tags --prune in gitdb\n"
            )

    @patch('gameta.cli.click.Context.ensure_object')
    def test_apply_raise_errors(self, mock_ensure_object):
        params = {
            'commands': ('git fetch --all --tags --prune', )
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
            result = self.runner.invoke(self.apply, ['--command', params['commands'][0], '-e'])
            self.assertEqual(result.exit_code, 1)

    @patch('gameta.cli.click.Context.ensure_object')
    def test_apply_verbose(self, mock_ensure_object):
        params = {
            'commands': ('git fetch --all --tags --prune', )
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
            result = self.runner.invoke(self.apply, ['--command', params['commands'][0], '-v'])
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                f"Applying '{params['commands']}' to repos ['gameta', 'GitPython', 'gitdb']\n"
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

import json
import zipfile
from os.path import join, dirname, basename
from shutil import copyfile

from unittest import TestCase
from unittest.mock import patch

from click import Context
from click.testing import CliRunner

from gameta import GametaContext
from gameta.init import init


class TestInit(TestCase):
    def setUp(self) -> None:
        self.runner = CliRunner()
        self.init = init

    @patch('gameta.click.BaseCommand.make_context')
    def test_init_with_default_values_folder_is_not_a_git_repo(self, mock_context):
        with self.runner.isolated_filesystem() as f:
            context = Context(self.init, obj=GametaContext())
            context.params = {'overwrite': False, 'git': False}
            context.obj.project_dir = f
            mock_context.return_value = context
            result = self.runner.invoke(self.init)
            self.assertEqual(result.exit_code, 1)
            self.assertEqual(
                result.output,
                f'Initialising metarepo in {f}\n'
                f"Error: {f} is not a valid git repo, initialise it with -g flag\n"
            )

    @patch('gameta.click.BaseCommand.make_context')
    def test_init_with_git_is_true_folder_is_not_a_git_repo(self, mock_context):
        with self.runner.isolated_filesystem() as f:
            context = Context(self.init, obj=GametaContext())
            context.params = {'overwrite': False, 'git': True}
            context.obj.project_dir = f
            mock_context.return_value = context
            result = self.runner.invoke(self.init)
            print(result.output)
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                f'Initialising metarepo in {f}\n'
                f'Initialising {f} as a git repository\n'
                f'Successfully initialised {basename(f)} as a metarepo\n'
            )
            with open(join(f, '.meta'), 'r') as m:
                self.assertEqual(
                    json.load(m),
                    {
                        'projects': {
                            basename(f): {
                                'path': '.',
                                'tags': ['meta'],
                                'url': None
                            }
                        }
                    }
                )

    @patch('gameta.click.BaseCommand.make_context')
    def test_init_with_default_values_folder_is_a_git_repo(self, mock_context):
        with self.runner.isolated_filesystem() as f:
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'git.zip'), 'r') as template:
                template.extractall(f)
            context = Context(self.init, obj=GametaContext())
            context.params = {'overwrite': False, 'git': False}
            context.obj.project_dir = f
            mock_context.return_value = context
            result = self.runner.invoke(self.init)
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                f'Initialising metarepo in {f}\n'
                f"Successfully initialised gameta as a metarepo\n"
            )
            with open(join(f, '.meta'), 'r') as m:
                self.assertEqual(
                    json.load(m),
                    {
                        'projects': {
                            'gameta': {
                                'path': '.',
                                'tags': ['meta'],
                                'url': 'git@github.com:genius-systems/gameta.git'
                            }
                        }
                    }
                )

    @patch('gameta.click.BaseCommand.make_context')
    def test_init_with_default_values_folder_is_a_metarepo(self, mock_context):
        with self.runner.isolated_filesystem() as f:
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'git.zip'), 'r') as template:
                template.extractall(f)
            copyfile(join(dirname(__file__), 'data', '.meta'), join(f, '.meta'))
            context = Context(self.init, obj=GametaContext())
            context.params = {'overwrite': False, 'git': False}
            context.obj.project_dir = f
            context.obj.load()
            mock_context.return_value = context
            result = self.runner.invoke(self.init)
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                f'Initialising metarepo in {f}\n'
                f"{f} is a metarepo, ignoring\n"
            )
            with open(join(f, '.meta'), 'r') as m:
                self.assertEqual(
                    json.load(m),
                    {
                        'projects': {
                            'gameta': {
                                'path': '.',
                                'tags': ['meta'],
                                'url': 'git@github.com:genius-systems/gameta.git'
                            }
                        }
                    }
                )

    @patch('gameta.click.BaseCommand.make_context')
    def test_init_with_overwrite_folder_is_a_metarepo(self, mock_context):
        with self.runner.isolated_filesystem() as f:
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'git.zip'), 'r') as template:
                template.extractall(f)
            copyfile(join(dirname(__file__), 'data', '.meta'), join(f, '.meta'))
            context = Context(self.init, obj=GametaContext())
            context.params = {'overwrite': True, 'git': False}
            context.obj.project_dir = f
            context.obj.load()
            mock_context.return_value = context
            result = self.runner.invoke(self.init)
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                f'Initialising metarepo in {f}\n'
                f"Successfully initialised gameta as a metarepo\n"
            )
            with open(join(f, '.meta'), 'r') as m:
                self.assertEqual(
                    json.load(m),
                    {
                        'projects': {
                            'gameta': {
                                'path': '.',
                                'tags': ['meta'],
                                'url': 'git@github.com:genius-systems/gameta.git'
                            }
                        }
                    }
                )

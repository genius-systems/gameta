import json
import zipfile
from os.path import join, dirname, basename
from shutil import copyfile

from unittest import TestCase
from unittest.mock import patch

from click.testing import CliRunner

from gameta import __version__
from gameta.base import GametaContext
from gameta.init import init


class TestInit(TestCase):
    def setUp(self) -> None:
        self.runner = CliRunner()
        self.init = init

    @patch('gameta.cli.click.Context.ensure_object')
    def test_init_with_default_values_folder_is_not_a_git_repo(self, mock_ensure_object):
        with self.runner.isolated_filesystem() as f:
            context = GametaContext()
            context.project_dir = f
            mock_ensure_object.return_value = context
            result = self.runner.invoke(self.init)
            self.assertEqual(result.exit_code, 1)
            self.assertEqual(
                result.output,
                f'Initialising metarepo in {f}\n'
                f"Error: {f} is not a valid git repo, initialise it with -g flag\n"
            )

    @patch('gameta.cli.click.Context.ensure_object')
    def test_init_with_git_folder_is_not_a_git_repo(self, mock_ensure_object):
        with self.runner.isolated_filesystem() as f:
            context = GametaContext()
            context.project_dir = f
            mock_ensure_object.return_value = context
            result = self.runner.invoke(self.init, ['--git'])
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                f'Initialising metarepo in {f}\n'
                f'Initialising {f} as a git repository\n'
                f'Successfully initialised {basename(f)} as a metarepo\n'
            )
            with open(join(f, '.gameta'), 'r') as m:
                self.assertEqual(
                    json.load(m),
                    {
                        "version": __version__,
                        'repositories': {
                            basename(f): {
                                'path': '.',
                                'tags': ['metarepo'],
                                'url': None,
                                '__metarepo__': True
                            }
                        }
                    }
                )

    @patch('gameta.cli.click.Context.ensure_object')
    def test_init_with_default_values_folder_is_a_git_repo(self, mock_ensure_object):
        with self.runner.isolated_filesystem() as f:
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'git.zip'), 'r') as template:
                template.extractall(f)
            context = GametaContext()
            context.project_dir = f
            context.load()
            mock_ensure_object.return_value = context
            result = self.runner.invoke(self.init)
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                f'Initialising metarepo in {f}\n'
                f"Successfully initialised gameta as a metarepo\n"
            )
            with open(join(f, '.gameta'), 'r') as m:
                self.assertEqual(
                    json.load(m),
                    {
                        "version": __version__,
                        'repositories': {
                            'gameta': {
                                'path': '.',
                                'tags': ['metarepo'],
                                'url': 'git@github.com:genius-systems/gameta.git',
                                '__metarepo__': True
                            }
                        }
                    }
                )

    @patch('gameta.cli.click.Context.ensure_object')
    def test_init_with_default_values_folder_is_a_metarepo(self, mock_ensure_object):
        with self.runner.isolated_filesystem() as f:
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'git.zip'), 'r') as template:
                template.extractall(f)
            copyfile(join(dirname(__file__), 'data', '.gameta'), join(f, '.gameta'))
            context = GametaContext()
            context.project_dir = f
            context.load()
            mock_ensure_object.return_value = context
            result = self.runner.invoke(self.init)
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                f'Initialising metarepo in {f}\n'
                f"{f} is a metarepo, ignoring\n"
            )
            with open(join(f, '.gameta'), 'r') as m:
                self.assertEqual(
                    json.load(m),
                    {
                        "version": '0.3.0',
                        'repositories': {
                            'gameta': {
                                'path': '.',
                                'tags': ['metarepo'],
                                'url': 'git@github.com:genius-systems/gameta.git',
                                '__metarepo__': True
                            }
                        }
                    }
                )

    @patch('gameta.cli.click.Context.ensure_object')
    def test_init_with_overwrite_folder_is_a_metarepo(self, mock_ensure_object):
        with self.runner.isolated_filesystem() as f:
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'git.zip'), 'r') as template:
                template.extractall(f)
            copyfile(join(dirname(__file__), 'data', '.gameta'), join(f, '.gameta'))
            context = GametaContext()
            context.project_dir = f
            context.load()
            mock_ensure_object.return_value = context
            result = self.runner.invoke(self.init, ['--overwrite'])
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                f'Initialising metarepo in {f}\n'
                f"Successfully initialised gameta as a metarepo\n"
            )
            with open(join(f, '.gameta'), 'r') as m:
                self.assertEqual(
                    json.load(m),
                    {
                        "version": '0.3.0',
                        'repositories': {
                            'gameta': {
                                'path': '.',
                                'tags': ['metarepo'],
                                'url': 'git@github.com:genius-systems/gameta.git',
                                '__metarepo__': True
                            }
                        }
                    }
                )

    @patch('gameta.cli.click.Context.ensure_object')
    def test_init_does_not_clear_gitignore_file(self, mock_ensure_object):
        with self.runner.isolated_filesystem() as f:
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'git.zip'), 'r') as template:
                template.extractall(f)
            copyfile(join(dirname(__file__), 'data', '.gitignore'), join(f, '.gitignore'))
            context = GametaContext()
            context.project_dir = f
            context.load()
            mock_ensure_object.return_value = context
            result = self.runner.invoke(self.init)
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                f'Initialising metarepo in {f}\n'
                f"Successfully initialised gameta as a metarepo\n"
            )
            with open(join(f, '.gameta'), 'r') as m:
                self.assertEqual(
                    json.load(m),
                    {
                        "version": __version__,
                        'repositories': {
                            'gameta': {
                                'path': '.',
                                'tags': ['metarepo'],
                                'url': 'git@github.com:genius-systems/gameta.git',
                                '__metarepo__': True
                            }
                        }
                    }
                )
            with open(join(f, '.gitignore'), 'r') as m1:
                with open(join(dirname(__file__), 'data', '.gitignore'), 'r') as m2:
                    self.assertEqual(m1.read(), m2.read())

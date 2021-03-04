import json
import zipfile
from os import listdir
from os.path import join, dirname, basename
from shutil import copyfile

from unittest import TestCase
from unittest.mock import patch

from click.testing import CliRunner

from gameta.context import GametaContext
from gameta.init import init, sync


class TestInit(TestCase):
    def setUp(self) -> None:
        self.maxDiff = None
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
            with open(join(f, '.meta'), 'r') as m:
                self.assertEqual(
                    json.load(m),
                    {
                        'projects': {
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
            with open(join(f, '.meta'), 'r') as m:
                self.assertEqual(
                    json.load(m),
                    {
                        'projects': {
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
            copyfile(join(dirname(__file__), 'data', '.meta'), join(f, '.meta'))
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
            with open(join(f, '.meta'), 'r') as m:
                self.assertEqual(
                    json.load(m),
                    {
                        'projects': {
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
            copyfile(join(dirname(__file__), 'data', '.meta'), join(f, '.meta'))
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
            with open(join(f, '.meta'), 'r') as m:
                self.assertEqual(
                    json.load(m),
                    {
                        'projects': {
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
            with open(join(f, '.meta'), 'r') as m:
                self.assertEqual(
                    json.load(m),
                    {
                        'projects': {
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


class TestSync(TestCase):
    def setUp(self) -> None:
        self.maxDiff = None
        self.runner = CliRunner()
        self.sync = sync

    @patch('gameta.cli.click.Context.ensure_object')
    def test_sync_empty_meta_file(self, mock_ensure_object):
        with self.runner.isolated_filesystem() as f:
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'git.zip'), 'r') as template:
                template.extractall(f)
            with open(join(f, '.meta'), 'w') as m:
                json.dump(
                    {
                        'projects': {},
                        "commands": {}
                    }, m
                )
            context = GametaContext()
            context.project_dir = f
            context.load()
            mock_ensure_object.return_value = context
            result = self.runner.invoke(self.sync)
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                f'Syncing all child repositories in metarepo {f}\n'
            )

    @patch('gameta.cli.click.Context.ensure_object')
    def test_sync_all_repos(self, mock_ensure_object):
        with self.runner.isolated_filesystem() as f:
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'git.zip'), 'r') as template:
                template.extractall(f)
            copyfile(join(dirname(__file__), 'data', '.meta_other_repos'), join(f, '.meta'))
            context = GametaContext()
            context.project_dir = f
            context.load()
            mock_ensure_object.return_value = context
            result = self.runner.invoke(self.sync)
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                f'Syncing all child repositories in metarepo {f}\n'
                'Successfully synced GitPython to GitPython\n'
                'Successfully synced gitdb to core/gitdb\n'
            )
            self.assertCountEqual(listdir(f), ['GitPython', 'core', '.git', '.meta'])
            self.assertTrue(all(i in listdir(join(f, 'GitPython')) for i in ['git', 'doc', 'test']))
            self.assertCountEqual(listdir(join(f, 'core')), ['gitdb'])
            self.assertTrue(all(i in listdir(join(f, 'core', 'gitdb')) for i in ['gitdb', 'doc', 'setup.py']))

    @patch('gameta.cli.click.Context.ensure_object')
    def test_sync_repo_already_exists(self, mock_ensure_object):
        with self.runner.isolated_filesystem() as f:
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'git.zip'), 'r') as template:
                template.extractall(f)
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'gitdb.zip'), 'r') as template:
                template.extractall(join(f, 'core'))
            copyfile(join(dirname(__file__), 'data', '.meta_other_repos'), join(f, '.meta'))
            context = GametaContext()
            context.project_dir = f
            context.load()
            mock_ensure_object.return_value = context
            result = self.runner.invoke(self.sync)
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                f'Syncing all child repositories in metarepo {f}\n'
                'Successfully synced GitPython to GitPython\n'
                "An error occurred Cmd('git') failed due to: exit code(128)\n"
                "  cmdline: git clone -v https://github.com/gitpython-developers/gitdb.git core/gitdb\n"
                "  stderr: 'fatal: destination path 'core/gitdb' already exists and is not an empty directory.\n"
                "', skipping repo\n"
            )
            self.assertCountEqual(listdir(f), ['GitPython', 'core', '.git', '.meta'])
            self.assertTrue(all(i in listdir(join(f, 'GitPython')) for i in ['git', 'doc', 'test']))
            self.assertCountEqual(listdir(join(f, 'core')), ['gitdb'])
            self.assertTrue(all(i in listdir(join(f, 'core', 'gitdb')) for i in ['gitdb', 'doc', 'setup.py']))

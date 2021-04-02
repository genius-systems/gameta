import json
import zipfile
from os import listdir
from os.path import dirname, join
from shutil import copyfile
from unittest import TestCase
from unittest.mock import patch

from click.testing import CliRunner

from gameta.base import GametaContext
from gameta.sync import sync


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
            with open(join(f, '.gameta'), 'w') as m:
                json.dump(
                    {
                        'repositories': {},
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
            copyfile(join(dirname(__file__), 'data', '.gameta_other_repos'), join(f, '.gameta'))
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
            self.assertCountEqual(listdir(f), ['GitPython', 'core', '.git', '.gameta'])
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
            copyfile(join(dirname(__file__), 'data', '.gameta_other_repos'), join(f, '.gameta'))
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
            self.assertCountEqual(listdir(f), ['GitPython', 'core', '.git', '.gameta'])
            self.assertTrue(all(i in listdir(join(f, 'GitPython')) for i in ['git', 'doc', 'test']))
            self.assertCountEqual(listdir(join(f, 'core')), ['gitdb'])
            self.assertTrue(all(i in listdir(join(f, 'core', 'gitdb')) for i in ['gitdb', 'doc', 'setup.py']))

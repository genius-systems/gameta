import zipfile
from os import getcwd
from os.path import dirname, join
from shutil import copytree
from unittest import TestCase
from unittest.mock import patch

import click
from click.testing import CliRunner

from gameta import __version__
from gameta.base import GametaContext
from gameta.cli import gameta_cli


class TestGametaCli(TestCase):
    def setUp(self) -> None:
        self.maxDiff = None
        self.runner = CliRunner()
        self.cli = gameta_cli

    @patch("gameta.cli.click.Context.ensure_object")
    def test_cli_change_project_folder(self, mock_ensure_object):
        with self.runner.isolated_filesystem() as f:
            copytree(
                join(dirname(__file__), "data", "gameta_single_repo_only"),
                join(f, "test"),
            )
            with zipfile.ZipFile(
                join(dirname(__file__), "data", "git.zip"), "r"
            ) as template:
                template.extractall(join(f, "test"))
            context = GametaContext()
            mock_ensure_object.return_value = context
            result = self.runner.invoke(self.cli, ["-d", join(f, "test")])
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(getcwd(), join(f, "test"))
            self.assertEqual(
                context.repositories,
                {
                    "gameta": {
                        "__metarepo__": True,
                        "path": ".",
                        "tags": ["metarepo"],
                        "url": "git@github.com:genius-systems/gameta.git",
                        "vcs": "git",
                    }
                },
            )

    @patch("gameta.cli.click.Context.ensure_object")
    def test_cli_project_folder_does_not_exist(self, mock_ensure_object):
        with self.runner.isolated_filesystem() as f:
            context = GametaContext()
            mock_ensure_object.return_value = context
            result = self.runner.invoke(self.cli, ["-d", join(f, "test")])
            self.assertEqual(result.exit_code, 1)
            self.assertEqual(
                result.output,
                f"Error: Project directory {join(f, 'test')} does not exist\n",
            )

    @patch("gameta.cli.click.Context.ensure_object")
    def test_cli_printing_version(self, mock_ensure_object):
        with self.runner.isolated_filesystem() as f:
            with zipfile.ZipFile(
                join(dirname(__file__), "data", "git.zip"), "r"
            ) as template:
                template.extractall(f)
            context = GametaContext()
            mock_ensure_object.return_value = context
            result = self.runner.invoke(self.cli, ["-v"])
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(result.output, f"Gameta version: {__version__}\n")

    def test_cli_all_gameta_plugins_loaded(self):
        self.assertTrue(
            isinstance(self.cli.get_command(c), click.BaseCommand)
            for c in [
                "apply",
                "cmd",
                "const",
                "exec",
                "init",
                "params",
                "repo",
                "schema",
                "sync",
                "tags",
                "venv",
            ]
        )

    def test_cli_additional_plugins_loaded(self):
        self.assertTrue(
            isinstance(self.cli.get_command(c), click.BaseCommand) for c in ["test"]
        )

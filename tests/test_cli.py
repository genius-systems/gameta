
import zipfile
from os.path import join, dirname
from unittest import TestCase
from unittest.mock import patch

from click.testing import CliRunner

from gameta.context import GametaContext
from gameta.cli import gameta_cli
from gameta import __version__


class TestGametaCli(TestCase):
    def setUp(self) -> None:
        self.maxDiff = None
        self.runner = CliRunner()
        self.cli = gameta_cli

    @patch('gameta.cli.click.Context.ensure_object')
    def test_cli_printing_version(self, mock_ensure_object):
        with self.runner.isolated_filesystem() as f:
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'git.zip'), 'r') as template:
                template.extractall(f)
            context = GametaContext()
            context.project_dir = f
            context.load()
            mock_ensure_object.return_value = context
            result = self.runner.invoke(self.cli, ["-v"])
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(result.output, f"Gameta version: {__version__}\n")

from unittest import TestCase

from click import Context
from click.testing import CliRunner
from gameta import GametaContext

from gameta.init import init


class TestInit(TestCase):
    def setUp(self) -> None:
        self.runner = CliRunner()
        self.init = init

    def test_init_with_default_values(self):
        with self.runner.isolated_filesystem() as f:
            with Context(init, obj=GametaContext()):
                print(init.invoke())

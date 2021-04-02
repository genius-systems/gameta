import json
from os import makedirs
from os.path import exists, join
from unittest import TestCase

from click.testing import CliRunner

from gameta import __version__
from gameta.base import GametaContext
from gameta.base.errors import ContextError


class TestGametaContext(TestCase):
    def setUp(self) -> None:
        self.maxDiff = None
        self.context = GametaContext()
        self.runner = CliRunner()

    def test_gameta_context_project_name_after_providing_project_dir(self):
        with self.runner.isolated_filesystem() as f:
            makedirs(join(f, "test"))
            self.context.project_dir = join(f, "test")
            self.assertEqual(self.context.project_name, "test")

    def test_gameta_context_project_name_no_project_dir(self):
        with self.runner.isolated_filesystem():
            with self.assertRaises(ContextError):
                self.context.project_name

    def test_gameta_context_gameta_points_to_gameta_file_if_provided(self):
        with self.runner.isolated_filesystem() as f:
            makedirs(join(f, ".gameta"))
            with open(join(f, ".gameta", ".gameta"), "w") as m:
                m.write("Hello world")
            self.context.init(f)
            self.assertEqual(self.context.gameta, join(f, ".gameta", ".gameta"))

    def test_gameta_context_gameta_points_to_gameta_file_if_not_provided(self):
        with self.runner.isolated_filesystem() as f:
            self.context.init(f)
            self.assertEqual(self.context.gameta, join(f, ".gameta", ".gameta"))

    def test_gameta_context_gameta_no_project_dir(self):
        with self.runner.isolated_filesystem():
            with self.assertRaises(ContextError):
                self.context.gameta

    def test_gameta_context_is_primary_metarepo(self):
        with self.runner.isolated_filesystem() as f:
            self.context.repositories = {
                "gameta": {
                    "url": "https://github.com/testing/gameta.git",
                    "path": ".",
                    "tags": ["metarepo"],
                    "__metarepo__": True,
                    "vcs": "git",
                },
                "genisys": {
                    "url": "https://github.com/testing/genisys.git",
                    "path": "core/genisys",
                    "tags": ["core", "templating"],
                    "__metarepo__": False,
                    "vcs": "git",
                },
                "genisys-testing": {
                    "url": "https://github.com/testing/genisys-testing.git",
                    "path": "core/genisys-testing",
                    "tags": ["core", "testing", "developer"],
                    "__metarepo__": False,
                    "vcs": "git",
                },
            }
            self.context.project_dir = f
            self.assertTrue(self.context.is_primary_metarepo("gameta"))
            self.assertFalse(self.context.is_primary_metarepo("genisys"))
            self.assertFalse(self.context.is_primary_metarepo("genisys-testing"))

    def test_gameta_context_is_primary_metarepo_repo_does_not_exist(self):
        with self.runner.isolated_filesystem() as f:
            self.context.repositories = {
                "gameta": {
                    "url": "https://github.com/testing/gameta.git",
                    "path": ".",
                    "tags": ["metarepo"],
                    "__metarepo__": True,
                    "vcs": "git",
                },
                "genisys": {
                    "url": "https://github.com/testing/genisys.git",
                    "path": "core/genisys",
                    "tags": ["core", "templating"],
                    "__metarepo__": False,
                    "vcs": "git",
                },
                "genisys-testing": {
                    "url": "https://github.com/testing/genisys-testing.git",
                    "path": "core/genisys-testing",
                    "tags": ["core", "testing", "developer"],
                    "__metarepo__": False,
                    "vcs": "git",
                },
            }
            self.context.project_dir = f
            with self.assertRaises(ContextError):
                self.context.is_primary_metarepo("test")

    def test_gameta_context_generate_tags_no_repositories(self):
        self.context.generate_tags()
        self.assertEqual({}, self.context.tags)

    def test_gameta_context_generate_tags_from_repositories(self):
        self.context.repositories = {
            "gameta": {
                "url": "https://github.com/testing/gameta.git",
                "path": ".",
                "tags": ["metarepo"],
                "__metarepo__": True,
                "vcs": "git",
            },
            "genisys": {
                "url": "https://github.com/testing/genisys.git",
                "path": "core/genisys",
                "tags": ["core", "templating"],
                "__metarepo__": False,
                "vcs": "git",
            },
            "genisys-testing": {
                "url": "https://github.com/testing/genisys-testing.git",
                "path": "core/genisys-testing",
                "tags": ["core", "testing", "developer"],
                "__metarepo__": False,
                "vcs": "git",
            },
        }
        self.context.generate_tags()
        self.assertCountEqual(
            self.context.tags,
            {
                "core": ["genisys-testing", "genisys"],
                "testing": ["genisys-testing"],
                "developer": ["genisys-testing"],
                "templating": ["genisys"],
                "metarepo": ["gameta"],
            },
        )

    def test_gameta_context_load_empty_gameta_file(self):
        with self.runner.isolated_filesystem() as f:
            makedirs(join(f, ".gameta"))
            with open(join(f, ".gameta", ".gameta"), "w"):
                pass

            self.context.project_dir = f
            self.context.load()
            self.assertEqual(self.context.repositories, {})
            self.assertEqual(self.context.commands, {})

    def test_gameta_context_load_malformed_repositories_in_gameta_file(self):
        with self.runner.isolated_filesystem() as f:
            makedirs(join(f, ".gameta"))
            with open(join(f, ".gameta", ".gameta"), "w") as m:
                output = {
                    "version": __version__,
                    "repositories": {"test": "malformed_metafile"},
                    "commands": {
                        "hello_world": {
                            "commands": ["git fetch --all --tags --prune", "git pull"],
                            "description": "Hello world",
                            "tags": [],
                            "repositories": ["gitdb", "GitPython"],
                            "all": False,
                            "verbose": False,
                            "shell": False,
                            "venv": None,
                            "sep": "&&",
                            "debug": False,
                            "raise_errors": False,
                        },
                        "hello_world2": {
                            "commands": ["git fetch --all --tags --prune", "git pull"],
                            "description": "Hello world",
                            "tags": [],
                            "repositories": ["gitdb", "GitPython"],
                            "all": False,
                            "verbose": False,
                            "shell": False,
                            "venv": None,
                            "sep": "&&",
                            "debug": False,
                            "raise_errors": False,
                        },
                    },
                    "constants": {"HELLO": "world", "I": "am", "A": "test"},
                    "virtualenvs": {
                        "testenv": join(f, "testenv"),
                        "testenv2": join(f, "testenv2"),
                    },
                }
                json.dump(output, m)

            self.context.init(f)
            self.context.load()
            self.assertEqual(self.context.repositories, {})
            self.assertEqual(
                self.context.commands,
                {
                    "hello_world": {
                        "commands": ["git fetch --all --tags --prune", "git pull"],
                        "description": "Hello world",
                        "tags": [],
                        "repositories": ["gitdb", "GitPython"],
                        "all": False,
                        "verbose": False,
                        "shell": False,
                        "venv": None,
                        "sep": "&&",
                        "debug": False,
                        "raise_errors": False,
                    },
                    "hello_world2": {
                        "commands": ["git fetch --all --tags --prune", "git pull"],
                        "description": "Hello world",
                        "tags": [],
                        "repositories": ["gitdb", "GitPython"],
                        "all": False,
                        "verbose": False,
                        "shell": False,
                        "venv": None,
                        "sep": "&&",
                        "debug": False,
                        "raise_errors": False,
                    },
                },
            )
            self.assertEqual(
                self.context.constants, {"HELLO": "world", "I": "am", "A": "test"}
            )

    def test_gameta_context_load_missing_repositories_in_gameta_file(self):
        with self.runner.isolated_filesystem() as f:
            makedirs(join(f, ".gameta"))
            with open(join(f, ".gameta", ".gameta"), "w") as m:
                output = {
                    "version": __version__,
                    "commands": {
                        "hello_world": {
                            "commands": ["git fetch --all --tags --prune", "git pull"],
                            "description": "Hello world",
                            "tags": [],
                            "repositories": ["gitdb", "GitPython"],
                            "all": False,
                            "verbose": False,
                            "shell": False,
                            "venv": None,
                            "sep": "&&",
                            "debug": False,
                            "raise_errors": False,
                        },
                        "hello_world2": {
                            "commands": ["git fetch --all --tags --prune", "git pull"],
                            "description": "Hello world",
                            "tags": [],
                            "repositories": ["gitdb", "GitPython"],
                            "all": False,
                            "verbose": False,
                            "shell": False,
                            "venv": None,
                            "sep": "&&",
                            "debug": False,
                            "raise_errors": False,
                        },
                    },
                    "constants": {"HELLO": "world", "I": "am", "A": "test"},
                    "virtualenvs": {
                        "testenv": join(f, "testenv"),
                        "testenv2": join(f, "testenv2"),
                    },
                }
                json.dump(output, m)

            self.context.init(f)
            self.context.load()
            self.assertEqual(self.context.repositories, {})
            self.assertEqual(
                self.context.commands,
                {
                    "hello_world": {
                        "commands": ["git fetch --all --tags --prune", "git pull"],
                        "description": "Hello world",
                        "tags": [],
                        "repositories": ["gitdb", "GitPython"],
                        "all": False,
                        "verbose": False,
                        "shell": False,
                        "venv": None,
                        "sep": "&&",
                        "debug": False,
                        "raise_errors": False,
                    },
                    "hello_world2": {
                        "commands": ["git fetch --all --tags --prune", "git pull"],
                        "description": "Hello world",
                        "tags": [],
                        "repositories": ["gitdb", "GitPython"],
                        "all": False,
                        "verbose": False,
                        "shell": False,
                        "venv": None,
                        "sep": "&&",
                        "debug": False,
                        "raise_errors": False,
                    },
                },
            )
            self.assertEqual(
                self.context.constants, {"HELLO": "world", "I": "am", "A": "test"}
            )
            self.assertEqual(
                self.context.virtualenvs,
                {"testenv": join(f, "testenv"), "testenv2": join(f, "testenv2")},
            )

    def test_gameta_context_load_malformed_commands_in_gameta_file(self):
        with self.runner.isolated_filesystem() as f:
            makedirs(join(f, ".gameta"))
            with open(join(f, ".gameta", ".gameta"), "w") as m:
                json.dump(
                    {
                        "version": __version__,
                        "repositories": {
                            "gameta": {
                                "url": "https://github.com/testing/gameta.git",
                                "path": ".",
                                "tags": ["metarepo"],
                                "__metarepo__": True,
                                "vcs": "git",
                            },
                            "genisys": {
                                "url": "https://github.com/testing/genisys.git",
                                "path": "core/genisys",
                                "tags": ["core", "templating"],
                                "__metarepo__": False,
                                "vcs": "git",
                            },
                            "genisys-testing": {
                                "url": "https://github.com/testing/genisys-testing.git",
                                "path": "core/genisys-testing",
                                "tags": ["core", "testing", "developer"],
                                "__metarepo__": False,
                                "vcs": "git",
                            },
                        },
                        "commands": {"invalid": "commands"},
                        "constants": {"HELLO": "world", "I": "am", "A": "test"},
                        "virtualenvs": {
                            "testenv": join(f, "testenv"),
                            "testenv2": join(f, "testenv2"),
                        },
                    },
                    m,
                )

            self.context.init(f)
            self.context.load()
            self.assertCountEqual(
                self.context.repositories,
                {
                    "gameta": {
                        "url": "https://github.com/testing/gameta.git",
                        "path": ".",
                        "tags": ["metarepo"],
                        "__metarepo__": True,
                        "vcs": "git",
                    },
                    "genisys": {
                        "url": "https://github.com/testing/genisys.git",
                        "path": "core/genisys",
                        "tags": ["core", "templating"],
                        "__metarepo__": False,
                        "vcs": "git",
                    },
                    "genisys-testing": {
                        "url": "https://github.com/testing/genisys-testing.git",
                        "path": "core/genisys-testing",
                        "tags": ["core", "testing", "developer"],
                        "__metarepo__": False,
                        "vcs": "git",
                    },
                },
            )
            self.assertEqual(self.context.commands, {})
            self.assertEqual(
                self.context.constants, {"HELLO": "world", "I": "am", "A": "test"}
            )
            self.assertEqual(
                self.context.virtualenvs,
                {"testenv": join(f, "testenv"), "testenv2": join(f, "testenv2")},
            )

    def test_gameta_context_load_malformed_constants_in_gameta_file(self):
        with self.runner.isolated_filesystem() as f:
            makedirs(join(f, ".gameta"))
            with open(join(f, ".gameta", ".gameta"), "w") as m:
                json.dump(
                    {
                        "version": __version__,
                        "repositories": {
                            "gameta": {
                                "url": "https://github.com/testing/gameta.git",
                                "path": ".",
                                "tags": ["metarepo"],
                                "__metarepo__": True,
                                "vcs": "git",
                            },
                            "genisys": {
                                "url": "https://github.com/testing/genisys.git",
                                "path": "core/genisys",
                                "tags": ["core", "templating"],
                                "__metarepo__": False,
                                "vcs": "git",
                            },
                            "genisys-testing": {
                                "url": "https://github.com/testing/genisys-testing.git",
                                "path": "core/genisys-testing",
                                "tags": ["core", "testing", "developer"],
                                "__metarepo__": False,
                                "vcs": "git",
                            },
                        },
                        "commands": {
                            "hello_world": {
                                "commands": [
                                    "git fetch --all --tags --prune",
                                    "git pull",
                                ],
                                "description": "Hello world",
                                "tags": [],
                                "repositories": ["gitdb", "GitPython"],
                                "all": False,
                                "verbose": False,
                                "shell": False,
                                "venv": None,
                                "sep": "&&",
                                "debug": False,
                                "raise_errors": False,
                            },
                            "hello_world2": {
                                "commands": [
                                    "git fetch --all --tags --prune",
                                    "git pull",
                                ],
                                "description": "Hello world",
                                "tags": [],
                                "repositories": ["gitdb", "GitPython"],
                                "all": False,
                                "verbose": False,
                                "shell": False,
                                "venv": None,
                                "sep": "&&",
                                "debug": False,
                                "raise_errors": False,
                            },
                        },
                        "constants": {"hello": "world", "i": "am", "a": "test"},
                        "virtualenvs": {
                            "testenv": join(f, "testenv"),
                            "testenv2": join(f, "testenv2"),
                        },
                    },
                    m,
                )

            self.context.init(f)
            self.context.load()
            self.assertCountEqual(
                self.context.repositories,
                {
                    "gameta": {
                        "url": "https://github.com/testing/gameta.git",
                        "path": ".",
                        "tags": ["metarepo"],
                        "__metarepo__": True,
                        "vcs": "git",
                    },
                    "genisys": {
                        "url": "https://github.com/testing/genisys.git",
                        "path": "core/genisys",
                        "tags": ["core", "templating"],
                        "__metarepo__": False,
                        "vcs": "git",
                    },
                    "genisys-testing": {
                        "url": "https://github.com/testing/genisys-testing.git",
                        "path": "core/genisys-testing",
                        "tags": ["core", "testing", "developer"],
                        "__metarepo__": False,
                        "vcs": "git",
                    },
                },
            )
            self.assertEqual(
                self.context.commands,
                {
                    "hello_world": {
                        "commands": ["git fetch --all --tags --prune", "git pull"],
                        "description": "Hello world",
                        "tags": [],
                        "repositories": ["gitdb", "GitPython"],
                        "all": False,
                        "verbose": False,
                        "shell": False,
                        "venv": None,
                        "sep": "&&",
                        "debug": False,
                        "raise_errors": False,
                    },
                    "hello_world2": {
                        "commands": ["git fetch --all --tags --prune", "git pull"],
                        "description": "Hello world",
                        "tags": [],
                        "repositories": ["gitdb", "GitPython"],
                        "all": False,
                        "verbose": False,
                        "shell": False,
                        "venv": None,
                        "sep": "&&",
                        "debug": False,
                        "raise_errors": False,
                    },
                },
            )
            self.assertEqual(self.context.constants, {})
            self.assertEqual(
                self.context.virtualenvs,
                {"testenv": join(f, "testenv"), "testenv2": join(f, "testenv2")},
            )

    def test_gameta_context_load_malformed_virtualenvs_in_gameta_file(self):
        with self.runner.isolated_filesystem() as f:
            makedirs(join(f, ".gameta"))
            with open(join(f, ".gameta", ".gameta"), "w") as m:
                json.dump(
                    {
                        "version": __version__,
                        "repositories": {
                            "gameta": {
                                "url": "https://github.com/testing/gameta.git",
                                "path": ".",
                                "tags": ["metarepo"],
                                "__metarepo__": True,
                                "vcs": "git",
                            },
                            "genisys": {
                                "url": "https://github.com/testing/genisys.git",
                                "path": "core/genisys",
                                "tags": ["core", "templating"],
                                "__metarepo__": False,
                                "vcs": "git",
                            },
                            "genisys-testing": {
                                "url": "https://github.com/testing/genisys-testing.git",
                                "path": "core/genisys-testing",
                                "tags": ["core", "testing", "developer"],
                                "__metarepo__": False,
                                "vcs": "git",
                            },
                        },
                        "commands": {
                            "hello_world": {
                                "commands": [
                                    "git fetch --all --tags --prune",
                                    "git pull",
                                ],
                                "description": "Hello world",
                                "tags": [],
                                "repositories": ["gitdb", "GitPython"],
                                "all": False,
                                "verbose": False,
                                "shell": False,
                                "venv": None,
                                "sep": "&&",
                                "debug": False,
                                "raise_errors": False,
                            },
                            "hello_world2": {
                                "commands": [
                                    "git fetch --all --tags --prune",
                                    "git pull",
                                ],
                                "description": "Hello world",
                                "tags": [],
                                "repositories": ["gitdb", "GitPython"],
                                "all": False,
                                "verbose": False,
                                "shell": False,
                                "venv": None,
                                "sep": "&&",
                                "debug": False,
                                "raise_errors": False,
                            },
                        },
                        "constants": {"HELLO": "world", "I": "am", "A": "test"},
                        "virtualenvs": {
                            "D*SJ": join(f, "testenv"),
                            "#@(*$": join(f, "testenv2"),
                        },
                    },
                    m,
                )

            self.context.init(f)
            self.context.load()
            self.assertCountEqual(
                self.context.repositories,
                {
                    "gameta": {
                        "url": "https://github.com/testing/gameta.git",
                        "path": ".",
                        "tags": ["metarepo"],
                        "__metarepo__": True,
                        "vcs": "git",
                    },
                    "genisys": {
                        "url": "https://github.com/testing/genisys.git",
                        "path": "core/genisys",
                        "tags": ["core", "templating"],
                        "__metarepo__": False,
                        "vcs": "git",
                    },
                    "genisys-testing": {
                        "url": "https://github.com/testing/genisys-testing.git",
                        "path": "core/genisys-testing",
                        "tags": ["core", "testing", "developer"],
                        "__metarepo__": False,
                        "vcs": "git",
                    },
                },
            )
            self.assertEqual(
                self.context.commands,
                {
                    "hello_world": {
                        "commands": ["git fetch --all --tags --prune", "git pull"],
                        "description": "Hello world",
                        "tags": [],
                        "repositories": ["gitdb", "GitPython"],
                        "all": False,
                        "verbose": False,
                        "shell": False,
                        "venv": None,
                        "sep": "&&",
                        "debug": False,
                        "raise_errors": False,
                    },
                    "hello_world2": {
                        "commands": ["git fetch --all --tags --prune", "git pull"],
                        "description": "Hello world",
                        "tags": [],
                        "repositories": ["gitdb", "GitPython"],
                        "all": False,
                        "verbose": False,
                        "shell": False,
                        "venv": None,
                        "sep": "&&",
                        "debug": False,
                        "raise_errors": False,
                    },
                },
            )
            self.assertEqual(
                self.context.constants, {"HELLO": "world", "I": "am", "A": "test"}
            )
            self.assertEqual(self.context.virtualenvs, {})

    def test_gameta_context_load_full_gameta_file(self):
        with self.runner.isolated_filesystem() as f:
            makedirs(join(f, ".gameta"))
            with open(join(f, ".gameta", ".gameta"), "w") as m:
                json.dump(
                    {
                        "version": __version__,
                        "repositories": {
                            "gameta": {
                                "url": "https://github.com/testing/gameta.git",
                                "path": ".",
                                "tags": ["metarepo"],
                                "__metarepo__": True,
                                "vcs": "git",
                            },
                            "genisys": {
                                "url": "https://github.com/testing/genisys.git",
                                "path": "core/genisys",
                                "tags": ["core", "templating"],
                                "__metarepo__": False,
                                "vcs": "git",
                            },
                            "genisys-testing": {
                                "url": "https://github.com/testing/genisys-testing.git",
                                "path": "core/genisys-testing",
                                "tags": ["core", "testing", "developer"],
                                "__metarepo__": False,
                                "vcs": "git",
                            },
                        },
                        "commands": {
                            "hello_world": {
                                "commands": [
                                    "git fetch --all --tags --prune",
                                    "git pull",
                                ],
                                "description": "Hello world",
                                "tags": [],
                                "repositories": ["gitdb", "GitPython"],
                                "all": False,
                                "verbose": False,
                                "shell": False,
                                "venv": None,
                                "sep": "&&",
                                "debug": False,
                                "raise_errors": False,
                            },
                            "hello_world2": {
                                "commands": [
                                    "git fetch --all --tags --prune",
                                    "git pull",
                                ],
                                "description": "Hello world",
                                "tags": [],
                                "repositories": ["gitdb", "GitPython"],
                                "all": False,
                                "verbose": False,
                                "shell": False,
                                "venv": None,
                                "sep": "&&",
                                "debug": False,
                                "raise_errors": False,
                            },
                        },
                        "constants": {"HELLO": "world", "I": "am", "A": "test"},
                        "virtualenvs": {
                            "testenv": join(f, "testenv"),
                            "testenv2": join(f, "testenv2"),
                        },
                    },
                    m,
                )
            self.context.init(f)
            self.context.load()
            self.assertCountEqual(
                self.context.repositories,
                {
                    "gameta": {
                        "url": "https://github.com/testing/gameta.git",
                        "path": ".",
                        "tags": ["metarepo"],
                        "__metarepo__": True,
                        "vcs": "git",
                    },
                    "genisys": {
                        "url": "https://github.com/testing/genisys.git",
                        "path": "core/genisys",
                        "tags": ["core", "templating"],
                        "__metarepo__": False,
                        "vcs": "git",
                    },
                    "genisys-testing": {
                        "url": "https://github.com/testing/genisys-testing.git",
                        "path": "core/genisys-testing",
                        "tags": ["core", "testing", "developer"],
                        "__metarepo__": False,
                        "vcs": "git",
                    },
                },
            )
            self.assertCountEqual(
                self.context.tags,
                {
                    "core": ["genisys-testing", "genisys"],
                    "testing": ["genisys-testing"],
                    "developer": ["genisys-testing"],
                    "templating": ["genisys"],
                    "metarepo": ["gameta"],
                },
            )
            self.assertTrue(self.context.is_metarepo)
            self.assertCountEqual(
                self.context.commands,
                {
                    "hello_world": {
                        "commands": ["git fetch --all --tags --prune", "git pull"],
                        "description": "Hello world",
                        "tags": [],
                        "repositories": ["gitdb", "GitPython"],
                        "all": False,
                        "verbose": False,
                        "shell": False,
                        "venv": None,
                        "sep": "&&",
                        "debug": False,
                        "raise_errors": False,
                    },
                    "hello_world2": {
                        "commands": ["git fetch --all --tags --prune", "git pull"],
                        "description": "Hello world",
                        "tags": [],
                        "repositories": ["gitdb", "GitPython"],
                        "all": False,
                        "verbose": False,
                        "shell": False,
                        "venv": None,
                        "sep": "&&",
                        "debug": False,
                        "raise_errors": False,
                    },
                },
            )
            self.assertEqual(
                self.context.constants, {"HELLO": "world", "I": "am", "A": "test"}
            )
            self.assertEqual(
                self.context.virtualenvs,
                {"testenv": join(f, "testenv"), "testenv2": join(f, "testenv2")},
            )

    def test_gameta_context_load_gameta_file_with_mergeable_constants(self):
        with self.runner.isolated_filesystem() as f:
            makedirs(join(f, ".gameta"))
            with open(join(f, ".gameta", ".gameta"), "w") as m:
                json.dump(
                    {
                        "version": __version__,
                        "repositories": {
                            "gameta": {
                                "url": "https://github.com/testing/gameta.git",
                                "path": ".",
                                "tags": ["metarepo"],
                                "__metarepo__": True,
                                "vcs": "git",
                            },
                            "genisys": {
                                "url": "https://github.com/testing/genisys.git",
                                "path": "core/genisys",
                                "tags": ["core", "templating"],
                                "__metarepo__": False,
                                "vcs": "git",
                            },
                            "genisys-testing": {
                                "url": "https://github.com/testing/genisys-testing.git",
                                "path": "core/genisys-testing",
                                "tags": ["core", "testing", "developer"],
                                "__metarepo__": False,
                                "vcs": "git",
                            },
                        },
                        "commands": {
                            "hello_world": {
                                "commands": [
                                    "git fetch --all --tags --prune",
                                    "git pull",
                                ],
                                "description": "Hello world",
                                "tags": [],
                                "repositories": ["gitdb", "GitPython"],
                                "all": False,
                                "verbose": False,
                                "shell": False,
                                "venv": None,
                                "sep": "&&",
                                "debug": False,
                                "raise_errors": False,
                            },
                            "hello_world2": {
                                "commands": [
                                    "git fetch --all --tags --prune",
                                    "git pull",
                                ],
                                "description": "Hello world",
                                "tags": [],
                                "repositories": ["gitdb", "GitPython"],
                                "all": False,
                                "verbose": False,
                                "shell": False,
                                "venv": None,
                                "sep": "&&",
                                "debug": False,
                                "raise_errors": False,
                            },
                        },
                        "constants": {"$HELLO": "world", "$I": "am", "$A": "test"},
                    },
                    m,
                )

            self.context.init(f)
            self.context.load()
            self.assertCountEqual(
                self.context.repositories,
                {
                    "gameta": {
                        "url": "https://github.com/testing/gameta.git",
                        "path": ".",
                        "tags": ["metarepo"],
                        "__metarepo__": True,
                        "vcs": "git",
                    },
                    "genisys": {
                        "url": "https://github.com/testing/genisys.git",
                        "path": "core/genisys",
                        "tags": ["core", "templating"],
                        "__metarepo__": False,
                        "vcs": "git",
                    },
                    "genisys-testing": {
                        "url": "https://github.com/testing/genisys-testing.git",
                        "path": "core/genisys-testing",
                        "tags": ["core", "testing", "developer"],
                        "__metarepo__": False,
                        "vcs": "git",
                    },
                },
            )
            self.assertCountEqual(
                self.context.tags,
                {
                    "core": ["genisys-testing", "genisys"],
                    "testing": ["genisys-testing"],
                    "developer": ["genisys-testing"],
                    "templating": ["genisys"],
                    "metarepo": ["gameta"],
                },
            )
            self.assertTrue(self.context.is_metarepo)
            self.assertCountEqual(
                self.context.commands,
                {
                    "hello_world": {
                        "commands": ["git fetch --all --tags --prune", "git pull"],
                        "description": "Hello world",
                        "tags": [],
                        "repositories": ["gitdb", "GitPython"],
                        "all": False,
                        "verbose": False,
                        "shell": False,
                        "venv": None,
                        "sep": "&&",
                        "debug": False,
                        "raise_errors": False,
                    },
                    "hello_world2": {
                        "commands": ["git fetch --all --tags --prune", "git pull"],
                        "description": "Hello world",
                        "tags": [],
                        "repositories": ["gitdb", "GitPython"],
                        "all": False,
                        "verbose": False,
                        "shell": False,
                        "venv": None,
                        "sep": "&&",
                        "debug": False,
                        "raise_errors": False,
                    },
                },
            )
            self.assertEqual(
                self.context.constants, {"$HELLO": "world", "$I": "am", "$A": "test"}
            )

    def test_gameta_context_load_no_gameta_file(self):
        with self.runner.isolated_filesystem() as f:
            self.context.init(f)
            self.context.load()
            self.assertEqual(self.context.repositories, {})
            self.assertEqual(self.context.commands, {})
            self.assertEqual(self.context.tags, {})
            self.assertFalse(self.context.is_metarepo)

    def test_gameta_context_load_wrongly_formed_gameta_file(self):
        with self.runner.isolated_filesystem() as f:
            makedirs(join(f, ".gameta"))
            with open(join(f, ".gameta", ".gameta"), "w") as m:
                json.dump(
                    {
                        "gameta": {
                            "url": "https://github.com/testing/gameta.git",
                            "path": ".",
                            "tags": ["metarepo"],
                            "__metarepo__": True,
                            "vcs": "git",
                        },
                        "genisys": {
                            "url": "https://github.com/testing/genisys.git",
                            "path": "core/genisys",
                            "tags": ["core", "templating"],
                            "__metarepo__": False,
                            "vcs": "git",
                        },
                        "genisys-testing": {
                            "url": "https://github.com/testing/genisys-testing.git",
                            "path": "core/genisys-testing",
                            "tags": ["core", "testing", "developer"],
                            "__metarepo__": False,
                            "vcs": "git",
                        },
                    },
                    m,
                )
            self.context.init(f)
            self.context.load()
            self.assertEqual(self.context.repositories, {})
            self.assertEqual(self.context.commands, {})
            self.assertEqual(self.context.tags, {})
            self.assertFalse(self.context.is_metarepo)

    def test_gameta_context_export_meta_file_non_existent(self):
        with self.runner.isolated_filesystem() as f:
            makedirs(join(f, ".gameta"))
            self.context.init(f)
            self.context.repositories = {
                "gameta": {
                    "url": "https://github.com/testing/gameta.git",
                    "path": ".",
                    "tags": ["metarepo"],
                    "__metarepo__": True,
                    "vcs": "git",
                }
            }
            self.context.export()
            self.assertTrue(exists(join(f, ".gameta", ".gameta")))
            with open(join(f, ".gameta", ".gameta")) as f:
                self.assertEqual(
                    json.load(f),
                    {
                        "version": __version__,
                        "repositories": {
                            "gameta": {
                                "url": "https://github.com/testing/gameta.git",
                                "path": ".",
                                "tags": ["metarepo"],
                                "__metarepo__": True,
                                "vcs": "git",
                            }
                        },
                    },
                )

    def test_gameta_context_export_meta_file_empty(self):
        with self.runner.isolated_filesystem() as f:
            makedirs(join(f, ".gameta"))
            with open(join(f, ".gameta", ".gameta"), "w") as m:
                json.dump({}, m)
            self.context.init(f)
            self.context.repositories = {
                "gameta": {
                    "url": "https://github.com/testing/gameta.git",
                    "path": ".",
                    "tags": ["metarepo"],
                    "__metarepo__": True,
                    "vcs": "git",
                }
            }
            self.context.export()
            self.assertTrue(exists(join(f, ".gameta", ".gameta")))
            with open(join(f, ".gameta", ".gameta")) as f:
                self.assertEqual(
                    json.load(f),
                    {
                        "version": __version__,
                        "repositories": {
                            "gameta": {
                                "url": "https://github.com/testing/gameta.git",
                                "path": ".",
                                "tags": ["metarepo"],
                                "__metarepo__": True,
                                "vcs": "git",
                            }
                        },
                    },
                )

    def test_gameta_context_export_meta_file_populated(self):
        with self.runner.isolated_filesystem() as f:
            makedirs(join(f, ".gameta"))
            with open(join(f, ".gameta", ".gameta"), "w") as m:
                json.dump(
                    {
                        "repositories": {
                            "gameta": {
                                "url": "https://github.com/testing/gameta.git",
                                "path": ".",
                                "tags": ["metarepo"],
                            }
                        }
                    },
                    m,
                )
            self.context.init(f)
            self.context.repositories = {
                "genisys": {
                    "url": "https://github.com/testing/genisys.git",
                    "path": "core/genisys",
                    "tags": ["core", "templating"],
                    "__metarepo__": False,
                },
                "genisys-testing": {
                    "url": "https://github.com/testing/genisys-testing.git",
                    "path": "core/genisys-testing",
                    "tags": ["core", "testing", "developer"],
                    "__metarepo__": False,
                },
            }
            self.context.commands = {
                "hello_world": {
                    "commands": ["git fetch --all --tags --prune", "git pull"],
                    "tags": [],
                    "repositories": ["gitdb", "GitPython"],
                    "verbose": False,
                    "shell": False,
                    "raise_errors": False,
                },
                "hello_world2": {
                    "commands": ["git fetch --all --tags --prune", "git pull"],
                    "tags": [],
                    "repositories": ["gitdb", "GitPython"],
                    "verbose": False,
                    "shell": False,
                    "raise_errors": False,
                },
            }
            self.context.constants = {"HELLO": "world", "I": "am", "A": "test"}
            self.context.export()
            self.assertTrue(exists(join(f, ".gameta", ".gameta")))
            with open(join(f, ".gameta", ".gameta")) as f:
                self.assertEqual(
                    json.load(f),
                    {
                        "version": __version__,
                        "repositories": {
                            "genisys": {
                                "url": "https://github.com/testing/genisys.git",
                                "path": "core/genisys",
                                "tags": ["core", "templating"],
                                "__metarepo__": False,
                            },
                            "genisys-testing": {
                                "url": "https://github.com/testing/genisys-testing.git",
                                "path": "core/genisys-testing",
                                "tags": ["core", "testing", "developer"],
                                "__metarepo__": False,
                            },
                        },
                        "commands": {
                            "hello_world": {
                                "commands": [
                                    "git fetch --all --tags --prune",
                                    "git pull",
                                ],
                                "tags": [],
                                "repositories": ["gitdb", "GitPython"],
                                "verbose": False,
                                "shell": False,
                                "raise_errors": False,
                            },
                            "hello_world2": {
                                "commands": [
                                    "git fetch --all --tags --prune",
                                    "git pull",
                                ],
                                "tags": [],
                                "repositories": ["gitdb", "GitPython"],
                                "verbose": False,
                                "shell": False,
                                "raise_errors": False,
                            },
                        },
                        "constants": {"HELLO": "world", "I": "am", "A": "test"},
                    },
                )

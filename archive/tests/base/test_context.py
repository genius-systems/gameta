import json
from os import makedirs, listdir, symlink, getcwd, getenv, environ
from os.path import join, basename, exists
from unittest import TestCase, skipIf

from click.testing import CliRunner

from gameta import __version__
from gameta.base import GametaContext


class TestGametaContext(TestCase):
    def setUp(self) -> None:
        self.maxDiff = None
        self.context = GametaContext()
        self.runner = CliRunner()

    def test_gameta_context_environment_variables_properly_extracted(self):
        self.assertTrue(all(i[0] == '$' for i in self.context.env_vars))

    @skipIf('HOME' not in environ, 'HOME variable is not present')
    def test_gameta_context_environment_variables_exists(self):
        self.assertTrue('$HOME' in self.context.env_vars)

    def test_gameta_context_cd_to_valid_directory(self):
        with self.runner.isolated_filesystem() as f:
            makedirs(join(f, 'test', 'hello', 'world'))
            makedirs(join(f, 'i', 'am'))
            makedirs(join(f, 'a'))

            self.context.project_dir = f
            with self.context.cd(join('test', 'hello')):
                self.assertCountEqual(listdir('.'), ['world'])
            self.assertCountEqual(listdir('.'), ['test', 'i', 'a'])

    def test_gameta_context_cd_to_nonexistent_directory(self):
        with self.runner.isolated_filesystem() as f:
            self.context.project_dir = f
            with self.assertRaises(FileNotFoundError):
                with self.context.cd('test'):
                    pass

    def test_gameta_context_only_cd_within_project_directory(self):
        with self.runner.isolated_filesystem() as f:
            self.context.project_dir = f
            with self.assertRaises(FileNotFoundError):
                with self.context.cd('/usr'):
                    pass
            with self.assertRaises(FileNotFoundError):
                with self.context.cd('/////usr'):
                    pass

    def test_gameta_context_cd_to_symlink_within_project_directory(self):
        with self.runner.isolated_filesystem() as f:
            makedirs(join(f, 'test'))
            makedirs(join(f, 'a'))
            symlink(join(f, 'a'), join(f, 'test', 'hello'))

            self.context.project_dir = join(f, 'test')
            with self.context.cd('hello'):
                self.assertEqual(basename(getcwd()), 'a')

    def test_gameta_context_project_name_after_providing_project_dir(self):
        with self.runner.isolated_filesystem() as f:
            makedirs(join(f, 'test'))
            self.context.project_dir = join(f, 'test')
            self.assertEqual(self.context.project_name, 'test')

    def test_gameta_context_project_name_no_project_dir(self):
        with self.runner.isolated_filesystem() as f:
            with self.assertRaises(TypeError):
                self.context.project_name

    def test_gameta_context_meta_points_to_meta_file_if_provided(self):
        with self.runner.isolated_filesystem() as f:
            with open(join(f, '.gameta'), 'w') as m:
                m.write('Hello world')
            self.context.project_dir = f
            self.assertEqual(self.context.gameta, join(f, '.gameta'))

    def test_gameta_context_meta_points_to_meta_file_if_not_provided(self):
        with self.runner.isolated_filesystem() as f:
            self.context.project_dir = f
            self.assertEqual(self.context.gameta, join(f, '.gameta'))

    def test_gameta_context_meta_no_project_dir(self):
        with self.runner.isolated_filesystem() as f:
            with self.assertRaises(TypeError):
                self.context.gameta

    def test_gameta_context_gitignore_to_gitignore_file_if_provided(self):
        with self.runner.isolated_filesystem() as f:
            with open(join(f, '.gitignore'), 'w') as m:
                m.write('Hello world')
            self.context.project_dir = f
            self.assertEqual(self.context.gitignore, join(f, '.gitignore'))

    def test_gameta_context_gitignore_points_to_gitignore_file_if_not_provided(self):
        with self.runner.isolated_filesystem() as f:
            self.context.project_dir = f
            self.assertEqual(self.context.gitignore, join(f, '.gitignore'))

    def test_gameta_context_gitignore_no_project_dir(self):
        with self.runner.isolated_filesystem() as f:
            with self.assertRaises(TypeError):
                self.context.gitignore

    def test_gameta_context_add_gitignore_add_path(self):
        self.context.add_gitignore('test_path')
        self.assertEqual(self.context.gitignore_data, ['test_path/\n'])

    def test_gameta_context_remove_gitignore_delete_path(self):
        self.context.add_gitignore('test_path')
        self.context.add_gitignore('another_test_path')
        self.context.add_gitignore('this/is/a/test')
        self.context.remove_gitignore('test_path')
        self.assertEqual(self.context.gitignore_data, ['another_test_path/\n', 'this/is/a/test/\n'])

    def test_gameta_context_remove_gitignore_path_does_not_exist(self):
        self.context.add_gitignore('test_path')
        self.context.add_gitignore('another_test_path')
        self.context.add_gitignore('this/is/a/test')
        self.context.remove_gitignore('test')
        self.assertEqual(self.context.gitignore_data, ['test_path/\n', 'another_test_path/\n', 'this/is/a/test/\n'])

    def test_gameta_context_is_primary_metarepo(self):
        with self.runner.isolated_filesystem() as f:
            self.context.repositories = {
                "gameta": {
                    "url": "https://github.com/testing/gameta.git",
                    "path": ".",
                    "tags": [
                        "metarepo"
                    ],
                    '__metarepo__': True
                },
                "genisys": {
                    "url": "https://github.com/testing/genisys.git",
                    "path": "core/genisys",
                    "tags": [
                        "core",
                        "templating"
                    ],
                    '__metarepo__': False
                },
                "genisys-testing": {
                    "url": "https://github.com/testing/genisys-testing.git",
                    "path": "core/genisys-testing",
                    "tags": [
                        "core",
                        "testing",
                        "developer"
                    ],
                    '__metarepo__': False
                }
            }
            self.context.project_dir = f
            self.assertTrue(self.context.is_primary_metarepo('gameta'))
            self.assertFalse(self.context.is_primary_metarepo('genisys'))
            self.assertFalse(self.context.is_primary_metarepo('genisys-testing'))

    def test_gameta_context_is_primary_metarepo_repo_does_not_exist(self):
        with self.runner.isolated_filesystem() as f:
            self.context.repositories = {
                "gameta": {
                    "url": "https://github.com/testing/gameta.git",
                    "path": ".",
                    "tags": [
                        "metarepo"
                    ],
                    '__metarepo__': True
                },
                "genisys": {
                    "url": "https://github.com/testing/genisys.git",
                    "path": "core/genisys",
                    "tags": [
                        "core",
                        "templating"
                    ],
                    '__metarepo__': False
                },
                "genisys-testing": {
                    "url": "https://github.com/testing/genisys-testing.git",
                    "path": "core/genisys-testing",
                    "tags": [
                        "core",
                        "testing",
                        "developer"
                    ],
                    '__metarepo__': False
                }
            }
            self.context.project_dir = f
            with self.assertRaises(KeyError):
                self.context.is_primary_metarepo('test')

    def test_gameta_context_generate_tags_no_repositories(self):
        self.context.generate_tags()
        self.assertEqual({}, self.context.tags)

    def test_gameta_context_generate_tags_from_repositories(self):
        self.context.repositories = {
            "gameta": {
                "url": "https://github.com/testing/gameta.git",
                "path": ".",
                "tags": [
                    "metarepo"
                ],
                '__metarepo__': True
            },
            "genisys": {
                "url": "https://github.com/testing/genisys.git",
                "path": "core/genisys",
                "tags": [
                    "core",
                    "templating"
                ],
                '__metarepo__': False
            },
            "genisys-testing": {
                "url": "https://github.com/testing/genisys-testing.git",
                "path": "core/genisys-testing",
                "tags": [
                    "core",
                    "testing",
                    "developer"
                ],
                '__metarepo__': False
            }
        }
        self.context.generate_tags()
        self.assertCountEqual(
            self.context.tags,
            {
                'core': ['genisys-testing', 'genisys'],
                'testing': ['genisys-testing'],
                'developer': ['genisys-testing'],
                'templating': ['genisys'],
                'metarepo': ['gameta']
            }
        )

    def test_gameta_context_load_empty_meta_file(self):
        with self.runner.isolated_filesystem() as f:
            with open(join(f, '.gameta'), 'w'):
                pass

            self.context.project_dir = f
            self.context.load()
            self.assertEqual(self.context.repositories, {})
            self.assertEqual(self.context.commands, {})

    def test_gameta_context_load_malformed_repositories_meta_file(self):
        with self.runner.isolated_filesystem() as f:
            with open(join(f, '.gameta'), 'w') as m:
                output = {
                    "version": __version__,
                    'repositories': {
                        'test': 'malformed_metafile'
                    },
                    "commands": {
                        'hello_world': {
                            'commands': ['git fetch --all --tags --prune', 'git pull'],
                            'description': "Hello world",
                            'tags': [],
                            'repositories': ['gitdb', 'GitPython'],
                            'all': False,
                            'verbose': False,
                            'shell': False,
                            'venv': None,
                            'python': False,
                            'raise_errors': False
                        },
                        'hello_world2': {
                            'commands': ['git fetch --all --tags --prune', 'git pull'],
                            'description': "Hello world",
                            'tags': [],
                            'repositories': ['gitdb', 'GitPython'],
                            'all': False,
                            'verbose': False,
                            'shell': False,
                            'venv': None,
                            'python': False,
                            'raise_errors': False
                        }
                    },
                    'constants': {
                        'HELLO': 'world',
                        "I": 'am',
                        'A': 'test'
                    },
                    'virtualenvs': {
                        'testenv': join(f, 'testenv'),
                        'testenv2': join(f, 'testenv2')
                    }
                }
                json.dump(output, m)

            self.context.project_dir = f
            self.context.load()
            self.assertEqual(self.context.repositories, {})
            self.assertEqual(
                self.context.commands,
                {
                    'hello_world': {
                        'commands': ['git fetch --all --tags --prune', 'git pull'],
                        'description': "Hello world",
                        'tags': [],
                        'repositories': ['gitdb', 'GitPython'],
                        'all': False,
                        'verbose': False,
                        'shell': False,
                        'venv': None,
                        'python': False,
                        'raise_errors': False
                    },
                    'hello_world2': {
                        'commands': ['git fetch --all --tags --prune', 'git pull'],
                        'description': "Hello world",
                        'tags': [],
                        'repositories': ['gitdb', 'GitPython'],
                        'all': False,
                        'verbose': False,
                        'shell': False,
                        'venv': None,
                        'python': False,
                        'raise_errors': False
                    }
                }
            )
            self.assertEqual(
                self.context.constants,
                {
                    'HELLO': 'world',
                    "I": 'am',
                    'A': 'test'
                }
            )

    def test_gameta_context_load_missing_repositories_in_meta_file(self):
        with self.runner.isolated_filesystem() as f:
            with open(join(f, '.gameta'), 'w') as m:
                output = {
                    "version": __version__,
                    "commands": {
                        'hello_world': {
                            'commands': ['git fetch --all --tags --prune', 'git pull'],
                            'description': "Hello world",
                            'tags': [],
                            'repositories': ['gitdb', 'GitPython'],
                            'all': False,
                            'verbose': False,
                            'shell': False,
                            'venv': None,
                            'python': False,
                            'raise_errors': False
                        },
                        'hello_world2': {
                            'commands': ['git fetch --all --tags --prune', 'git pull'],
                            'description': "Hello world",
                            'tags': [],
                            'repositories': ['gitdb', 'GitPython'],
                            'all': False,
                            'verbose': False,
                            'shell': False,
                            'venv': None,
                            'python': False,
                            'raise_errors': False
                        }
                    },
                    'constants': {
                        'HELLO': 'world',
                        "I": 'am',
                        'A': 'test'
                    },
                    'virtualenvs': {
                        'testenv': join(f, 'testenv'),
                        'testenv2': join(f, 'testenv2')
                    }
                }
                json.dump(output, m)

            self.context.project_dir = f
            self.context.load()
            self.assertEqual(self.context.repositories, {})
            self.assertEqual(
                self.context.commands,
                {
                    'hello_world': {
                        'commands': ['git fetch --all --tags --prune', 'git pull'],
                        'description': "Hello world",
                        'tags': [],
                        'repositories': ['gitdb', 'GitPython'],
                        'all': False,
                        'verbose': False,
                        'shell': False,
                        'venv': None,
                        'python': False,
                        'raise_errors': False
                    },
                    'hello_world2': {
                        'commands': ['git fetch --all --tags --prune', 'git pull'],
                        'description': "Hello world",
                        'tags': [],
                        'repositories': ['gitdb', 'GitPython'],
                        'all': False,
                        'verbose': False,
                        'shell': False,
                        'venv': None,
                        'python': False,
                        'raise_errors': False
                    }
                }
            )
            self.assertEqual(
                self.context.constants,
                {
                    'HELLO': 'world',
                    "I": 'am',
                    'A': 'test'
                }
            )
            self.assertEqual(
                self.context.virtualenvs,
                {
                    'testenv': join(f, 'testenv'),
                    'testenv2': join(f, 'testenv2')
                }
            )

    def test_gameta_context_load_malformed_commands_meta_file(self):
        with self.runner.isolated_filesystem() as f:
            with open(join(f, '.gameta'), 'w') as m:
                json.dump(
                    {
                        "version": __version__,
                        "repositories": {
                            "gameta": {
                                "url": "https://github.com/testing/gameta.git",
                                "path": ".",
                                "tags": [
                                    "metarepo"
                                ],
                                '__metarepo__': True
                            },
                            "genisys": {
                                "url": "https://github.com/testing/genisys.git",
                                "path": "core/genisys",
                                "tags": [
                                    "core",
                                    "templating"
                                ],
                                '__metarepo__': False
                            },
                            "genisys-testing": {
                                "url": "https://github.com/testing/genisys-testing.git",
                                "path": "core/genisys-testing",
                                "tags": [
                                    "core",
                                    "testing",
                                    "developer"
                                ],
                                '__metarepo__': False
                            }
                        },
                        "commands": {
                            'invalid': 'commands'
                        },
                        'constants': {
                            'HELLO': 'world',
                            "I": 'am',
                            'A': 'test'
                        },
                        'virtualenvs': {
                            'testenv': join(f, 'testenv'),
                            'testenv2': join(f, 'testenv2')
                        }
                    }, m
                )

            self.context.project_dir = f
            self.context.load()
            self.assertCountEqual(
                self.context.repositories,
                {
                    "gameta": {
                        "url": "https://github.com/testing/gameta.git",
                        "path": ".",
                        "tags": [
                            "metarepo"
                        ],
                        '__metarepo__': True
                    },
                    "genisys": {
                        "url": "https://github.com/testing/genisys.git",
                        "path": "core/genisys",
                        "tags": [
                            "core",
                            "templating"
                        ],
                        '__metarepo__': False
                    },
                    "genisys-testing": {
                        "url": "https://github.com/testing/genisys-testing.git",
                        "path": "core/genisys-testing",
                        "tags": [
                            "core",
                            "testing",
                            "developer"
                        ],
                        '__metarepo__': False
                    }
                }
            )
            self.assertEqual(self.context.commands, {})
            self.assertEqual(
                self.context.constants,
                {
                    'HELLO': 'world',
                    "I": 'am',
                    'A': 'test'
                }
            )
            self.assertEqual(
                self.context.virtualenvs,
                {
                    'testenv': join(f, 'testenv'),
                    'testenv2': join(f, 'testenv2')
                }
            )

    def test_gameta_context_load_malformed_constants_meta_file(self):
        with self.runner.isolated_filesystem() as f:
            with open(join(f, '.gameta'), 'w') as m:
                json.dump(
                    {
                        "version": __version__,
                        "repositories": {
                            "gameta": {
                                "url": "https://github.com/testing/gameta.git",
                                "path": ".",
                                "tags": [
                                    "metarepo"
                                ],
                                '__metarepo__': True
                            },
                            "genisys": {
                                "url": "https://github.com/testing/genisys.git",
                                "path": "core/genisys",
                                "tags": [
                                    "core",
                                    "templating"
                                ],
                                '__metarepo__': False
                            },
                            "genisys-testing": {
                                "url": "https://github.com/testing/genisys-testing.git",
                                "path": "core/genisys-testing",
                                "tags": [
                                    "core",
                                    "testing",
                                    "developer"
                                ],
                                '__metarepo__': False
                            }
                        },
                        "commands": {
                            'hello_world': {
                                'commands': ['git fetch --all --tags --prune', 'git pull'],
                                'description': "Hello world",
                                'tags': [],
                                'repositories': ['gitdb', 'GitPython'],
                                'all': False,
                                'verbose': False,
                                'shell': False,
                                'venv': None,
                                'python': False,
                                'raise_errors': False
                            },
                            'hello_world2': {
                                'commands': ['git fetch --all --tags --prune', 'git pull'],
                                'description': "Hello world",
                                'tags': [],
                                'repositories': ['gitdb', 'GitPython'],
                                'all': False,
                                'verbose': False,
                                'shell': False,
                                'venv': None,
                                'python': False,
                                'raise_errors': False
                            }
                        },
                        'constants': {
                            'hello': 'world',
                            "i": 'am',
                            'a': 'test'
                        },
                        'virtualenvs': {
                            'testenv': join(f, 'testenv'),
                            'testenv2': join(f, 'testenv2')
                        }
                    }, m
                )

            self.context.project_dir = f
            self.context.load()
            self.assertCountEqual(
                self.context.repositories,
                {
                    "gameta": {
                        "url": "https://github.com/testing/gameta.git",
                        "path": ".",
                        "tags": [
                            "metarepo"
                        ],
                        '__metarepo__': True
                    },
                    "genisys": {
                        "url": "https://github.com/testing/genisys.git",
                        "path": "core/genisys",
                        "tags": [
                            "core",
                            "templating"
                        ],
                        '__metarepo__': False
                    },
                    "genisys-testing": {
                        "url": "https://github.com/testing/genisys-testing.git",
                        "path": "core/genisys-testing",
                        "tags": [
                            "core",
                            "testing",
                            "developer"
                        ],
                        '__metarepo__': False
                    }
                }
            )
            self.assertEqual(
                self.context.commands,
                {
                    'hello_world': {
                        'commands': ['git fetch --all --tags --prune', 'git pull'],
                        'description': "Hello world",
                        'tags': [],
                        'repositories': ['gitdb', 'GitPython'],
                        'all': False,
                        'verbose': False,
                        'shell': False,
                        'venv': None,
                        'python': False,
                        'raise_errors': False
                    },
                    'hello_world2': {
                        'commands': ['git fetch --all --tags --prune', 'git pull'],
                        'description': "Hello world",
                        'tags': [],
                        'repositories': ['gitdb', 'GitPython'],
                        'all': False,
                        'verbose': False,
                        'shell': False,
                        'venv': None,
                        'python': False,
                        'raise_errors': False
                    }
                }
            )
            self.assertEqual(self.context.constants, {})
            self.assertEqual(
                self.context.virtualenvs,
                {
                    'testenv': join(f, 'testenv'),
                    'testenv2': join(f, 'testenv2')
                }
            )

    def test_gameta_context_load_malformed_virtualenvs_meta_file(self):
        with self.runner.isolated_filesystem() as f:
            with open(join(f, '.gameta'), 'w') as m:
                json.dump(
                    {
                        "version": __version__,
                        "repositories": {
                            "gameta": {
                                "url": "https://github.com/testing/gameta.git",
                                "path": ".",
                                "tags": [
                                    "metarepo"
                                ],
                                '__metarepo__': True
                            },
                            "genisys": {
                                "url": "https://github.com/testing/genisys.git",
                                "path": "core/genisys",
                                "tags": [
                                    "core",
                                    "templating"
                                ],
                                '__metarepo__': False
                            },
                            "genisys-testing": {
                                "url": "https://github.com/testing/genisys-testing.git",
                                "path": "core/genisys-testing",
                                "tags": [
                                    "core",
                                    "testing",
                                    "developer"
                                ],
                                '__metarepo__': False
                            }
                        },
                        "commands": {
                            'hello_world': {
                                'commands': ['git fetch --all --tags --prune', 'git pull'],
                                'description': "Hello world",
                                'tags': [],
                                'repositories': ['gitdb', 'GitPython'],
                                'all': False,
                                'verbose': False,
                                'shell': False,
                                'venv': None,
                                'python': False,
                                'raise_errors': False
                            },
                            'hello_world2': {
                                'commands': ['git fetch --all --tags --prune', 'git pull'],
                                'description': "Hello world",
                                'tags': [],
                                'repositories': ['gitdb', 'GitPython'],
                                'all': False,
                                'verbose': False,
                                'shell': False,
                                'venv': None,
                                'python': False,
                                'raise_errors': False
                            }
                        },
                        'constants': {
                            'HELLO': 'world',
                            "I": 'am',
                            'A': 'test'
                        },
                        'virtualenvs': {
                            'D*SJ': join(f, 'testenv'),
                            '#@(*$': join(f, 'testenv2')
                        }
                    }, m
                )

            self.context.project_dir = f
            self.context.load()
            self.assertCountEqual(
                self.context.repositories,
                {
                    "gameta": {
                        "url": "https://github.com/testing/gameta.git",
                        "path": ".",
                        "tags": [
                            "metarepo"
                        ],
                        '__metarepo__': True
                    },
                    "genisys": {
                        "url": "https://github.com/testing/genisys.git",
                        "path": "core/genisys",
                        "tags": [
                            "core",
                            "templating"
                        ],
                        '__metarepo__': False
                    },
                    "genisys-testing": {
                        "url": "https://github.com/testing/genisys-testing.git",
                        "path": "core/genisys-testing",
                        "tags": [
                            "core",
                            "testing",
                            "developer"
                        ],
                        '__metarepo__': False
                    }
                }
            )
            self.assertEqual(
                self.context.commands,
                {
                    'hello_world': {
                        'commands': ['git fetch --all --tags --prune', 'git pull'],
                        'description': "Hello world",
                        'tags': [],
                        'repositories': ['gitdb', 'GitPython'],
                        'all': False,
                        'verbose': False,
                        'shell': False,
                        'venv': None,
                        'python': False,
                        'raise_errors': False
                    },
                    'hello_world2': {
                        'commands': ['git fetch --all --tags --prune', 'git pull'],
                        'description': "Hello world",
                        'tags': [],
                        'repositories': ['gitdb', 'GitPython'],
                        'all': False,
                        'verbose': False,
                        'shell': False,
                        'venv': None,
                        'python': False,
                        'raise_errors': False
                    }
                }
            )
            self.assertEqual(
                self.context.constants,
                {
                    'HELLO': 'world',
                    "I": 'am',
                    'A': 'test'
                }
            )
            self.assertEqual(self.context.virtualenvs, {})

    def test_gameta_context_load_full_meta_file(self):
        with self.runner.isolated_filesystem() as f:
            with open(join(f, '.gameta'), 'w') as m:
                json.dump(
                    {
                        "version": __version__,
                        "repositories": {
                            "gameta": {
                                "url": "https://github.com/testing/gameta.git",
                                "path": ".",
                                "tags": [
                                    "metarepo"
                                ],
                                '__metarepo__': True
                            },
                            "genisys": {
                                "url": "https://github.com/testing/genisys.git",
                                "path": "core/genisys",
                                "tags": [
                                    "core",
                                    "templating"
                                ],
                                '__metarepo__': False
                            },
                            "genisys-testing": {
                                "url": "https://github.com/testing/genisys-testing.git",
                                "path": "core/genisys-testing",
                                "tags": [
                                    "core",
                                    "testing",
                                    "developer"
                                ],
                                '__metarepo__': False
                            }
                        },
                        "commands": {
                            'hello_world': {
                                'commands': ['git fetch --all --tags --prune', 'git pull'],
                                'description': "Hello world",
                                'tags': [],
                                'repositories': ['gitdb', 'GitPython'],
                                'all': False,
                                'verbose': False,
                                'shell': False,
                                'venv': None,
                                'python': False,
                                'raise_errors': False
                            },
                            'hello_world2': {
                                'commands': ['git fetch --all --tags --prune', 'git pull'],
                                'description': "Hello world",
                                'tags': [],
                                'repositories': ['gitdb', 'GitPython'],
                                'all': False,
                                'verbose': False,
                                'shell': False,
                                'venv': None,
                                'python': False,
                                'raise_errors': False
                            }
                        },
                        'constants': {
                            'HELLO': 'world',
                            "I": 'am',
                            'A': 'test'
                        },
                        'virtualenvs': {
                            'testenv': join(f, 'testenv'),
                            'testenv2': join(f, 'testenv2')
                        }
                    }, m
                )
            self.context.project_dir = f
            self.context.load()
            self.assertCountEqual(
                self.context.repositories,
                {
                    "gameta": {
                        "url": "https://github.com/testing/gameta.git",
                        "path": ".",
                        "tags": [
                            "metarepo"
                        ],
                        '__metarepo__': True
                    },
                    "genisys": {
                        "url": "https://github.com/testing/genisys.git",
                        "path": "core/genisys",
                        "tags": [
                            "core",
                            "templating"
                        ],
                        '__metarepo__': False
                    },
                    "genisys-testing": {
                        "url": "https://github.com/testing/genisys-testing.git",
                        "path": "core/genisys-testing",
                        "tags": [
                            "core",
                            "testing",
                            "developer"
                        ],
                        '__metarepo__': False
                    }
                }
            )
            self.assertCountEqual(
                self.context.tags,
                {
                    'core': ['genisys-testing', 'genisys'],
                    'testing': ['genisys-testing'],
                    'developer': ['genisys-testing'],
                    'templating': ['genisys'],
                    'metarepo': ['gameta']
                }
            )
            self.assertTrue(self.context.is_metarepo)
            self.assertCountEqual(
                self.context.commands,
                {
                    'hello_world': {
                        'commands': ['git fetch --all --tags --prune', 'git pull'],
                        'description': "Hello world",
                        'tags': [],
                        'repositories': ['gitdb', 'GitPython'],
                        'all': False,
                        'verbose': False,
                        'shell': False,
                        'venv': None,
                        'python': False,
                        'raise_errors': False
                    },
                    'hello_world2': {
                        'commands': ['git fetch --all --tags --prune', 'git pull'],
                        'description': "Hello world",
                        'tags': [],
                        'repositories': ['gitdb', 'GitPython'],
                        'all': False,
                        'verbose': False,
                        'shell': False,
                        'venv': None,
                        'python': False,
                        'raise_errors': False
                    }
                }
            )
            self.assertEqual(
                self.context.constants,
                {
                    'HELLO': 'world',
                    "I": 'am',
                    'A': 'test'
                }
            )
            self.assertEqual(
                self.context.virtualenvs,
                {
                    'testenv': join(f, 'testenv'),
                    'testenv2': join(f, 'testenv2')
                }
            )

    def test_gameta_context_load_meta_file_with_mergeable_constants(self):
        with self.runner.isolated_filesystem() as f:
            with open(join(f, '.gameta'), 'w') as m:
                json.dump(
                    {
                        "version": __version__,
                        "repositories": {
                            "gameta": {
                                "url": "https://github.com/testing/gameta.git",
                                "path": ".",
                                "tags": [
                                    "metarepo"
                                ],
                                '__metarepo__': True
                            },
                            "genisys": {
                                "url": "https://github.com/testing/genisys.git",
                                "path": "core/genisys",
                                "tags": [
                                    "core",
                                    "templating"
                                ],
                                '__metarepo__': False
                            },
                            "genisys-testing": {
                                "url": "https://github.com/testing/genisys-testing.git",
                                "path": "core/genisys-testing",
                                "tags": [
                                    "core",
                                    "testing",
                                    "developer"
                                ],
                                '__metarepo__': False
                            }
                        },
                        "commands": {
                            'hello_world': {
                                'commands': ['git fetch --all --tags --prune', 'git pull'],
                                'description': "Hello world",
                                'tags': [],
                                'repositories': ['gitdb', 'GitPython'],
                                'all': False,
                                'verbose': False,
                                'shell': False,
                                'venv': None,
                                'python': False,
                                'raise_errors': False
                            },
                            'hello_world2': {
                                'commands': ['git fetch --all --tags --prune', 'git pull'],
                                'description': "Hello world",
                                'tags': [],
                                'repositories': ['gitdb', 'GitPython'],
                                'all': False,
                                'verbose': False,
                                'shell': False,
                                'venv': None,
                                'python': False,
                                'raise_errors': False
                            }
                        },
                        'constants': {
                            '$HELLO': 'world',
                            "$I": 'am',
                            '$A': 'test'
                        }
                    }, m
                )
            self.context.project_dir = f
            self.context.load()
            self.assertCountEqual(
                self.context.repositories,
                {
                    "gameta": {
                        "url": "https://github.com/testing/gameta.git",
                        "path": ".",
                        "tags": [
                            "metarepo"
                        ],
                        '__metarepo__': True
                    },
                    "genisys": {
                        "url": "https://github.com/testing/genisys.git",
                        "path": "core/genisys",
                        "tags": [
                            "core",
                            "templating"
                        ],
                        '__metarepo__': False
                    },
                    "genisys-testing": {
                        "url": "https://github.com/testing/genisys-testing.git",
                        "path": "core/genisys-testing",
                        "tags": [
                            "core",
                            "testing",
                            "developer"
                        ],
                        '__metarepo__': False
                    }
                }
            )
            self.assertCountEqual(
                self.context.tags,
                {
                    'core': ['genisys-testing', 'genisys'],
                    'testing': ['genisys-testing'],
                    'developer': ['genisys-testing'],
                    'templating': ['genisys'],
                    'metarepo': ['gameta']
                }
            )
            self.assertTrue(self.context.is_metarepo)
            self.assertCountEqual(
                self.context.commands,
                {
                    'hello_world': {
                        'commands': ['git fetch --all --tags --prune', 'git pull'],
                        'description': "Hello world",
                        'tags': [],
                        'repositories': ['gitdb', 'GitPython'],
                        'all': False,
                        'verbose': False,
                        'shell': False,
                        'venv': None,
                        'python': False,
                        'raise_errors': False
                    },
                    'hello_world2': {
                        'commands': ['git fetch --all --tags --prune', 'git pull'],
                        'description': "Hello world",
                        'tags': [],
                        'repositories': ['gitdb', 'GitPython'],
                        'all': False,
                        'verbose': False,
                        'shell': False,
                        'venv': None,
                        'python': False,
                        'raise_errors': False
                    }
                }
            )
            self.assertEqual(
                self.context.constants,
                {
                    '$HELLO': 'world',
                    "$I": 'am',
                    '$A': 'test'
                }
            )

    def test_gameta_context_load_meta_and_gitignore_file(self):
        with self.runner.isolated_filesystem() as f:
            with open(join(f, '.gameta'), 'w') as m:
                json.dump(
                    {
                        "version": __version__,
                        "repositories": {
                            "gameta": {
                                "url": "https://github.com/testing/gameta.git",
                                "path": ".",
                                "tags": [
                                    "metarepo"
                                ],
                                '__metarepo__': True
                            },
                            "genisys": {
                                "url": "https://github.com/testing/genisys.git",
                                "path": "core/genisys",
                                "tags": [
                                    "core",
                                    "templating"
                                ],
                                '__metarepo__': False
                            },
                            "genisys-testing": {
                                "url": "https://github.com/testing/genisys-testing.git",
                                "path": "core/genisys-testing",
                                "tags": [
                                    "core",
                                    "testing",
                                    "developer"
                                ],
                                '__metarepo__': False
                            }
                        },
                        "commands": {
                            'hello_world': {
                                'commands': ['git fetch --all --tags --prune', 'git pull'],
                                'description': "Hello world",
                                'tags': [],
                                'repositories': ['gitdb', 'GitPython'],
                                'all': False,
                                'verbose': False,
                                'shell': False,
                                'venv': None,
                                'python': False,
                                'raise_errors': False
                            },
                            'hello_world2': {
                                'commands': ['git fetch --all --tags --prune', 'git pull'],
                                'description': "Hello world",
                                'tags': [],
                                'repositories': ['gitdb', 'GitPython'],
                                'all': False,
                                'verbose': False,
                                'shell': False,
                                'venv': None,
                                'python': False,
                                'raise_errors': False
                            }
                        },
                        'constants': {
                            'HELLO': 'world',
                            "I": 'am',
                            'A': 'test'
                        }
                    }, m
                )
            with open(join(f, '.gitignore'), 'w') as g:
                g.writelines("HelloWorld\n")
                g.writelines(".env\n")
                g.writelines("env\n")

            self.context.project_dir = f
            self.context.load()
            self.assertCountEqual(
                self.context.gameta_data,
                {
                    "version": __version__,
                    "repositories": {
                        "gameta": {
                            "url": "https://github.com/testing/gameta.git",
                            "path": ".",
                            "tags": [
                                "metarepo"
                            ],
                            '__metarepo__': True
                        },
                        "genisys": {
                            "url": "https://github.com/testing/genisys.git",
                            "path": "core/genisys",
                            "tags": [
                                "core",
                                "templating"
                            ],
                            '__metarepo__': False
                        },
                        "genisys-testing": {
                            "url": "https://github.com/testing/genisys-testing.git",
                            "path": "core/genisys-testing",
                            "tags": [
                                "core",
                                "testing",
                                "developer"
                            ],
                            '__metarepo__': False
                        }
                    },
                    "commands": {
                        'hello_world': {
                            'commands': ['git fetch --all --tags --prune', 'git pull'],
                            'description': "Hello world",
                            'tags': [],
                            'repositories': ['gitdb', 'GitPython'],
                            'all': False,
                            'verbose': False,
                            'shell': False,
                            'venv': None,
                            'python': False,
                            'raise_errors': False
                        },
                        'hello_world2': {
                            'commands': ['git fetch --all --tags --prune', 'git pull'],
                            'description': "Hello world",
                            'tags': [],
                            'repositories': ['gitdb', 'GitPython'],
                            'all': False,
                            'verbose': False,
                            'shell': False,
                            'venv': None,
                            'python': False,
                            'raise_errors': False
                        }
                    },
                    'constants': {
                        'HELLO': 'world',
                        "I": 'am',
                        'A': 'test'
                    }
                }
            )
            self.assertCountEqual(
                self.context.repositories,
                {
                    "gameta": {
                        "url": "https://github.com/testing/gameta.git",
                        "path": ".",
                        "tags": [
                            "metarepo"
                        ],
                        '__metarepo__': True
                    },
                    "genisys": {
                        "url": "https://github.com/testing/genisys.git",
                        "path": "core/genisys",
                        "tags": [
                            "core",
                            "templating"
                        ],
                        '__metarepo__': False
                    },
                    "genisys-testing": {
                        "url": "https://github.com/testing/genisys-testing.git",
                        "path": "core/genisys-testing",
                        "tags": [
                            "core",
                            "testing",
                            "developer"
                        ],
                        '__metarepo__': False
                    }
                }
            )
            self.assertCountEqual(
                self.context.tags,
                {
                    'core': ['genisys-testing', 'genisys'],
                    'testing': ['genisys-testing'],
                    'developer': ['genisys-testing'],
                    'templating': ['genisys'],
                    'metarepo': ['gameta']
                }
            )
            self.assertTrue(self.context.is_metarepo)

            self.assertCountEqual(
                self.context.commands,
                {
                    'hello_world': {
                        'commands': ['git fetch --all --tags --prune', 'git pull'],
                        'tags': [],
                        'repositories': ['gitdb', 'GitPython'],
                        'verbose': False,
                        'shell': False,
                        'raise_errors': False
                    },
                    'hello_world2': {
                        'commands': ['git fetch --all --tags --prune', 'git pull'],
                        'tags': [],
                        'repositories': ['gitdb', 'GitPython'],
                        'verbose': False,
                        'shell': False,
                        'raise_errors': False
                    }
                }
            )

            self.assertCountEqual(
                self.context.constants,
                {
                    'HELLO': "world",
                    "I": 'am',
                    'A': 'test'
                }
            )

            self.assertCountEqual(
                self.context.gitignore_data,
                ['HelloWorld\n', '.env\n', 'env\n']
            )

    def test_gameta_context_load_no_meta_file(self):
        with self.runner.isolated_filesystem() as f:
            self.context.project_dir = f
            self.context.load()
            self.assertEqual(self.context.repositories, {})
            self.assertEqual(self.context.commands, {})
            self.assertEqual(self.context.tags, {})
            self.assertFalse(self.context.is_metarepo)
            self.assertEqual(self.context.gitignore_data, [])

    def test_gameta_context_load_wrongly_formed_meta_file(self):
        with self.runner.isolated_filesystem() as f:
            with open(join(f, '.gameta'), 'w') as m:
                json.dump(
                    {
                        "gameta": {
                            "url": "https://github.com/testing/gameta.git",
                            "path": ".",
                            "tags": [
                                "metarepo"
                            ],
                            '__metarepo__': True
                        },
                        "genisys": {
                            "url": "https://github.com/testing/genisys.git",
                            "path": "core/genisys",
                            "tags": [
                                "core",
                                "templating"
                            ],
                            '__metarepo__': False
                        },
                        "genisys-testing": {
                            "url": "https://github.com/testing/genisys-testing.git",
                            "path": "core/genisys-testing",
                            "tags": [
                                "core",
                                "testing",
                                "developer"
                            ],
                            '__metarepo__': False
                        }
                    },
                    m
                )
            self.context.project_dir = f
            self.context.load()
            self.assertEqual(self.context.repositories, {})
            self.assertEqual(self.context.commands, {})
            self.assertEqual(self.context.gitignore_data, [])

    def test_gameta_context_export_meta_file_non_existent(self):
        with self.runner.isolated_filesystem() as f:
            self.context.project_dir = f
            self.context.repositories = {
                "gameta": {
                    "url": "https://github.com/testing/gameta.git",
                    "path": ".",
                    "tags": [
                        "metarepo"
                    ],
                    '__metarepo__': True
                }
            }
            self.context.export()
            self.assertTrue(exists(join(f, '.gameta')))
            with open(join(f, '.gameta')) as f:
                self.assertEqual(
                    json.load(f),
                    {
                        "version": __version__,
                        'repositories': {
                            "gameta": {
                                "url": "https://github.com/testing/gameta.git",
                                "path": ".",
                                "tags": [
                                    "metarepo"
                                ],
                                '__metarepo__': True
                            }
                        }
                    }
                )

    def test_gameta_context_export_meta_file_empty(self):
        with self.runner.isolated_filesystem() as f:
            with open(join(f, '.gameta'), 'w') as m:
                json.dump({}, m)
            self.context.project_dir = f
            self.context.repositories = {
                "gameta": {
                    "url": "https://github.com/testing/gameta.git",
                    "path": ".",
                    "tags": [
                        "metarepo"
                    ],
                    '__metarepo__': True
                }
            }
            self.context.export()
            self.assertTrue(exists(join(f, '.gameta')))
            with open(join(f, '.gameta')) as f:
                self.assertEqual(
                    json.load(f),
                    {
                        "version": __version__,
                        'repositories': {
                            "gameta": {
                                "url": "https://github.com/testing/gameta.git",
                                "path": ".",
                                "tags": [
                                    "metarepo"
                                ],
                                '__metarepo__': True
                            }
                        }
                    }
                )

    def test_gameta_context_export_meta_file_populated(self):
        with self.runner.isolated_filesystem() as f:
            with open(join(f, '.gameta'), 'w') as m:
                json.dump(
                    {
                        "repositories": {
                            "gameta": {
                                "url": "https://github.com/testing/gameta.git",
                                "path": ".",
                                "tags": [
                                    "metarepo"
                                ]
                            }
                        }
                    }, m)
            self.context.project_dir = f
            self.context.repositories = {
                "genisys": {
                    "url": "https://github.com/testing/genisys.git",
                    "path": "core/genisys",
                    "tags": [
                        "core",
                        "templating"
                    ],
                    '__metarepo__': False
                },
                "genisys-testing": {
                    "url": "https://github.com/testing/genisys-testing.git",
                    "path": "core/genisys-testing",
                    "tags": [
                        "core",
                        "testing",
                        "developer"
                    ],
                    '__metarepo__': False
                },
            }
            self.context.commands = {
                'hello_world': {
                    'commands': ['git fetch --all --tags --prune', 'git pull'],
                    'tags': [],
                    'repositories': ['gitdb', 'GitPython'],
                    'verbose': False,
                    'shell': False,
                    'raise_errors': False
                },
                'hello_world2': {
                    'commands': ['git fetch --all --tags --prune', 'git pull'],
                    'tags': [],
                    'repositories': ['gitdb', 'GitPython'],
                    'verbose': False,
                    'shell': False,
                    'raise_errors': False
                }
            }
            self.context.constants = {
                'HELLO': "world",
                "I": 'am',
                'A': 'test'
            }
            self.context.export()
            self.assertTrue(exists(join(f, '.gameta')))
            with open(join(f, '.gameta')) as f:
                self.assertEqual(
                    json.load(f),
                    {
                        "version": __version__,
                        'repositories': {
                            "genisys": {
                                "url": "https://github.com/testing/genisys.git",
                                "path": "core/genisys",
                                "tags": [
                                    "core",
                                    "templating"
                                ],
                                '__metarepo__': False
                            },
                            "genisys-testing": {
                                "url": "https://github.com/testing/genisys-testing.git",
                                "path": "core/genisys-testing",
                                "tags": [
                                    "core",
                                    "testing",
                                    "developer"
                                ],
                                '__metarepo__': False
                            }
                        },
                        "commands": {
                            'hello_world': {
                                'commands': ['git fetch --all --tags --prune', 'git pull'],
                                'tags': [],
                                'repositories': ['gitdb', 'GitPython'],
                                'verbose': False,
                                'shell': False,
                                'raise_errors': False
                            },
                            'hello_world2': {
                                'commands': ['git fetch --all --tags --prune', 'git pull'],
                                'tags': [],
                                'repositories': ['gitdb', 'GitPython'],
                                'verbose': False,
                                'shell': False,
                                'raise_errors': False
                            }
                        },
                        "constants": {
                            'HELLO': "world",
                            "I": 'am',
                            'A': 'test'
                        }
                    }
                )

    def test_gameta_context_apply_command_to_all_repos(self):
        with self.runner.isolated_filesystem() as f:
            makedirs(join(f, 'core', 'genisys'))
            makedirs(join(f, 'core', 'genisys-testing'))
            with open('.gameta', 'w') as m:
                json.dump(
                    {
                        "version": __version__,
                        "repositories": {
                            "gameta": {
                                "url": "https://github.com/testing/gameta.git",
                                "path": ".",
                                "tags": [
                                    "metarepo"
                                ],
                                '__metarepo__': True
                            },
                            "genisys": {
                                "url": "https://github.com/testing/genisys.git",
                                "path": "core/genisys",
                                "tags": [
                                    "core",
                                    "templating"
                                ],
                                '__metarepo__': False
                            },
                            "genisys-testing": {
                                "url": "https://github.com/testing/genisys-testing.git",
                                "path": "core/genisys-testing",
                                "tags": [
                                    "core",
                                    "testing",
                                    "developer"
                                ],
                                '__metarepo__': False
                            }
                        }
                    }, m
                )
            self.context.project_dir = f
            self.context.load()
            for cwd, repo, repo_command in zip(
                    [f, join(f, 'core', 'genisys'), join(f, 'core', 'genisys-testing')],
                    ['gameta', 'genisys', 'genisys-testing'],
                    self.context.apply(['git fetch --all --tags --prune', 'git pull'])
            ):
                self.assertEqual(getcwd(), cwd)
                self.assertEqual(repo, repo_command[0])
                self.assertEqual(repo_command[1], ['git', 'fetch', '--all', '--tags', '--prune', '&&', 'git', 'pull'])

    def test_gameta_context_apply_command_to_selected_repos(self):
        with self.runner.isolated_filesystem() as f:
            makedirs(join(f, 'core', 'genisys'))
            makedirs(join(f, 'core', 'genisys-testing'))
            with open(join(f, '.gameta'), 'w') as m:
                json.dump(
                    {
                        "version": __version__,
                        "repositories": {
                            "gameta": {
                                "url": "https://github.com/testing/gameta.git",
                                "path": ".",
                                "tags": [
                                    "metarepo"
                                ],
                                '__metarepo__': False
                            },
                            "genisys": {
                                "url": "https://github.com/testing/genisys.git",
                                "path": "core/genisys",
                                "tags": [
                                    "core",
                                    "templating"
                                ],
                                '__metarepo__': False
                            },
                            "genisys-testing": {
                                "url": "https://github.com/testing/genisys-testing.git",
                                "path": "core/genisys-testing",
                                "tags": [
                                    "core",
                                    "testing",
                                    "developer"
                                ],
                                '__metarepo__': False
                            }
                        }
                    }, m
                )
            self.context.project_dir = f
            self.context.load()
            for cwd, repo, repo_command in zip(
                    [f, join(f, 'core', 'genisys')],
                    ['gameta', 'genisys', 'genisys-testing'],
                    self.context.apply(['git fetch --all --tags --prune', 'git pull'], ['genisys', 'gameta'])
            ):
                self.assertEqual(getcwd(), cwd)
                self.assertEqual(repo, repo_command[0])
                self.assertEqual(
                    repo_command[1],
                    [getenv('SHELL', '/bin/sh'), '-c', 'git fetch --all --tags --prune && git pull']
                )

    def test_gameta_context_apply_command_in_separate_shell(self):
        with self.runner.isolated_filesystem() as f:
            makedirs(join(f, 'core', 'genisys'))
            makedirs(join(f, 'core', 'genisys-testing'))
            with open(join(f, '.gameta'), 'w') as m:
                json.dump(
                    {
                        "version": __version__,
                        "repositories": {
                            "gameta": {
                                "url": "https://github.com/testing/gameta.git",
                                "path": ".",
                                "tags": [
                                    "metarepo"
                                ],
                                '__metarepo__': False
                            },
                            "genisys": {
                                "url": "https://github.com/testing/genisys.git",
                                "path": "core/genisys",
                                "tags": [
                                    "core",
                                    "templating"
                                ],
                                '__metarepo__': False
                            },
                            "genisys-testing": {
                                "url": "https://github.com/testing/genisys-testing.git",
                                "path": "core/genisys-testing",
                                "tags": [
                                    "core",
                                    "testing",
                                    "developer"
                                ],
                                '__metarepo__': False
                            }
                        },
                        "commands": {}
                    }, m
                )
            self.context.project_dir = f
            self.context.load()
            for cwd, repo, repo_command in zip(
                    [f, join(f, 'core', 'genisys')],
                    ['gameta', 'genisys', 'genisys-testing'],
                    self.context.apply(['git fetch --all --tags --prune', 'git pull'], shell=True)
            ):
                self.assertEqual(getcwd(), cwd)
                self.assertEqual(repo, repo_command[0])
                self.assertEqual(
                    repo_command[1],
                    [getenv('SHELL', '/bin/sh'), '-c', 'git fetch --all --tags --prune && git pull']
                )

    def test_gameta_context_apply_with_parameter_substitution(self):
        with self.runner.isolated_filesystem() as f:
            makedirs(join(f, 'core', 'genisys'))
            makedirs(join(f, 'core', 'genisys-testing'))
            with open(join(f, '.gameta'), 'w') as m:
                json.dump(
                    {
                        "version": __version__,
                        "repositories": {
                            "gameta": {
                                "url": "https://github.com/test/gameta.git",
                                "path": ".",
                                "tags": [
                                    "metarepo"
                                ],
                                '__metarepo__': False
                            },
                            "genisys": {
                                "url": "https://github.com/test/genisys.git",
                                "path": "core/genisys",
                                "tags": [
                                    "core",
                                    "templating"
                                ],
                                '__metarepo__': False
                            },
                            "genisys-testing": {
                                "url": "https://github.com/test/genisys-testing.git",
                                "path": "core/genisys-testing",
                                "tags": [
                                    "core",
                                    "testing",
                                    "developer"
                                ],
                                '__metarepo__': False
                            }
                        },
                        "commands": {}
                    }, m
                )
            self.context.project_dir = f
            self.context.load()
            for cwd, test_output, repo, repo_command in zip(
                    [f, join(f, 'core', 'genisys'), join(f, 'core', 'genisys-testing')],
                    [
                        ['git', 'clone', 'https://github.com/test/gameta.git', '.'],
                        ['git', 'clone', 'https://github.com/test/genisys.git', 'core/genisys'],
                        ['git', 'clone', 'https://github.com/test/genisys-testing.git', 'core/genisys-testing']
                    ],
                    ['gameta', 'genisys', 'genisys-testing'],
                    self.context.apply(['git clone {url} {path}'])
            ):
                self.assertEqual(getcwd(), cwd)
                self.assertEqual(repo, repo_command[0])
                self.assertEqual(repo_command[1], test_output)

    def test_gameta_context_apply_with_constants_substitution(self):
        with self.runner.isolated_filesystem() as f:
            makedirs(join(f, 'core', 'genisys'))
            makedirs(join(f, 'core', 'genisys-testing'))
            with open(join(f, '.gameta'), 'w') as m:
                json.dump(
                    {
                        "version": __version__,
                        "repositories": {
                            "gameta": {
                                "url": "https://github.com/test/gameta.git",
                                "path": ".",
                                "tags": [
                                    "metarepo"
                                ],
                                '__metarepo__': False
                            },
                            "genisys": {
                                "url": "https://github.com/test/genisys.git",
                                "path": "core/genisys",
                                "tags": [
                                    "core",
                                    "templating"
                                ],
                                '__metarepo__': False
                            },
                            "genisys-testing": {
                                "url": "https://github.com/test/genisys-testing.git",
                                "path": "core/genisys-testing",
                                "tags": [
                                    "core",
                                    "testing",
                                    "developer"
                                ],
                                '__metarepo__': False
                            }
                        },
                        "commands": {},
                        "constants": {
                            "BRANCH": "hello"
                        }
                    }, m
                )
            self.context.project_dir = f
            self.context.load()
            for cwd, test_output, repo, repo_command in zip(
                    [f, join(f, 'core', 'genisys'), join(f, 'core', 'genisys-testing')],
                    [
                        ['git', 'checkout', 'hello'],
                        ['git', 'checkout', 'hello'],
                        ['git', 'checkout', 'hello']
                    ],
                    ['gameta', 'genisys', 'genisys-testing'],
                    self.context.apply(['git checkout {BRANCH}'])
            ):
                self.assertEqual(getcwd(), cwd)
                self.assertEqual(repo, repo_command[0])
                self.assertEqual(repo_command[1], test_output)

    def test_gameta_context_apply_with_environment_variable_substitution(self):
        with self.runner.isolated_filesystem() as f:
            makedirs(join(f, 'core', 'genisys'))
            makedirs(join(f, 'core', 'genisys-testing'))
            with open(join(f, '.gameta'), 'w') as m:
                json.dump(
                    {
                        "version": __version__,
                        "repositories": {
                            "gameta": {
                                "url": "https://github.com/test/gameta.git",
                                "path": ".",
                                "tags": [
                                    "metarepo"
                                ],
                                '__metarepo__': False
                            },
                            "genisys": {
                                "url": "https://github.com/test/genisys.git",
                                "path": "core/genisys",
                                "tags": [
                                    "core",
                                    "templating"
                                ],
                                '__metarepo__': False
                            },
                            "genisys-testing": {
                                "url": "https://github.com/test/genisys-testing.git",
                                "path": "core/genisys-testing",
                                "tags": [
                                    "core",
                                    "testing",
                                    "developer"
                                ],
                                '__metarepo__': False
                            }
                        },
                        "commands": {},
                        "constants": {
                            "BRANCH": "hello"
                        }
                    }, m
                )
            self.context.project_dir = f
            self.context.env_vars['$BRANCH'] = "world"
            self.context.load()
            for cwd, test_output, repo, repo_command in zip(
                    [f, join(f, 'core', 'genisys'), join(f, 'core', 'genisys-testing')],
                    [
                        ['git', 'checkout', 'world'],
                        ['git', 'checkout', 'world'],
                        ['git', 'checkout', 'world']
                    ],
                    ['gameta', 'genisys', 'genisys-testing'],
                    self.context.apply(['git checkout {$BRANCH}'])
            ):
                self.assertEqual(getcwd(), cwd)
                self.assertEqual(repo, repo_command[0])
                self.assertEqual(repo_command[1], test_output)

    def test_gameta_context_apply_with_all_substitutions(self):
        with self.runner.isolated_filesystem() as f:
            makedirs(join(f, 'core', 'genisys'))
            makedirs(join(f, 'core', 'genisys-testing'))
            with open(join(f, '.gameta'), 'w') as m:
                json.dump(
                    {
                        "version": __version__,
                        "repositories": {
                            "gameta": {
                                "url": "https://github.com/test/gameta.git",
                                "path": ".",
                                "tags": [
                                    "metarepo"
                                ],
                                '__metarepo__': False
                            },
                            "genisys": {
                                "url": "https://github.com/test/genisys.git",
                                "path": "core/genisys",
                                "tags": [
                                    "core",
                                    "templating"
                                ],
                                '__metarepo__': False
                            },
                            "genisys-testing": {
                                "url": "https://github.com/test/genisys-testing.git",
                                "path": "core/genisys-testing",
                                "tags": [
                                    "core",
                                    "testing",
                                    "developer"
                                ],
                                '__metarepo__': False
                            }
                        },
                        "commands": {},
                        "constants": {
                            "BRANCH": "hello"
                        }
                    }, m
                )
            self.context.project_dir = f
            self.context.env_vars['$ORIGIN'] = "world"
            self.context.load()
            for cwd, test_output, repo, repo_command in zip(
                    [f, join(f, 'core', 'genisys'), join(f, 'core', 'genisys-testing')],
                    [
                        [
                            'git', 'clone', 'https://github.com/test/gameta.git', '.', '&&',
                            'git', 'checkout', 'hello', '&&',
                            'git', 'push', 'world', 'hello'
                        ],
                        [
                            'git', 'clone', 'https://github.com/test/genisys.git', 'core/genisys', '&&',
                            'git', 'checkout', 'hello', '&&',
                            'git', 'push', 'world', 'hello'
                        ],
                        [
                            'git', 'clone', 'https://github.com/test/genisys-testing.git', 'core/genisys-testing', '&&',
                            'git', 'checkout', 'hello', '&&',
                            'git', 'push', 'world', 'hello'
                        ],
                    ],
                    ['gameta', 'genisys', 'genisys-testing'],
                    self.context.apply(
                        ['git clone {url} {path}', 'git checkout {BRANCH}', 'git push {$ORIGIN} {BRANCH}']
                    )
            ):
                self.assertEqual(getcwd(), cwd)
                self.assertEqual(repo, repo_command[0])
                self.assertEqual(repo_command[1], test_output)

    def test_gameta_context_apply_command_for_python_execution(self):
        with self.runner.isolated_filesystem() as f:
            makedirs(join(f, 'core', 'genisys'))
            makedirs(join(f, 'core', 'genisys-testing'))
            with open(join(f, '.gameta'), 'w') as m:
                json.dump(
                    {
                        "version": __version__,
                        "repositories": {
                            "gameta": {
                                "url": "https://github.com/test/gameta.git",
                                "path": ".",
                                "tags": [
                                    "metarepo"
                                ],
                                '__metarepo__': False
                            },
                            "genisys": {
                                "url": "https://github.com/test/genisys.git",
                                "path": "core/genisys",
                                "tags": [
                                    "core",
                                    "templating"
                                ],
                                '__metarepo__': False
                            },
                            "genisys-testing": {
                                "url": "https://github.com/test/genisys-testing.git",
                                "path": "core/genisys-testing",
                                "tags": [
                                    "core",
                                    "testing",
                                    "developer"
                                ],
                                '__metarepo__': False
                            }
                        },
                        "commands": {},
                        "constants": {
                            "ENCRYPTION_FILE_NAME": 'encryption.txt',
                            "KEY_LEN": 16
                        }
                    }, m
                )
            self.context.project_dir = f
            self.context.load()
            for cwd, repo, repo_command in zip(
                    [f, join(f, 'core', 'genisys'), join(f, 'core', 'genisys-testing')],
                    ['gameta', 'genisys', 'genisys-testing'],
                    self.context.apply(
                        [
                            'from random import choice\n'
                            'from string import ascii_lowercase, ascii_uppercase, digits, punctuation\n'
                            'with open("{ENCRYPTION_FILE_NAME}", "w") as f:\n'
                            '\tf.write("".join([choice(ascii_lowercase + ascii_uppercase + digits + punctuation) '
                            'for _ in range({KEY_LEN})]))'
                        ],
                        python=True
                    )
            ):
                self.assertEqual(getcwd(), cwd)
                self.assertEqual(repo, repo_command[0])
                self.assertEqual(
                    repo_command[1],
                    [
                        getenv('SHELL', '/bin/sh'), '-c',
                        "python3 -c \'"
                        'from random import choice\n'
                        'from string import ascii_lowercase, ascii_uppercase, digits, punctuation\n'
                        'with open("encryption.txt", "w") as f:\n'
                        '\tf.write("".join([choice(ascii_lowercase + ascii_uppercase + digits + punctuation) '
                        "for _ in range(16)]))'"
                    ]
                )

    def test_gameta_context_apply_shell_command_with_virtualenv(self):
        with self.runner.isolated_filesystem() as f:
            makedirs(join(f, 'core', 'genisys'))
            makedirs(join(f, 'core', 'genisys-testing'))
            with open(join(f, '.gameta'), 'w') as m:
                json.dump(
                    {
                        "version": __version__,
                        "repositories": {
                            "gameta": {
                                "url": "https://github.com/testing/gameta.git",
                                "path": ".",
                                "tags": [
                                    "metarepo"
                                ],
                                '__metarepo__': False
                            },
                            "genisys": {
                                "url": "https://github.com/testing/genisys.git",
                                "path": "core/genisys",
                                "tags": [
                                    "core",
                                    "templating"
                                ],
                                '__metarepo__': False
                            },
                            "genisys-testing": {
                                "url": "https://github.com/testing/genisys-testing.git",
                                "path": "core/genisys-testing",
                                "tags": [
                                    "core",
                                    "testing",
                                    "developer"
                                ],
                                '__metarepo__': False
                            }
                        },
                        "commands": {},
                        "virtualenvs": {
                            'test': join(f, 'test')
                        }
                    }, m
                )
            self.context.project_dir = f
            self.context.load()
            for cwd, repo, repo_command in zip(
                    [f, join(f, 'core', 'genisys')],
                    ['gameta', 'genisys', 'genisys-testing'],
                    self.context.apply(['git fetch --all --tags --prune', 'git pull'], venv='test')
            ):
                self.assertEqual(getcwd(), cwd)
                self.assertEqual(repo, repo_command[0])
                self.assertEqual(
                    repo_command[1],
                    [
                        getenv('SHELL', '/bin/sh'), '-c',
                        f". {join(f, 'test', 'bin', 'activate')} && "
                        'git fetch --all --tags --prune && git pull']
                )

    def test_gameta_context_apply_python_scripts_with_virtualenv(self):
        with self.runner.isolated_filesystem() as f:
            makedirs(join(f, 'core', 'genisys'))
            makedirs(join(f, 'core', 'genisys-testing'))
            with open(join(f, '.gameta'), 'w') as m:
                json.dump(
                    {
                        "version": __version__,
                        "repositories": {
                            "gameta": {
                                "url": "https://github.com/test/gameta.git",
                                "path": ".",
                                "tags": [
                                    "metarepo"
                                ],
                                '__metarepo__': False
                            },
                            "genisys": {
                                "url": "https://github.com/test/genisys.git",
                                "path": "core/genisys",
                                "tags": [
                                    "core",
                                    "templating"
                                ],
                                '__metarepo__': False
                            },
                            "genisys-testing": {
                                "url": "https://github.com/test/genisys-testing.git",
                                "path": "core/genisys-testing",
                                "tags": [
                                    "core",
                                    "testing",
                                    "developer"
                                ],
                                '__metarepo__': False
                            }
                        },
                        "commands": {},
                        "constants": {
                            "ENCRYPTION_FILE_NAME": 'encryption.txt',
                            "KEY_LEN": 16
                        },
                        "virtualenvs": {
                            'test': join(f, 'test')
                        }
                    }, m
                )
            self.context.project_dir = f
            self.context.load()
            for cwd, repo, repo_command in zip(
                    [f, join(f, 'core', 'genisys'), join(f, 'core', 'genisys-testing')],
                    ['gameta', 'genisys', 'genisys-testing'],
                    self.context.apply(
                        [
                            'from random import choice\n'
                            'from string import ascii_lowercase, ascii_uppercase, digits, punctuation\n'
                            'with open("{ENCRYPTION_FILE_NAME}", "w") as f:\n'
                            '\tf.write("".join([choice(ascii_lowercase + ascii_uppercase + digits + punctuation) '
                            'for _ in range({KEY_LEN})]))'
                        ],
                        python=True,
                        venv='test'
                    )
            ):
                self.assertEqual(getcwd(), cwd)
                self.assertEqual(repo, repo_command[0])
                self.assertEqual(
                    repo_command[1],
                    [
                        getenv('SHELL', '/bin/sh'), '-c',
                        f". {join(f, 'test', 'bin', 'activate')} && "
                        "python3 -c \'"
                        'from random import choice\n'
                        'from string import ascii_lowercase, ascii_uppercase, digits, punctuation\n'
                        'with open("encryption.txt", "w") as f:\n'
                        '\tf.write("".join([choice(ascii_lowercase + ascii_uppercase + digits + punctuation) '
                        "for _ in range(16)]))'"
                    ]
                )

    def test_gameta_context_generate_parameters_complete_parameter_set_generated(self):
        self.context.repositories = {
            "genisys": {
                "url": "https://github.com/testing/genisys.git",
                "path": "core/genisys",
                "tags": [
                    "core",
                    "templating"
                ],
                '__metarepo__': False
            },
            "genisys-testing": {
                "url": "https://github.com/testing/genisys-testing.git",
                "path": "core/genisys-testing",
                "tags": [
                    "core",
                    "testing",
                    "developer"
                ],
                '__metarepo__': False
            },
        }
        self.context.commands = {
            'hello_world': {
                'commands': ['git fetch --all --tags --prune', 'git pull'],
                'tags': [],
                'repositories': ['gitdb', 'GitPython'],
                'verbose': False,
                'shell': False,
                'raise_errors': False
            },
            'hello_world2': {
                'commands': ['git fetch --all --tags --prune', 'git pull'],
                'tags': [],
                'repositories': ['gitdb', 'GitPython'],
                'verbose': False,
                'shell': False,
                'raise_errors': False
            }
        }
        self.context.constants = {
            'HELLO': "world",
            "I": 'am',
            'A': 'test'
        }
        self.context.env_vars = {
            '$HELLO': 'world',
            '$I': 'am',
            '$A': 'test'
        }

        self.assertEqual(
            self.context.generate_parameters('genisys', self.context.repositories['genisys']),
            {
                "url": "https://github.com/testing/genisys.git",
                "path": "core/genisys",
                "tags": [
                    "core",
                    "templating"
                ],
                '__metarepo__': False,
                'HELLO': "world",
                "I": 'am',
                'A': 'test',
                '$HELLO': 'world',
                '$I': 'am',
                '$A': 'test'
            }
        )

    def test_gameta_context_generate_parameters_complete_parameter_set_generated_with_python_variables(self):
        self.context.repositories = {
            "genisys": {
                "url": "https://github.com/testing/genisys.git",
                "path": "core/genisys",
                "tags": [
                    "core",
                    "templating"
                ],
                '__metarepo__': False
            },
            "genisys-testing": {
                "url": "https://github.com/testing/genisys-testing.git",
                "path": "core/genisys-testing",
                "tags": [
                    "core",
                    "testing",
                    "developer"
                ],
                '__metarepo__': False
            },
        }
        self.context.commands = {
            'hello_world': {
                'commands': ['git fetch --all --tags --prune', 'git pull'],
                'tags': [],
                'repositories': ['gitdb', 'GitPython'],
                'verbose': False,
                'shell': False,
                'raise_errors': False
            },
            'hello_world2': {
                'commands': ['git fetch --all --tags --prune', 'git pull'],
                'tags': [],
                'repositories': ['gitdb', 'GitPython'],
                'verbose': False,
                'shell': False,
                'raise_errors': False
            }
        }
        self.context.constants = {
            'HELLO': "world",
            "I": 'am',
            'A': 'test'
        }
        self.context.env_vars = {
            '$HELLO': 'world',
            '$I': 'am',
            '$A': 'test'
        }

        self.assertCountEqual(
            self.context.generate_parameters('genisys', self.context.repositories['genisys'], python=True),
            {
                "url": "https://github.com/testing/genisys.git",
                "path": "core/genisys",
                "tags": [
                    "core",
                    "templating"
                ],
                '__metarepo__': False,
                'HELLO': "world",
                "I": 'am',
                'A': 'test',
                '$HELLO': 'world',
                '$I': 'am',
                '$A': 'test',
                '__repos__': self.context.repositories
            }
        )

    def test_gameta_context_generate_parameters_constants_substituted_by_environment_variables(self):
        self.context.repositories = {
            "genisys": {
                "url": "https://github.com/testing/genisys.git",
                "path": "core/genisys",
                "tags": [
                    "core",
                    "templating"
                ],
                '__metarepo__': False
            },
            "genisys-testing": {
                "url": "https://github.com/testing/genisys-testing.git",
                "path": "core/genisys-testing",
                "tags": [
                    "core",
                    "testing",
                    "developer"
                ],
                '__metarepo__': False
            },
        }
        self.context.commands = {
            'hello_world': {
                'commands': ['git fetch --all --tags --prune', 'git pull'],
                'tags': [],
                'repositories': ['gitdb', 'GitPython'],
                'verbose': False,
                'shell': False,
                'raise_errors': False
            },
            'hello_world2': {
                'commands': ['git fetch --all --tags --prune', 'git pull'],
                'tags': [],
                'repositories': ['gitdb', 'GitPython'],
                'verbose': False,
                'shell': False,
                'raise_errors': False
            }
        }
        self.context.constants = {
            '$HELLO': "world",
            "$I": 'am',
            '$A': 'test'
        }
        self.context.env_vars = {
            '$HELLO': 'hello_world',
            '$I': 'hello_world',
            '$A': 'hello_world'
        }

        self.assertCountEqual(
            self.context.generate_parameters('genisys', self.context.repositories['genisys'], python=True),
            {
                "url": "https://github.com/testing/genisys.git",
                "path": "core/genisys",
                "tags": [
                    "core",
                    "templating"
                ],
                '__metarepo__': False,
                '$HELLO': 'hello_world',
                '$I': 'hello_world',
                '$A': 'hello_world',
                '__repos__': json.dumps(self.context.repositories)
            }
        )

    def test_gameta_context_generate_parameters_parameters_substituted_by_environment_variables(self):
        self.context.repositories = {
            "genisys": {
                "url": "https://github.com/testing/genisys.git",
                "path": "core/genisys",
                "tags": [
                    "core",
                    "templating"
                ],
                '__metarepo__': False,
                'branch': '{$BRANCH}'
            },
            "genisys-testing": {
                "url": "https://github.com/testing/genisys-testing.git",
                "path": "core/genisys-testing",
                "tags": [
                    "core",
                    "testing",
                    "developer"
                ],
                '__metarepo__': False,
                'branch': 'master'
            },
        }
        self.context.commands = {
            'hello_world': {
                'commands': ['git fetch --all --tags --prune', 'git pull'],
                'tags': [],
                'repositories': ['gitdb', 'GitPython'],
                'verbose': False,
                'shell': False,
                'raise_errors': False
            },
            'hello_world2': {
                'commands': ['git fetch --all --tags --prune', 'git pull'],
                'tags': [],
                'repositories': ['gitdb', 'GitPython'],
                'verbose': False,
                'shell': False,
                'raise_errors': False
            }
        }
        self.context.constants = {
            '$HELLO': "world",
            "$I": 'am',
            '$A': 'test'
        }
        self.context.env_vars = {
            '$BRANCH': 'test',
            '$HELLO': 'hello_world',
            '$I': 'hello_world',
            '$A': 'hello_world'
        }

        self.assertCountEqual(
            self.context.generate_parameters('genisys', self.context.repositories['genisys'], python=True),
            {
                "url": "https://github.com/testing/genisys.git",
                "path": "core/genisys",
                "tags": [
                    "core",
                    "templating"
                ],
                'branch': 'test',
                '__metarepo__': False,
                '$HELLO': 'hello_world',
                '$I': 'hello_world',
                '$A': 'hello_world',
                '$BRANCH': 'test',
                '__repos__': json.dumps({
                    'genisys': {
                        "url": "https://github.com/testing/genisys.git",
                        "path": "core/genisys",
                        "tags": [
                            "core",
                            "templating"
                        ],
                        '__metarepo__': False,
                        'branch': 'test'
                    },
                    "genisys-testing": {
                        "url": "https://github.com/testing/genisys-testing.git",
                        "path": "core/genisys-testing",
                        "tags": [
                            "core",
                            "testing",
                            "developer"
                        ],
                        '__metarepo__': False,
                        'branch': 'master'
                    }
                })
            }
        )
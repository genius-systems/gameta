from os import makedirs, symlink, getcwd, listdir, getenv, environ
from os.path import join, basename
from unittest import TestCase, skipIf

from click.testing import CliRunner

from gameta.base.commands import GametaCommand, CommandConfig, SHELL, Runner
from gameta.base.errors import CommandError


class TestGametaCommand(TestCase):
    def setUp(self) -> None:
        self.command = GametaCommand

    def test_gameta_command_generate_full_pipeline_with_virtualenv(self):
        test_inputs = {
            'commands': ['cp {FILE} {DEST}'],
            'params': {'FILE': 'hello.yml', 'DEST': "test/hello.yml"},
            'config': {
                'shell': False,
                'venv': 'path/to/venv'
            }
        }
        self.command = GametaCommand(
            commands=test_inputs['commands'],
            params=test_inputs['params'],
            config=CommandConfig(**test_inputs['config'])
        )
        with self.command.generate() as c:
            self.assertEqual(c, [f'{SHELL}', '-c', '. path/to/venv/bin/activate && cp hello.yml test/hello.yml'])
            self.assertEqual(self.command.commands, test_inputs['commands'])

    def test_gameta_command_generate_full_pipeline_with_shell(self):
        test_inputs = {
            'commands': ['cp {FILE} {DEST}'],
            'params': {'FILE': 'hello.yml', 'DEST': "test/hello.yml"},
            'config': {
                'shell': True,
                'venv': None
            }
        }
        self.command = GametaCommand(
            commands=test_inputs['commands'],
            params=test_inputs['params'],
            config=CommandConfig(**test_inputs['config'])
        )
        with self.command.generate() as c:
            self.assertEqual(c, [f'{SHELL}', '-c', 'cp hello.yml test/hello.yml'])
            self.assertEqual(self.command.commands, test_inputs['commands'])

    def test_gameta_command_generate_full_pipeline_with_default_configuration(self):
        test_inputs = {
            'commands': ['cp {FILE} {DEST}'],
            'params': {'FILE': 'hello.yml', 'DEST': "test/hello.yml"},
            'config': {
                'shell': False,
                'venv': None
            }
        }
        self.command = GametaCommand(
            commands=test_inputs['commands'],
            params=test_inputs['params'],
            config=CommandConfig(**test_inputs['config'])
        )
        with self.command.generate() as c:
            self.assertEqual(c, ['cp', 'hello.yml', 'test/hello.yml'])
            self.assertEqual(self.command.commands, test_inputs['commands'])

    def test_gameta_command_substitute_no_matching_parameter(self):
        test_inputs = {
            'commands': ['docker-compose -f {FILE} up -d'],
            'params': {'HELLO': 'hello.yml'},
            'config': {
                'shell': False,
                'venv': 'path/to/venv'
            }
        }
        self.command = GametaCommand(
            commands=test_inputs['commands'],
            params=test_inputs['params'],
            config=CommandConfig(**test_inputs['config'])
        )
        with self.assertRaisesRegex(CommandError, "Parameter FILE was not provided"):
            self.command.substitute(),

    def test_gameta_command_substitute_single_parameter(self):
        test_inputs = {
            'commands': ['docker-compose -f {FILE} up -d'],
            'params': {'FILE': 'hello.yml'},
            'config': {
                'shell': False,
                'venv': 'path/to/venv'
            }
        }
        self.command = GametaCommand(
            commands=test_inputs['commands'],
            params=test_inputs['params'],
            config=CommandConfig(**test_inputs['config'])
        )
        self.assertEqual(
            self.command.substitute(),
            ['docker-compose -f hello.yml up -d']
        )
        self.assertEqual(self.command.commands, test_inputs['commands'])

    def test_gameta_command_substitute_multiple_parameters(self):
        test_inputs = {
            'commands': ['cp {FILE} {DEST}'],
            'params': {'FILE': 'hello.yml', 'DEST': "test/hello.yml"},
            'config': {
                'shell': False,
                'venv': 'path/to/venv'
            }
        }
        self.command = GametaCommand(
            commands=test_inputs['commands'],
            params=test_inputs['params'],
            config=CommandConfig(**test_inputs['config'])
        )
        self.assertEqual(
            self.command.substitute(),
            ['cp hello.yml test/hello.yml']
        )
        self.assertEqual(self.command.commands, test_inputs['commands'])

    def test_gameta_command_virtualenv_shell_command(self):
        test_inputs = {
            'commands': ['docker-compose up -d'],
            'params': {},
            'config': {
                'shell': False,
                'venv': 'path/to/venv'
            }
        }
        self.command = GametaCommand(
            commands=test_inputs['commands'],
            params=test_inputs['params'],
            config=CommandConfig(**test_inputs['config'])
        )
        self.assertEqual(
            self.command.virtualenv(test_inputs['commands']),
            ['. path/to/venv/bin/activate'] + test_inputs['commands']
        )

    def test_gameta_command_shell_bash_function(self):
        test_inputs = {
            'commands': [
                "generate_version_info () { echo \"HELLO_WORLD=\\\"$1\\\"\" >> output.env; }; "
                "generate_version_info $(git rev-parse --abbrev-ref HEAD)"
            ],
            'params': {},
            'config': {
                'shell': False,
                'venv': 'path/to/venv'
            }
        }
        self.command = GametaCommand(
            commands=test_inputs['commands'],
            params=test_inputs['params'],
            config=CommandConfig(**test_inputs['config'])
        )
        self.assertEqual(
            self.command.shell(test_inputs['commands']),
            f"{SHELL} -c 'generate_version_info () "
            '{ echo \"HELLO_WORLD=\\\"$1\\\"\" >> output.env; }; '
            f"generate_version_info $(git rev-parse --abbrev-ref HEAD)'"
        )

    def test_gameta_command_shell_pipe_command(self):
        test_inputs = {
            'commands': [
                'aws ecr get-login-password --region region | '
                'docker login --username AWS --password-stdin aws_account_id.dkr.ecr.region.amazonaws.com'
            ],
            'params': {},
            'config': {
                'shell': False,
                'venv': 'path/to/venv'
            }
        }
        self.command = GametaCommand(
            commands=test_inputs['commands'],
            params=test_inputs['params'],
            config=CommandConfig(**test_inputs['config'])
        )
        self.assertEqual(
            self.command.shell(test_inputs['commands']),
            f"{SHELL} -c 'aws ecr get-login-password --region region | "
            f"docker login --username AWS --password-stdin aws_account_id.dkr.ecr.region.amazonaws.com'"
        )

    def test_gameta_command_shell_multiple_commands(self):
        test_inputs = {
            'commands': [
                'git clone https://github.com/libgit2/libgit2',
                'git fetch --all --tags --prune',
                'git merge'
            ],
            'params': {},
            'config': {
                'shell': False,
                'venv': 'path/to/venv'
            }
        }
        self.command = GametaCommand(
            commands=test_inputs['commands'],
            params=test_inputs['params'],
            config=CommandConfig(**test_inputs['config'])
        )
        self.assertEqual(
            self.command.shell(test_inputs['commands']),
            f"{SHELL} -c 'git clone https://github.com/libgit2/libgit2 && "
            f"git fetch --all --tags --prune && git merge'"
        )

    def test_gameta_command_shell_with_semicolon_separator(self):
        test_inputs = {
            'commands': [
                'git clone https://github.com/libgit2/libgit2',
                'git fetch --all --tags --prune',
                'git merge'
            ],
            'params': {},
            'config': {
                'shell': False,
                'venv': 'path/to/venv',
                'sep': ';'
            }
        }
        self.command = GametaCommand(
            commands=test_inputs['commands'],
            params=test_inputs['params'],
            config=CommandConfig(**test_inputs['config'])
        )
        self.assertEqual(
            self.command.shell(test_inputs['commands']),
            f"{SHELL} -c 'git clone https://github.com/libgit2/libgit2; "
            f"git fetch --all --tags --prune; git merge'"
        )

    def test_gameta_command_shell_with_double_pipe_separator(self):
        test_inputs = {
            'commands': [
                'git clone https://github.com/libgit2/libgit2',
                'git fetch --all --tags --prune',
                'git merge'
            ],
            'params': {},
            'config': {
                'shell': False,
                'venv': 'path/to/venv',
                'sep': '||'
            }
        }
        self.command = GametaCommand(
            commands=test_inputs['commands'],
            params=test_inputs['params'],
            config=CommandConfig(**test_inputs['config'])
        )
        self.assertEqual(
            self.command.shell(test_inputs['commands']),
            f"{SHELL} -c 'git clone https://github.com/libgit2/libgit2 || "
            f"git fetch --all --tags --prune || git merge'"
        )

    def test_gameta_command_tokenise_valid_command(self):
        self.assertEqual(
            self.command.tokenise('git clone https://github.com/libgit2/libgit2'),
            ['git', 'clone', 'https://github.com/libgit2/libgit2']
        )

    def test_gameta_command_tokenise_shell_command(self):
        self.assertEqual(
            self.command.tokenise(
                f'{SHELL} -c "git clone https://github.com/libgit2/libgit2 && '
                f'git fetch --all --tags --prune && git merge"'
            ),
            [
                f'{SHELL}', '-c',
                'git clone https://github.com/libgit2/libgit2 && git fetch --all --tags --prune && git merge'
            ]
        )

    def test_gameta_command_tokenise_empty_string(self):
        self.assertEqual(self.command.tokenise(''), [])


class TestRunner(TestCase):
    def setUp(self) -> None:
        self.runner = CliRunner()

    def test_runner_environment_variables_properly_extracted(self):
        self.assertTrue(all(i[0] == '$' for i in Runner.env_vars))

    @skipIf('HOME' not in environ, 'HOME variable is not present')
    def test_runner_environment_variables_exists(self):
        self.assertTrue('$HOME' in Runner.env_vars)

    def test_runner_cd_to_valid_directory(self):
        with self.runner.isolated_filesystem() as f:
            makedirs(join(f, 'test', 'hello', 'world'))
            makedirs(join(f, 'i', 'am'))
            makedirs(join(f, 'a'))

            gameta_runner = Runner(f, {}, {}, {})
            with gameta_runner.cd(join('test', 'hello')):
                self.assertCountEqual(listdir('.'), ['world'])
            self.assertCountEqual(listdir('.'), ['test', 'i', 'a'])

    def test_runner_cd_to_nonexistent_directory(self):
        with self.runner.isolated_filesystem() as f:
            gameta_runner = Runner(f, {}, {}, {})
            with self.assertRaises(FileNotFoundError):
                with gameta_runner.cd('test'):
                    pass

    def test_runner_only_cd_within_project_directory(self):
        with self.runner.isolated_filesystem() as f:
            gameta_runner = Runner(f, {}, {}, {})
            with self.assertRaises(FileNotFoundError):
                with gameta_runner.cd('/usr'):
                    pass
            with self.assertRaises(FileNotFoundError):
                with gameta_runner.cd('/////usr'):
                    pass

    def test_runner_cd_to_symlink_within_project_directory(self):
        with self.runner.isolated_filesystem() as f:
            makedirs(join(f, 'test'))
            makedirs(join(f, 'a'))
            symlink(join(f, 'a'), join(f, 'test', 'hello'))

            gameta_runner = Runner(join(f, 'test'), {}, {}, {})
            with gameta_runner.cd('hello'):
                self.assertEqual(basename(getcwd()), 'a')

    def test_runner_apply_command_to_all_repos(self):
        with self.runner.isolated_filesystem() as f:
            makedirs(join(f, 'core', 'genisys'))
            makedirs(join(f, 'core', 'genisys-testing'))

            gameta_runner = Runner(
                f,
                {
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
                },
                {},
                {}
            )
            for cwd, repo, repo_command in zip(
                    [f, join(f, 'core', 'genisys'), join(f, 'core', 'genisys-testing')],
                    ['gameta', 'genisys', 'genisys-testing'],
                    gameta_runner.apply(['git fetch --all --tags --prune', 'git pull'])
            ):
                self.assertEqual(getcwd(), cwd)
                self.assertEqual(repo, repo_command[0])
                self.assertEqual(repo_command[1], ['git', 'fetch', '--all', '--tags', '--prune', '&&', 'git', 'pull'])

    def test_runner_apply_command_to_selected_repos(self):
        with self.runner.isolated_filesystem() as f:
            makedirs(join(f, 'core', 'genisys'))
            makedirs(join(f, 'core', 'genisys-testing'))

            gameta_runner = Runner(
                f,
                {
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
                },
                {},
                {}
            )
            for cwd, repo, repo_command in zip(
                    [f, join(f, 'core', 'genisys')],
                    ['gameta', 'genisys', 'genisys-testing'],
                    gameta_runner.apply(['git fetch --all --tags --prune', 'git pull'], ['genisys', 'gameta'])
            ):
                self.assertEqual(getcwd(), cwd)
                self.assertEqual(repo, repo_command[0])
                self.assertEqual(
                    repo_command[1],
                    [getenv('SHELL', '/bin/sh'), '-c', 'git fetch --all --tags --prune && git pull']
                )

    def test_runner_apply_command_in_separate_shell(self):
        with self.runner.isolated_filesystem() as f:
            makedirs(join(f, 'core', 'genisys'))
            makedirs(join(f, 'core', 'genisys-testing'))
            gameta_runner = Runner(
                f,
                {
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
                },
                {},
                {}
            )
            for cwd, repo, repo_command in zip(
                    [f, join(f, 'core', 'genisys')],
                    ['gameta', 'genisys', 'genisys-testing'],
                    gameta_runner.apply(['git fetch --all --tags --prune', 'git pull'], shell=True)
            ):
                self.assertEqual(getcwd(), cwd)
                self.assertEqual(repo, repo_command[0])
                self.assertEqual(
                    repo_command[1],
                    [getenv('SHELL', '/bin/sh'), '-c', 'git fetch --all --tags --prune && git pull']
                )

    def test_runner_apply_with_parameter_substitution(self):
        with self.runner.isolated_filesystem() as f:
            makedirs(join(f, 'core', 'genisys'))
            makedirs(join(f, 'core', 'genisys-testing'))
            gameta_runner = Runner(
                f,
                {
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
                },
                {},
                {}
            )
            for cwd, test_output, repo, repo_command in zip(
                    [f, join(f, 'core', 'genisys'), join(f, 'core', 'genisys-testing')],
                    [
                        ['git', 'clone', 'https://github.com/test/gameta.git', '.'],
                        ['git', 'clone', 'https://github.com/test/genisys.git', 'core/genisys'],
                        ['git', 'clone', 'https://github.com/test/genisys-testing.git', 'core/genisys-testing']
                    ],
                    ['gameta', 'genisys', 'genisys-testing'],
                    gameta_runner.apply(['git clone {url} {path}'])
            ):
                self.assertEqual(getcwd(), cwd)
                self.assertEqual(repo, repo_command[0])
                self.assertEqual(repo_command[1], test_output)

    def test_runner_apply_with_constants_substitution(self):
        with self.runner.isolated_filesystem() as f:
            makedirs(join(f, 'core', 'genisys'))
            makedirs(join(f, 'core', 'genisys-testing'))
            gameta_runner = Runner(
                f,
                {
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
                },
                {},
                {'BRANCH': 'hello'}
            )
            for cwd, test_output, repo, repo_command in zip(
                    [f, join(f, 'core', 'genisys'), join(f, 'core', 'genisys-testing')],
                    [
                        ['git', 'checkout', 'hello'],
                        ['git', 'checkout', 'hello'],
                        ['git', 'checkout', 'hello']
                    ],
                    ['gameta', 'genisys', 'genisys-testing'],
                    gameta_runner.apply(['git checkout {BRANCH}'])
            ):
                self.assertEqual(getcwd(), cwd)
                self.assertEqual(repo, repo_command[0])
                self.assertEqual(repo_command[1], test_output)

    def test_runner_apply_with_environment_variable_substitution(self):
        with self.runner.isolated_filesystem() as f:
            makedirs(join(f, 'core', 'genisys'))
            makedirs(join(f, 'core', 'genisys-testing'))
            gameta_runner = Runner(
                f,
                {
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
                    }
                },
                {},
                {'BRANCH': "hello"}
            )
            gameta_runner.env_vars['$BRANCH'] = "world"
            for cwd, test_output, repo, repo_command in zip(
                    [f, join(f, 'core', 'genisys'), join(f, 'core', 'genisys-testing')],
                    [
                        ['git', 'checkout', 'world'],
                        ['git', 'checkout', 'world'],
                        ['git', 'checkout', 'world']
                    ],
                    ['gameta', 'genisys', 'genisys-testing'],
                    gameta_runner.apply(['git checkout {$BRANCH}'])
            ):
                self.assertEqual(getcwd(), cwd)
                self.assertEqual(repo, repo_command[0])
                self.assertEqual(repo_command[1], test_output)

    def test_runner_apply_with_all_substitutions(self):
        with self.runner.isolated_filesystem() as f:
            makedirs(join(f, 'core', 'genisys'))
            gameta_runner = Runner(
                f,
                {
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
                },
                {},
                {"BRANCH": "hello"}
            )
            makedirs(join(f, 'core', 'genisys-testing'))
            gameta_runner.env_vars['$ORIGIN'] = "world"
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
                    gameta_runner.apply(
                        ['git clone {url} {path}', 'git checkout {BRANCH}', 'git push {$ORIGIN} {BRANCH}']
                    )
            ):
                self.assertEqual(getcwd(), cwd)
                self.assertEqual(repo, repo_command[0])
                self.assertEqual(repo_command[1], test_output)

    def test_runner_apply_shell_command_with_virtualenv(self):
        with self.runner.isolated_filesystem() as f:
            makedirs(join(f, 'core', 'genisys'))
            makedirs(join(f, 'core', 'genisys-testing'))
            gameta_runner = Runner(
                f,
                {
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
                },
                {'test': join(f, 'test')},
                {}
            )
            for cwd, repo, repo_command in zip(
                    [f, join(f, 'core', 'genisys')],
                    ['gameta', 'genisys', 'genisys-testing'],
                    gameta_runner.apply(['git fetch --all --tags --prune', 'git pull'], venv='test')
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

    def test_runner_generate_parameters_complete_parameter_set_generated(self):
        gameta_runner = Runner(
            '',
            {
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
            },
            {},
            {
                'HELLO': "world",
                "I": 'am',
                'A': 'test'
            }
        )
        gameta_runner.env_vars = {
            '$HELLO': 'world',
            '$I': 'am',
            '$A': 'test'
        }

        self.assertEqual(
            gameta_runner.generate_parameters(gameta_runner.repositories['genisys']),
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

    def test_runner_generate_parameters_constants_substituted_by_environment_variables(self):
        gameta_runner = Runner(
            '',
            {
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
            },
            {},
            {
                '$HELLO': "world",
                "$I": 'am',
                '$A': 'test'
            }
        )
        gameta_runner.env_vars = {
            '$HELLO': 'hello_world',
            '$I': 'hello_world',
            '$A': 'hello_world'
        }

        self.assertCountEqual(
            gameta_runner.generate_parameters(gameta_runner.repositories['genisys']),
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
            }
        )

    def test_runner_generate_parameters_parameters_substituted_by_environment_variables(self):
        gameta_runner = Runner(
            '',
            {
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
            },
            {},
            {
                '$HELLO': "world",
                "$I": 'am',
                '$A': 'test'
            }
        )
        gameta_runner.env_vars = {
            '$BRANCH': 'test',
            '$HELLO': 'hello_world',
            '$I': 'hello_world',
            '$A': 'hello_world'
        }

        self.assertCountEqual(
            gameta_runner.generate_parameters(gameta_runner.repositories['genisys']),
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
            }
        )

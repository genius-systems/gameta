import json
import venv
import zipfile
from os.path import join, dirname, exists
from shutil import copyfile, copytree
from unittest import TestCase
from unittest.mock import patch

from click import Context
from click.testing import CliRunner

from gameta.context import GametaContext, SHELL
from gameta.execute import execute


class TestExec(TestCase):
    def setUp(self) -> None:
        self.runner = CliRunner()
        self.exec = execute

    @patch('gameta.cli.click.Context.ensure_object')
    def test_exec_key_parameters_not_provided(self, mock_ensure_object):
        with self.runner.isolated_filesystem() as f:
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'git.zip'), 'r') as template:
                template.extractall(f)
            copyfile(join(dirname(__file__), 'data', '.meta_other_repos'), join(f, '.meta'))
            context = GametaContext()
            context.project_dir = f
            context.load()
            mock_ensure_object.return_value = context
            result = self.runner.invoke(self.exec)
            self.assertEqual(result.exit_code, 2)
            self.assertEqual(
                result.output,
                "Usage: exec [OPTIONS]\n"
                "Try 'exec --help' for help.\n"
                "\n"
                "Error: Missing option '--command' / '-c'.\n"
            )

    @patch('gameta.cli.click.core.Context')
    def test_exec_nonexistent_command(self, mock_context):
        params = {
            'commands': ['hello_world', 'hello_world2']
        }
        with self.runner.isolated_filesystem() as f:
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'git.zip'), 'r') as template:
                template.extractall(f)
            copyfile(join(dirname(__file__), 'data', '.meta'), join(f, '.meta'))
            gameta_context = GametaContext()
            gameta_context.project_dir = f
            gameta_context.load()
            context = Context(self.exec, obj=gameta_context)
            mock_context.return_value = context
            result = self.runner.invoke(self.exec, ['-c', params['commands'][0], '-c', params['commands'][1]])
            self.assertEqual(result.exit_code, 1)
            self.assertEqual(
                result.output,
                f"Error: One of the commands in {list(params['commands'])} does not exist in the Gameta command store, "
                f"please run `gameta cmd add` to add it first\n"
            )
            self.assertTrue(exists(join(f, '.meta')))
            with open(join(f, '.meta'), 'r') as m:
                self.assertEqual(
                    json.load(m),
                    {
                        'repositories': {
                            'gameta': {
                                '__metarepo__': True,
                                'path': '.',
                                'tags': ['metarepo'],
                                'url': 'git@github.com:genius-systems/gameta.git'
                            }
                        }
                    }
                )

    @patch('gameta.cli.click.core.Context')
    def test_exec_single_command(self, mock_context):
        params = {
            'commands': ['hello_world'],
            'hello_world': {
                'commands': ['git fetch --all --tags --prune'],
                'description': '',
                'tags': ['a', 'b'],
                'repositories': ['gameta'],
                'verbose': False,
                'shell': False,
                'python': False,
                'venv': None,
                'raise_errors': True
            },
            'actual_repositories': ['GitPython', 'gameta', 'gitdb']

        }
        with self.runner.isolated_filesystem() as f:
            copytree(join(dirname(dirname(__file__)), '.git'), join(f, '.git'))
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'gitdb.zip'), 'r') as template:
                template.extractall(join(f, 'core'))
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'gitpython.zip'), 'r') as template:
                template.extractall(f)
            with open(join(dirname(__file__), 'data', '.meta_other_repos'), 'r') as m1:
                output = json.load(m1)
                with open(join(f, '.meta'), 'w') as m2:
                    output['commands'] = {}
                    output['commands']['hello_world'] = params['hello_world']
                    json.dump(output, m2)
            gameta_context = GametaContext()
            gameta_context.project_dir = f
            gameta_context.load()
            context = Context(self.exec, obj=gameta_context)
            mock_context.return_value = context
            result = self.runner.invoke(self.exec, ['-c', params['commands'][0]])
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                f"Executing {params['commands']}\n"
                f"Executing Gameta command {params['commands'][0]}\n"
                f"Applying {params['hello_world']['commands']} to repos {params['actual_repositories']}\n"
                f"Executing {params['hello_world']['commands'][0]} in {params['actual_repositories'][1]}\n"
                f"Executing {params['hello_world']['commands'][0]} in {params['actual_repositories'][0]}\n"
                f"Executing {params['hello_world']['commands'][0]} in {params['actual_repositories'][2]}\n"
            )
            self.assertTrue(exists(join(f, '.meta')))
            with open(join(f, '.meta'), 'r') as m:
                self.assertEqual(
                    json.load(m),
                    {
                        'repositories': {
                            'GitPython': {
                                '__metarepo__': False,
                                'path': 'GitPython',
                                'tags': ['a', 'b', 'c'],
                                'url': 'https://github.com/gitpython-developers/GitPython.git'
                            },
                            'gameta': {
                                '__metarepo__': True,
                                'path': '.',
                                'tags': ['metarepo'],
                                'url': 'git@github.com:genius-systems/gameta.git'
                            },
                            'gitdb': {
                                '__metarepo__': False,
                                'path': 'core/gitdb',
                                'tags': ['a', 'c', 'd'],
                                'url': 'https://github.com/gitpython-developers/gitdb.git'
                            }
                        },
                        'commands': {
                            'hello_world': params['hello_world']
                        }
                    }
                )

    @patch('gameta.cli.click.core.Context')
    def test_exec_multiple_commands(self, mock_context):
        params = {
            'commands': ['hello_world', 'hello_world2', 'hello_world3'],
            'hello_world': {
                'commands': ['git fetch --all --tags --prune'],
                'description': '',
                'tags': ['a', 'b'],
                'repositories': ['gameta'],
                'verbose': False,
                'shell': False,
                'python': False,
                'venv': None,
                'raise_errors': True
            },
            'hello_world2': {
                'commands': ['git fetch --all --tags --prune'],
                'description': '',
                'tags': ['a', 'b'],
                'repositories': ['gameta'],
                'verbose': False,
                'shell': False,
                'python': False,
                'venv': None,
                'raise_errors': True
            },
            'hello_world3': {
                'commands': [
                    'from random import choice\n'
                    'from string import ascii_lowercase, ascii_uppercase, digits, punctuation\n'
                    'with open("{ENCRYPTION_FILE_NAME}", "w") as f:\n'
                    '    f.write("".join([choice(ascii_lowercase + ascii_uppercase + digits + punctuation) '
                    'for _ in range({KEY_LEN})]))'
                ],
                'description': '',
                'tags': [],
                'repositories': ['gameta'],
                'verbose': False,
                'shell': False,
                'python': True,
                'venv': None,
                'raise_errors': True
            },
            'encryption_file_name': 'encryption.txt',
            'key_len': 16,
            'actual_repositories': ['GitPython', 'gameta', 'gitdb']
        }
        with self.runner.isolated_filesystem() as f:
            copytree(join(dirname(dirname(__file__)), '.git'), join(f, '.git'))
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'gitdb.zip'), 'r') as template:
                template.extractall(join(f, 'core'))
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'gitpython.zip'), 'r') as template:
                template.extractall(f)
            with open(join(dirname(__file__), 'data', '.meta_other_repos'), 'r') as m1:
                output = json.load(m1)
                with open(join(f, '.meta'), 'w') as m2:
                    output.update(
                        {
                            'commands': {
                                'hello_world': params['hello_world'],
                                'hello_world2': params['hello_world2'],
                                'hello_world3': params['hello_world3']
                            },
                            'constants': {
                                'ENCRYPTION_FILE_NAME': params['encryption_file_name'],
                                'KEY_LEN': params['key_len']
                            }
                        }
                    )
                    json.dump(output, m2)
            gameta_context = GametaContext()
            gameta_context.project_dir = f
            gameta_context.load()
            context = Context(self.exec, obj=gameta_context)
            mock_context.return_value = context
            result = self.runner.invoke(
                self.exec,
                [
                    '-c', params['commands'][0],
                    '-c', params['commands'][1],
                    '-c', params['commands'][2],
                ]
            )
            output = [c for c in context.obj.apply(params['hello_world3']['commands'], python=True)][0][1]
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                f"Executing {params['commands']}\n"
                f"Executing Gameta command {params['commands'][0]}\n"
                f"Applying {params['hello_world']['commands']} to repos {params['actual_repositories']}\n"
                f"Executing {params['hello_world']['commands'][0]} in {params['actual_repositories'][1]}\n"
                f"Executing {params['hello_world']['commands'][0]} in {params['actual_repositories'][0]}\n"
                f"Executing {params['hello_world']['commands'][0]} in {params['actual_repositories'][2]}\n"
                f"Executing Gameta command {params['commands'][1]}\n"
                f"Applying {params['hello_world2']['commands']} to repos {params['actual_repositories']}\n"
                f"Executing {params['hello_world2']['commands'][0]} in {params['actual_repositories'][1]}\n"
                f"Executing {params['hello_world2']['commands'][0]} in {params['actual_repositories'][0]}\n"
                f"Executing {params['hello_world2']['commands'][0]} in {params['actual_repositories'][2]}\n"
                f"Executing Gameta command {params['commands'][2]}\n"
                f"Applying Python commands {params['hello_world3']['commands']} to repos "
                f"{[params['actual_repositories'][1]]} in a separate shell\n"
                f"Executing {output[0]} {output[1]} {output[2]} in {params['actual_repositories'][1]}\n"
            )
            self.assertTrue(exists(join(f, '.meta')))
            with open(join(f, '.meta'), 'r') as m:
                self.assertEqual(
                    json.load(m),
                    {
                        'repositories': {
                            'GitPython': {
                                '__metarepo__': False,
                                'path': 'GitPython',
                                'tags': ['a', 'b', 'c'],
                                'url': 'https://github.com/gitpython-developers/GitPython.git'
                            },
                            'gameta': {
                                '__metarepo__': True,
                                'path': '.',
                                'tags': ['metarepo'],
                                'url': 'git@github.com:genius-systems/gameta.git'
                            },
                            'gitdb': {
                                '__metarepo__': False,
                                'path': 'core/gitdb',
                                'tags': ['a', 'c', 'd'],
                                'url': 'https://github.com/gitpython-developers/gitdb.git'
                            }
                        },
                        'commands': {
                            'hello_world': params['hello_world'],
                            'hello_world2': params['hello_world2'],
                            'hello_world3': params['hello_world3']
                        },
                        'constants': {
                            'ENCRYPTION_FILE_NAME': params['encryption_file_name'],
                            'KEY_LEN': params['key_len']
                        }
                    }
                )
            self.assertTrue(exists(join(f, params['encryption_file_name'])))
            with open(join(f, params['encryption_file_name']), 'r') as e:
                self.assertEqual(len(e.read()), params['key_len'])

    @patch('gameta.cli.click.core.Context')
    def test_exec_multiple_commands_with_virtualenv(self, mock_context):
        params = {
            'commands': ['hello_world', 'hello_world2'],
            'hello_world': {
                'commands': ['pip3 install cryptography'],
                'description': '',
                'tags': [],
                'repositories': ['gameta'],
                'verbose': False,
                'shell': False,
                'python': False,
                'venv': 'test',
                'raise_errors': True
            },
            'hello_world2': {
                'commands': [
                    'from cryptography.fernet import Fernet\n'
                    'key = Fernet.generate_key()\n'
                    'encryptor = Fernet(key)\n'
                    'message = encryptor.encrypt(b"This is a secret message")\n'
                    'with open("{ENCRYPTION_FILE_NAME}", "wb") as f:\n'
                    '    f.write(message)\n'
                    'with open("key", "wb") as f:\n'
                    '    f.write(key)\n',
                    'from cryptography.fernet import Fernet\n'
                    'with open("key", "rb") as f:\n'
                    '    decryptor = Fernet(f.read())\n'
                    'with open("{ENCRYPTION_FILE_NAME}", "rb") as f:\n'
                    '    print("This is the decrypted message:", decryptor.decrypt(f.read()).decode("utf-8"))\n'
                ],
                'description': '',
                'tags': [],
                'repositories': ['gameta'],
                'verbose': False,
                'shell': False,
                'python': True,
                'venv': 'test',
                'raise_errors': True
            },
            'venv': 'test',
            'directory': 'test',
            'encryption_file_name': 'encryption.txt',
            'actual_repositories': ['gameta']
        }
        with self.runner.isolated_filesystem() as f:
            copytree(join(dirname(dirname(__file__)), '.git'), join(f, '.git'))
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'gitdb.zip'), 'r') as template:
                template.extractall(join(f, 'core'))
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'gitpython.zip'), 'r') as template:
                template.extractall(f)
            venv.create(params['directory'], clear=False, with_pip=True, symlinks=False, system_site_packages=False)
            with open(join(dirname(__file__), 'data', '.meta_other_repos'), 'r') as m1:
                output = json.load(m1)
                with open(join(f, '.meta'), 'w') as m2:
                    output.update(
                        {
                            'commands': {
                                'hello_world': params['hello_world'],
                                'hello_world2': params['hello_world2']
                            },
                            'constants': {
                                'ENCRYPTION_FILE_NAME': params['encryption_file_name'],
                            },
                            'virtualenvs': {
                                params['venv']: join(f, params['directory'])
                            }
                        }
                    )
                    json.dump(output, m2)
            gameta_context = GametaContext()
            gameta_context.project_dir = f
            gameta_context.load()
            context = Context(self.exec, obj=gameta_context)
            mock_context.return_value = context
            result = self.runner.invoke(
                self.exec,
                [
                    '-c', params['commands'][0],
                    '-c', params['commands'][1],
                ]
            )
            output = [c for c in context.obj.apply(
                params['hello_world2']['commands'], python=True, venv=params['venv']
            )][0][1]
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                f"Executing {params['commands']}\n"
                f"Executing Gameta command {params['commands'][0]}\n"
                f"Applying {params['hello_world']['commands']} to repos {params['actual_repositories']} "
                f"with virtualenv {params['venv']}\n"
                f"Executing {SHELL} -c . {join(f, 'test', 'bin', 'activate')} && "
                f"{params['hello_world']['commands'][0]} in {params['actual_repositories'][0]}\n"
                f"Executing Gameta command {params['commands'][1]}\n"
                "Multiple commands detected, executing in a separate shell\n"
                f"Applying {params['hello_world2']['commands']} to repos {params['actual_repositories']} "
                f"with virtualenv {params['venv']}\n"
                f"Executing {output[0]} {output[1]} {output[2]} in {params['actual_repositories'][0]}\n"
            )
            self.assertTrue(exists(join(f, '.meta')))
            with open(join(f, '.meta'), 'r') as m:
                self.assertEqual(
                    json.load(m),
                    {
                        'repositories': {
                            'GitPython': {
                                '__metarepo__': False,
                                'path': 'GitPython',
                                'tags': ['a', 'b', 'c'],
                                'url': 'https://github.com/gitpython-developers/GitPython.git'
                            },
                            'gameta': {
                                '__metarepo__': True,
                                'path': '.',
                                'tags': ['metarepo'],
                                'url': 'git@github.com:genius-systems/gameta.git'
                            },
                            'gitdb': {
                                '__metarepo__': False,
                                'path': 'core/gitdb',
                                'tags': ['a', 'c', 'd'],
                                'url': 'https://github.com/gitpython-developers/gitdb.git'
                            }
                        },
                        'commands': {
                            'hello_world': params['hello_world'],
                            'hello_world2': params['hello_world2'],
                        },
                        'constants': {
                            'ENCRYPTION_FILE_NAME': params['encryption_file_name'],
                        },
                        'virtualenvs': {
                            params['venv']: join(f, params['directory'])
                        }
                    }
                )
            self.assertTrue(exists(join(f, params['encryption_file_name'])))
            self.assertTrue(exists(join(f, 'key')))

import json
import zipfile
from os import listdir
from os.path import join, dirname, exists
from tempfile import mkdtemp
from shutil import copyfile, copytree, rmtree
from unittest import TestCase
from unittest.mock import patch

from click.testing import CliRunner

from gameta.context import GametaContext, SHELL
from gameta.apply import apply


class TestApply(TestCase):
    def setUp(self) -> None:
        self.runner = CliRunner()
        self.apply = apply

    @patch('gameta.cli.click.Context.ensure_object')
    def test_apply_key_parameters_not_provided(self, mock_ensure_object):
        with self.runner.isolated_filesystem() as f:
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'git.zip'), 'r') as template:
                template.extractall(f)
            copyfile(join(dirname(__file__), 'data', '.meta_other_repos'), join(f, '.meta'))
            context = GametaContext()
            context.project_dir = f
            context.load()
            mock_ensure_object.return_value = context
            result = self.runner.invoke(self.apply)
            self.assertEqual(result.exit_code, 2)
            self.assertEqual(
                result.output,
                "Usage: apply [OPTIONS]\n"
                "Try 'apply --help' for help.\n"
                "\n"
                "Error: Missing option '--command' / '-c'.\n"
            )

    @patch('gameta.cli.click.Context.ensure_object')
    def test_apply_command_to_all_repositories(self, mock_ensure_object):
        params = {
            'commands': ['git fetch --all --tags --prune'],
            'actual_repositories': ['gameta', 'GitPython', 'gitdb']
        }
        with self.runner.isolated_filesystem() as f:
            copytree(join(dirname(dirname(__file__)), '.git'), join(f, '.git'))
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'gitpython.zip'), 'r') as template:
                template.extractall(f)
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'gitdb.zip'), 'r') as template:
                template.extractall(join(f, 'core'))
            copyfile(join(dirname(__file__), 'data', '.meta_other_repos'), join(f, '.meta'))
            context = GametaContext()
            context.project_dir = f
            context.load()
            mock_ensure_object.return_value = context
            result = self.runner.invoke(self.apply, ['--command', params['commands'][0]])
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                f"Applying {params['commands']} to repos {params['actual_repositories']}\n"
                f"Executing git fetch --all --tags --prune in {params['actual_repositories'][0]}\n"
                f"Executing git fetch --all --tags --prune in {params['actual_repositories'][1]}\n"
                f"Executing git fetch --all --tags --prune in {params['actual_repositories'][2]}\n"
            )

    @patch('gameta.cli.click.Context.ensure_object')
    def test_apply_multiple_commands_to_all_repositories_with_parameter_substitution(self, mock_ensure_object):
        params = {
            'commands': [
                'git fetch --all --tags --prune',
                'git checkout {BRANCH}',
                'mkdir {$TMP}/{test_dir}',
                'cp -r . {$TMP}/{test_dir}'
            ],
            'actual_repositories': ['gameta', 'GitPython', 'gitdb']
        }
        tempdir = mkdtemp()
        with self.runner.isolated_filesystem() as f:
            copytree(join(dirname(dirname(__file__)), '.git'), join(f, '.git'))
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'gitpython.zip'), 'r') as template:
                template.extractall(f)
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'gitdb.zip'), 'r') as template:
                template.extractall(join(f, 'core'))
            with open(join(dirname(__file__), 'data', '.meta_other_repos'), 'r') as m1:
                output = json.load(m1)
                with open(join(f, '.meta'), 'w+') as m2:
                    output['projects']['gameta'].update({'test_dir': 'test_gameta'})
                    output['projects']['gitdb'].update({'test_dir': 'test_gitdb'})
                    output['projects']['GitPython'].update({'test_dir': 'test_gitpython'})
                    output.update({'constants': {'BRANCH': 'master'}})
                    json.dump(output, m2)
            context = GametaContext()
            context.project_dir = f
            context.load()
            context.env_vars['$TMP'] = tempdir
            mock_ensure_object.return_value = context

            output = [c for repo, c in context.apply(list(params['commands']), shell=True)]
            result = self.runner.invoke(
                self.apply,
                [
                    '--command', params['commands'][0],
                    '--command', params['commands'][1],
                    '--command', params['commands'][2],
                    '--command', params['commands'][3],
                ]
            )
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                "Multiple commands detected, executing in a separate shell\n"
                f"Applying {params['commands']} to repos {params['actual_repositories']} in a separate shell\n"
                f"Executing {' '.join(output[0])} in {params['actual_repositories'][0]}\n"
                f"Executing {' '.join(output[1])} in {params['actual_repositories'][1]}\n"
                f"Executing {' '.join(output[2])} in {params['actual_repositories'][2]}\n"
            )
            self.assertCountEqual(listdir(tempdir), ['test_gitdb', 'test_gitpython', 'test_gameta'])
            self.assertTrue(all(
                i in listdir(join(tempdir, 'test_gameta')) for i in ['.git', '.meta', 'GitPython', 'core']
            ))
            self.assertTrue(all(i in listdir(join(tempdir, 'test_gitpython')) for i in ['git', 'doc', 'test']))
            self.assertTrue(all(i in listdir(join(tempdir, 'test_gitdb')) for i in ['gitdb', 'doc', 'setup.py']))
        rmtree(tempdir)

    @patch('gameta.cli.click.Context.ensure_object')
    def test_apply_command_to_tagged_repositories(self, mock_ensure_object):
        params = {
            'commands': ['git fetch --all --tags --prune'],
            'tags': ['c'],
            'actual_repositories': ['GitPython', 'gitdb']
        }
        with self.runner.isolated_filesystem() as f:
            copytree(join(dirname(dirname(__file__)), '.git'), join(f, '.git'))
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'gitpython.zip'), 'r') as template:
                template.extractall(f)
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'gitdb.zip'), 'r') as template:
                template.extractall(join(f, 'core'))
            copyfile(join(dirname(__file__), 'data', '.meta_other_repos'), join(f, '.meta'))
            context = GametaContext()
            context.project_dir = f
            context.load()
            mock_ensure_object.return_value = context
            result = self.runner.invoke(self.apply, ['--command', params['commands'][0], '-t', params['tags'][0]])
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                f"Applying {params['commands']} to repos {params['actual_repositories']}\n"
                f"Executing git fetch --all --tags --prune in {params['actual_repositories'][0]}\n"
                f"Executing git fetch --all --tags --prune in {params['actual_repositories'][1]}\n"
            )

    @patch('gameta.cli.click.Context.ensure_object')
    def test_apply_command_to_tagged_repositories_that_do_not_exist(self, mock_ensure_object):
        params = {
            'commands': ['git fetch --all --tags --prune'],
            'tags': ['hello', 'world'],
            'actual_repositories': ['gameta', 'GitPython', 'gitdb']
        }
        with self.runner.isolated_filesystem() as f:
            copytree(join(dirname(dirname(__file__)), '.git'), join(f, '.git'))
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'gitpython.zip'), 'r') as template:
                template.extractall(f)
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'gitdb.zip'), 'r') as template:
                template.extractall(join(f, 'core'))
            copyfile(join(dirname(__file__), 'data', '.meta_other_repos'), join(f, '.meta'))
            context = GametaContext()
            context.project_dir = f
            context.load()
            mock_ensure_object.return_value = context
            result = self.runner.invoke(
                self.apply, ['--command', params['commands'][0], '-t', params['tags'][0], '-t', params['tags'][1]]
            )
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                f"Applying {params['commands']} to repos {params['actual_repositories']}\n"
                f"Executing git fetch --all --tags --prune in {params['actual_repositories'][0]}\n"
                f"Executing git fetch --all --tags --prune in {params['actual_repositories'][1]}\n"
                f"Executing git fetch --all --tags --prune in {params['actual_repositories'][2]}\n"
            )

    @patch('gameta.cli.click.Context.ensure_object')
    def test_apply_command_to_specified_repositories(self, mock_ensure_object):
        params = {
            'commands': ['git fetch --all --tags --prune', ],
            'repositories': ['GitPython'],
            'actual_repositories': ['GitPython']
        }
        with self.runner.isolated_filesystem() as f:
            copytree(join(dirname(dirname(__file__)), '.git'), join(f, '.git'))
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'gitpython.zip'), 'r') as template:
                template.extractall(f)
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'gitdb.zip'), 'r') as template:
                template.extractall(join(f, 'core'))
            copyfile(join(dirname(__file__), 'data', '.meta_other_repos'), join(f, '.meta'))
            context = GametaContext()
            context.project_dir = f
            context.load()
            mock_ensure_object.return_value = context
            result = self.runner.invoke(
                self.apply, ['--command', params['commands'][0], '-r', params['repositories'][0]]
            )
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                f"Applying {params['commands']} to repos {params['repositories']}\n"
                f"Executing git fetch --all --tags --prune in {params['actual_repositories'][0]}\n"
            )

    @patch('gameta.cli.click.Context.ensure_object')
    def test_apply_command_to_specified_repositories_that_do_not_exist(self, mock_ensure_object):
        params = {
            'commands': ['git fetch --all --tags --prune'],
            'repositories': ['hello', 'world'],
            'actual_repositories': ['gameta', 'GitPython', 'gitdb']
        }
        with self.runner.isolated_filesystem() as f:
            copytree(join(dirname(dirname(__file__)), '.git'), join(f, '.git'))
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'gitpython.zip'), 'r') as template:
                template.extractall(f)
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'gitdb.zip'), 'r') as template:
                template.extractall(join(f, 'core'))
            copyfile(join(dirname(__file__), 'data', '.meta_other_repos'), join(f, '.meta'))
            context = GametaContext()
            context.project_dir = f
            context.load()
            mock_ensure_object.return_value = context
            result = self.runner.invoke(
                self.apply,
                ['--command', params['commands'][0], '-r', params['repositories'][0], '-r', params['repositories'][1]]
            )
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                f"Applying {params['commands']} to repos {params['actual_repositories']}\n"
                f"Executing git fetch --all --tags --prune in {params['actual_repositories'][0]}\n"
                f"Executing git fetch --all --tags --prune in {params['actual_repositories'][1]}\n"
                f"Executing git fetch --all --tags --prune in {params['actual_repositories'][2]}\n"
            )

    @patch('gameta.cli.click.Context.ensure_object')
    def test_apply_command_to_merged_tags_and_repos(self, mock_ensure_object):
        params = {
            'commands': ['git fetch --all --tags --prune', ],
            'tags': ['metarepo'],
            'repositories': ['gitdb'],
            'actual_repositories': ['gameta', 'gitdb']
        }
        with self.runner.isolated_filesystem() as f:
            copytree(join(dirname(dirname(__file__)), '.git'), join(f, '.git'))
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'gitpython.zip'), 'r') as template:
                template.extractall(f)
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'gitdb.zip'), 'r') as template:
                template.extractall(join(f, 'core'))
            copyfile(join(dirname(__file__), 'data', '.meta_other_repos'), join(f, '.meta'))
            context = GametaContext()
            context.project_dir = f
            context.load()
            mock_ensure_object.return_value = context
            result = self.runner.invoke(
                self.apply,
                ['--command', params['commands'][0], '-t', params['tags'][0], '-r', params['repositories'][0]]
            )
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                f"Applying {params['commands']} to repos {params['actual_repositories']}\n"
                f"Executing git fetch --all --tags --prune in {params['actual_repositories'][0]}\n"
                f"Executing git fetch --all --tags --prune in {params['actual_repositories'][1]}\n"
            )

    @patch('gameta.cli.click.Context.ensure_object')
    def test_apply_command_in_separate_shell(self, mock_ensure_object):
        params = {
            'commands': ['git fetch --all --tags --prune'],
            'actual_repositories': ['gameta', 'GitPython', 'gitdb']
        }
        with self.runner.isolated_filesystem() as f:
            copytree(join(dirname(dirname(__file__)), '.git'), join(f, '.git'))
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'gitpython.zip'), 'r') as template:
                template.extractall(f)
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'gitdb.zip'), 'r') as template:
                template.extractall(join(f, 'core'))
            copyfile(join(dirname(__file__), 'data', '.meta_other_repos'), join(f, '.meta'))
            context = GametaContext()
            context.project_dir = f
            context.load()
            mock_ensure_object.return_value = context
            result = self.runner.invoke(self.apply, ['--command', params['commands'][0], '-s'])
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                f"Applying {params['commands']} to repos {params['actual_repositories']} in a separate shell\n"
                f"Executing {SHELL} -c git fetch --all --tags --prune in {params['actual_repositories'][0]}\n"
                f"Executing {SHELL} -c git fetch --all --tags --prune in {params['actual_repositories'][1]}\n"
                f"Executing {SHELL} -c git fetch --all --tags --prune in {params['actual_repositories'][2]}\n"
            )

    @patch('gameta.cli.click.Context.ensure_object')
    def test_apply_command_with_python_interpreter(self, mock_ensure_object):
        params = {
            'commands': [
                'from random import choice\n'
                'from string import ascii_lowercase, ascii_uppercase, digits, punctuation\n'
                'with open("{ENCRYPTION_FILE_NAME}", "w") as f:\n'
                '    f.write("".join([choice(ascii_lowercase + ascii_uppercase + digits + punctuation) '
                'for _ in range({KEY_LEN})]))',
                'from os import getcwd\n'
                'from os.path import join, exists\n'
                'from shutil import copyfile\n'
                'for repo, details in {__repos__}.items():\n'
                '    if not exists(join(getcwd(), details["path"], "{ENCRYPTION_FILE_NAME}")):\n'
                '        copyfile("{ENCRYPTION_FILE_NAME}", join(getcwd(), details["path"], "{ENCRYPTION_FILE_NAME}"))'
            ],
            'tags': ['metarepo'],
            'actual_repositories': ['gameta'],
            'encryption_file_name': 'encryption.txt',
            'key_len': 16
        }
        with self.runner.isolated_filesystem() as f:
            copytree(join(dirname(dirname(__file__)), '.git'), join(f, '.git'))
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'gitpython.zip'), 'r') as template:
                template.extractall(f)
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'gitdb.zip'), 'r') as template:
                template.extractall(join(f, 'core'))
            with open(join(dirname(__file__), 'data', '.meta_other_repos'), 'r') as m1:
                output = json.load(m1)
                with open(join(f, '.meta'), 'w+') as m2:
                    output.update(
                        {
                            'constants': {
                                'ENCRYPTION_FILE_NAME': params['encryption_file_name'],
                                'KEY_LEN': params['key_len']
                            }
                        }
                    )
                    json.dump(output, m2)
            context = GametaContext()
            context.project_dir = f
            context.load()
            mock_ensure_object.return_value = context

            output = [c for c in context.apply(params['commands'], python=True)]
            result = self.runner.invoke(
                self.apply, [
                    '--command', params['commands'][0],
                    '--command', params['commands'][1],
                    '--tags', params['tags'][0],
                    '-p', '-v'
                ]
            )
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                "Multiple commands detected, executing in a separate shell\n"
                f"Applying {params['commands']} to repos {params['actual_repositories']} in a separate shell\n"
                f"Executing {output[0][1][0]} {output[0][1][1]} {output[0][1][2]} in "
                f"{params['actual_repositories'][0]}\n"
            )
            for path in [f, join(f, 'GitPython'), join(f, 'core', 'gitdb')]:
                self.assertTrue(exists(join(path, params['encryption_file_name'])))
                with open(join(path, params['encryption_file_name'])) as e:
                    self.assertEqual(len(e.read()), params['key_len'])

    @patch('gameta.cli.click.Context.ensure_object')
    def test_apply_command_with_python_interpreter_invalid_python_script(self, mock_ensure_object):
        params = {
            'commands': [
                'from random import choice\n'
                'from string import ascii_lowercase, ascii_uppercase, digits, punctuation\n'
                'with open("{ENCRYPTION_FILE_NAME}", "w") as f:\n'
                '    f.write(".join([choice(ascii_lowercase + ascii_uppercase + digits + punctuation) '  # Missing one "
                'for _ in range({KEY_LEN})]))',
                'from os import getcwd\n'
                'from os.path import join, exists\n'
                'from shutil import copyfile\n'
                'for repo, details in {__repos__}.items():\n'
                '    if not exists(join(getcwd(), details["path"], "{ENCRYPTION_FILE_NAME}")):\n'
                '        copyfile("{ENCRYPTION_FILE_NAME}", join(getcwd(), details["path"], "{ENCRYPTION_FILE_NAME}"))'
            ],
            'tags': ['metarepo'],
            'actual_repositories': ['gameta'],
            'encryption_file_name': 'encryption.txt',
            'key_len': 16
        }
        with self.runner.isolated_filesystem() as f:
            copytree(join(dirname(dirname(__file__)), '.git'), join(f, '.git'))
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'gitpython.zip'), 'r') as template:
                template.extractall(f)
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'gitdb.zip'), 'r') as template:
                template.extractall(join(f, 'core'))
            with open(join(dirname(__file__), 'data', '.meta_other_repos'), 'r') as m1:
                output = json.load(m1)
                with open(join(f, '.meta'), 'w+') as m2:
                    output.update(
                        {
                            'constants': {
                                'ENCRYPTION_FILE_NAME': params['encryption_file_name'],
                                'KEY_LEN': params['key_len']
                            }
                        }
                    )
                    json.dump(output, m2)
            context = GametaContext()
            context.project_dir = f
            context.load()
            mock_ensure_object.return_value = context
            result = self.runner.invoke(
                self.apply, [
                    '--command', params['commands'][0],
                    '--command', params['commands'][1],
                    '--tags', params['tags'][0],
                    '-p', '-v'
                ]
            )
            self.assertEqual(result.exit_code, 1)
            self.assertEqual(
                result.output,
                f"Error: One of the commands in {params['commands']} is not a valid Python script\n"
            )

    @patch('gameta.cli.click.Context.ensure_object')
    def test_apply_command_with_python_interpreter_shell_command_passed(self, mock_ensure_object):
        params = {
            'commands': ['git fetch --all --tags --prune', ],
            'tags': ['metarepo'],
            'actual_repositories': ['gameta'],
            'encryption_file_name': 'encryption.txt',
            'key_len': 16
        }
        with self.runner.isolated_filesystem() as f:
            copytree(join(dirname(dirname(__file__)), '.git'), join(f, '.git'))
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'gitpython.zip'), 'r') as template:
                template.extractall(f)
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'gitdb.zip'), 'r') as template:
                template.extractall(join(f, 'core'))
            with open(join(dirname(__file__), 'data', '.meta_other_repos'), 'r') as m1:
                output = json.load(m1)
                with open(join(f, '.meta'), 'w+') as m2:
                    output.update(
                        {
                            'constants': {
                                'ENCRYPTION_FILE_NAME': params['encryption_file_name'],
                                'KEY_LEN': params['key_len']
                            }
                        }
                    )
                    json.dump(output, m2)
            context = GametaContext()
            context.project_dir = f
            context.load()
            mock_ensure_object.return_value = context

            result = self.runner.invoke(
                self.apply, [
                    '--command', params['commands'][0],
                    '--tags', params['tags'][0],
                    '-p', '-v'
                ]
            )
            self.assertEqual(result.exit_code, 1)
            self.assertEqual(
                result.output,
                f"Error: One of the commands in {params['commands']} is not a valid Python script\n"
            )

    @patch('gameta.cli.click.Context.ensure_object')
    def test_apply_raise_errors(self, mock_ensure_object):
        params = {
            'commands': ('git fetch --all --tags --prune', )
        }
        with self.runner.isolated_filesystem() as f:
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'git.zip'), 'r') as template:
                template.extractall(f)
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'gitpython.zip'), 'r') as template:
                template.extractall(f)
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'gitdb.zip'), 'r') as template:
                template.extractall(join(f, 'core'))
            copyfile(join(dirname(__file__), 'data', '.meta_other_repos'), join(f, '.meta'))
            context = GametaContext()
            context.project_dir = f
            context.load()
            mock_ensure_object.return_value = context
            result = self.runner.invoke(self.apply, ['--command', params['commands'][0], '-e'])
            self.assertEqual(result.exit_code, 128)

    @patch('gameta.cli.click.Context.ensure_object')
    def test_apply_command_failed_to_execute(self, mock_ensure_object):
        params = {
            'commands': ['rm test', ],
            'actual_repositories': ['gameta', 'GitPython', 'gitdb'],
        }
        with self.runner.isolated_filesystem() as f:
            copytree(join(dirname(dirname(__file__)), '.git'), join(f, '.git'))
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'gitpython.zip'), 'r') as template:
                template.extractall(f)
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'gitdb.zip'), 'r') as template:
                template.extractall(join(f, 'core'))
            copyfile(join(dirname(__file__), 'data', '.meta_other_repos'), join(f, '.meta'))
            context = GametaContext()
            context.project_dir = f
            context.load()
            mock_ensure_object.return_value = context
            result = self.runner.invoke(self.apply, ['--command', params['commands'][0], '-e'])
            self.assertEqual(result.exit_code, 1)
            self.assertEqual(
                result.output,
                f"Applying {params['commands']} to repos {params['actual_repositories']}\n"
                f"Executing rm test in {params['actual_repositories'][0]}\n"
                f"Error: CalledProcessError.Command '['rm', 'test']' returned non-zero exit status 1. "
                f"occurred when executing command ['rm', 'test'] in gameta\n"
            )

    @patch('gameta.cli.click.Context.ensure_object')
    def test_apply_command_failed_to_execute_verbose(self, mock_ensure_object):
        params = {
            'commands': ['rm test', ],
            'actual_repositories': ['gameta', 'GitPython', 'gitdb'],
        }
        with self.runner.isolated_filesystem() as f:
            copytree(join(dirname(dirname(__file__)), '.git'), join(f, '.git'))
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'gitpython.zip'), 'r') as template:
                template.extractall(f)
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'gitdb.zip'), 'r') as template:
                template.extractall(join(f, 'core'))
            copyfile(join(dirname(__file__), 'data', '.meta_other_repos'), join(f, '.meta'))
            context = GametaContext()
            context.project_dir = f
            context.load()
            mock_ensure_object.return_value = context
            result = self.runner.invoke(self.apply, ['--command', params['commands'][0], '-e', '-v'])
            self.assertEqual(result.exit_code, 1)
            self.assertEqual(
                result.output,
                f"Applying {params['commands']} to repos {params['actual_repositories']}\n"
                f"Executing rm test in {params['actual_repositories'][0]}\n"
                "rm: cannot remove 'test': No such file or directory\n"
                f"Error: CalledProcessError.Command '['rm', 'test']' returned non-zero exit status 1. "
                f"occurred when executing command ['rm', 'test'] in gameta\n"
            )

    @patch('gameta.cli.click.Context.ensure_object')
    def test_apply_verbose(self, mock_ensure_object):
        params = {
            'commands': ['git fetch --all --tags --prune'],
            'actual_repositories': ['gameta', 'GitPython', 'gitdb']
        }
        with self.runner.isolated_filesystem() as f:
            copytree(join(dirname(dirname(__file__)), '.git'), join(f, '.git'))
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'gitpython.zip'), 'r') as template:
                template.extractall(f)
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'gitdb.zip'), 'r') as template:
                template.extractall(join(f, 'core'))
            copyfile(join(dirname(__file__), 'data', '.meta_other_repos'), join(f, '.meta'))
            context = GametaContext()
            context.project_dir = f
            context.load()
            mock_ensure_object.return_value = context
            result = self.runner.invoke(self.apply, ['--command', params['commands'][0], '-v'])
            self.assertEqual(result.exit_code, 0)
            self.assertTrue(len(result.output.split('\n')) >= 18)

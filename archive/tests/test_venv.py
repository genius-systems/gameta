import json
import venv
from os import listdir, makedirs
from os.path import dirname, exists, join
from shutil import copyfile
from unittest import TestCase
from unittest.mock import patch

from click import Context
from click.testing import CliRunner

from gameta import __version__
from gameta.base import GametaContext
from gameta.venv import create, register, unregister


class TestVenvCreate(TestCase):
    def setUp(self) -> None:
        self.maxDiff = None
        self.create = create
        self.runner = CliRunner()

    @patch('gameta.cli.click.Context.ensure_object')
    def test_venv_create_key_parameters_not_provided(self, mock_ensure_object):
        with self.runner.isolated_filesystem() as f:
            copyfile(join(dirname(__file__), 'data', '.gameta'), join(f, '.gameta'))
            context = GametaContext()
            context.project_dir = f
            context.load()
            mock_ensure_object.return_value = context
            result = self.runner.invoke(self.create)
            self.assertEqual(result.exit_code, 2)
            self.assertEqual(
                result.output,
                "Usage: create [OPTIONS]\n"
                "Try 'create --help' for help.\n"
                "\n"
                "Error: Missing option '--name' / '-n'.\n"
            )

    @patch('gameta.cli.click.core.Context')
    def test_venv_create_default_virtualenv_configuration(self, mock_context):
        params = {
            'name': 'test',
        }
        with self.runner.isolated_filesystem() as f:
            copyfile(join(dirname(__file__), 'data', '.gameta'), join(f, '.gameta'))
            gameta_context = GametaContext()
            gameta_context.project_dir = f
            gameta_context.load()
            context = Context(self.create, obj=gameta_context)
            mock_context.return_value = context
            result = self.runner.invoke(self.create, ['-n', params['name']])
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                f"Creating virtualenv in {join(f, '.venv')} with the following config: "
                "(site_packages: False, pip: True, symlinks: False, overwrite: False)\n"
                f"Registering virtualenv in {join(f, '.venv')} as {params['name']}\n"
                f"Successfully registered {params['name']}\n"
                f"Successfully created virtualenv {params['name']}\n"
            )
            self.assertCountEqual(listdir(f), ['.venv', '.gameta', '.gitignore'])
            self.assertTrue(
                all(
                    i in listdir(join(f, '.venv'))
                    for i in ['bin', 'lib64', 'lib', 'include', 'pyvenv.cfg']
                )
            )
            self.assertTrue(
                all(
                    i in listdir(join(f, '.venv', 'bin'))
                    for i in [
                        'activate', 'activate.fish', 'activate.csh', 'pip', 'pip3', 'easy_install', 'python3', 'python'
                    ]
                )
            )
            with open(join(f, '.gameta'), 'r') as m:
                self.assertEqual(
                    json.load(m),
                    {
                        "version": '0.3.0',
                        "repositories": {
                            "gameta": {
                                "__metarepo__": True,
                                "path": ".",
                                "tags": ["metarepo"],
                                "url": "git@github.com:genius-systems/gameta.git"
                            }
                        },
                        "virtualenvs": {
                            'test': join(f, '.venv')
                        }
                    }
                )

    @patch('gameta.cli.click.core.Context')
    def test_venv_create_virtualenv_fully_customised_configuration(self, mock_context):
        params = {
            'name': 'test',
            'directory': 'test',
            'site_packages': True,
            'pip': False,
            'symlinks': True,
        }
        with self.runner.isolated_filesystem() as f:
            gameta_context = GametaContext()
            gameta_context.project_dir = f
            gameta_context.load()
            context = Context(self.create, obj=gameta_context)
            mock_context.return_value = context
            result = self.runner.invoke(
                self.create,
                [
                    '-n', params['name'],
                    '-d', params['directory'],
                    '-s', '-np', '-l'
                ]
            )
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                f"Creating virtualenv in {join(f, params['directory'])} with the following config: "
                f"(site_packages: {params['site_packages']}, pip: {params['pip']}, symlinks: {params['symlinks']}, "
                f"overwrite: False)\n"
                f"Registering virtualenv in {join(f, params['directory'])} as {params['name']}\n"
                f"Successfully registered {params['name']}\n"
                f"Successfully created virtualenv {params['name']}\n"
            )
            self.assertCountEqual(listdir(f), [params['directory'], '.gameta', '.gitignore'])
            self.assertTrue(
                all(
                    i in listdir(join(f, params['directory']))
                    for i in ['bin', 'lib64', 'lib', 'include', 'pyvenv.cfg']
                )
            )
            self.assertTrue(
                all(
                    i in listdir(join(f, params['directory'], 'bin'))
                    for i in [
                        'activate', 'activate.fish', 'activate.csh', 'python3', 'python'
                    ]
                )
            )
            with open(join(f, '.gameta'), 'r') as m:
                self.assertEqual(
                    json.load(m),
                    {
                        "version": __version__,
                        "repositories": {},
                        "virtualenvs": {
                            'test': join(f, params['directory'])
                        }
                    }
                )

    @patch('gameta.cli.click.core.Context')
    def test_venv_create_virtualenv_in_nested_directories(self, mock_context):
        params = {
            'name': 'test',
            'directory': 'test/another_test'
        }
        with self.runner.isolated_filesystem() as f:
            copyfile(join(dirname(__file__), 'data', '.gameta'), join(f, '.gameta'))
            gameta_context = GametaContext()
            gameta_context.project_dir = f
            gameta_context.load()
            context = Context(self.create, obj=gameta_context)
            mock_context.return_value = context
            result = self.runner.invoke(self.create, ['-n', params['name'], '-d', join(f, params['directory'])])
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                f"Creating virtualenv in {join(f, params['directory'])} with the following config: "
                "(site_packages: False, pip: True, symlinks: False, overwrite: False)\n"
                f"Registering virtualenv in {join(f, params['directory'])} as {params['name']}\n"
                f"Successfully registered {params['name']}\n"
                f"Successfully created virtualenv {params['name']}\n"
            )
            self.assertCountEqual(listdir(f), ['test', '.gameta', '.gitignore'])
            self.assertCountEqual(listdir(join(f, 'test')), ['another_test'])
            self.assertTrue(
                all(
                    i in listdir(join(f, params['directory']))
                    for i in ['bin', 'lib64', 'lib', 'include', 'pyvenv.cfg']
                )
            )
            self.assertTrue(
                all(
                    i in listdir(join(f, params['directory'], 'bin'))
                    for i in [
                        'activate', 'activate.fish', 'activate.csh', 'pip', 'pip3', 'easy_install', 'python3', 'python'
                    ]
                )
            )
            with open(join(f, '.gameta'), 'r') as m:
                self.assertEqual(
                    json.load(m),
                    {
                        "version": '0.3.0',
                        "repositories": {
                            "gameta": {
                                "__metarepo__": True,
                                "path": ".",
                                "tags": ["metarepo"],
                                "url": "git@github.com:genius-systems/gameta.git"
                            }
                        },
                        "virtualenvs": {
                            'test': join(f, params['directory'])
                        }
                    }
                )

    @patch('gameta.cli.click.core.Context')
    def test_venv_create_virtualenv_in_directory_with_contents(self, mock_context):
        params = {
            'name': 'test',
            'directory': 'test'
        }
        with self.runner.isolated_filesystem() as f:
            copyfile(join(dirname(__file__), 'data', '.gameta'), join(f, '.gameta'))
            makedirs(join(f, params['directory']))
            with open(join(f, params['directory'], 'test.txt'), 'w') as t:
                t.write('Hello World!')
            gameta_context = GametaContext()
            gameta_context.project_dir = f
            gameta_context.load()
            context = Context(self.create, obj=gameta_context)
            mock_context.return_value = context
            result = self.runner.invoke(self.create, ['-n', params['name'], '-d', join(f, params['directory'])])
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                f"Creating virtualenv in {join(f, params['directory'])} with the following config: "
                "(site_packages: False, pip: True, symlinks: False, overwrite: False)\n"
                f"Registering virtualenv in {join(f, params['directory'])} as {params['name']}\n"
                f"Successfully registered {params['name']}\n"
                f"Successfully created virtualenv {params['name']}\n"
            )
            self.assertCountEqual(listdir(f), ['test', '.gameta', '.gitignore'])
            self.assertTrue(
                all(
                    i in listdir(join(f, params['directory']))
                    for i in ['bin', 'lib64', 'lib', 'include', 'pyvenv.cfg', 'test.txt']
                )
            )
            self.assertTrue(
                all(
                    i in listdir(join(f, params['directory'], 'bin'))
                    for i in [
                        'activate', 'activate.fish', 'activate.csh', 'pip', 'pip3', 'easy_install', 'python3', 'python'
                    ]
                )
            )
            with open(join(f, '.gameta'), 'r') as m:
                self.assertEqual(
                    json.load(m),
                    {
                        "version": '0.3.0',
                        "repositories": {
                            "gameta": {
                                "__metarepo__": True,
                                "path": ".",
                                "tags": ["metarepo"],
                                "url": "git@github.com:genius-systems/gameta.git"
                            }
                        },
                        "virtualenvs": {
                            'test': join(f, params['directory'])
                        }
                    }
                )

    @patch('gameta.cli.click.core.Context')
    def test_venv_create_overwrite_directory_with_contents(self, mock_context):
        params = {
            'name': 'test',
            'directory': 'test'
        }
        with self.runner.isolated_filesystem() as f:
            copyfile(join(dirname(__file__), 'data', '.gameta'), join(f, '.gameta'))
            makedirs(join(f, params['directory']))
            with open(join(f, params['directory'], 'test.txt'), 'w') as t:
                t.write('Hello World!')
            gameta_context = GametaContext()
            gameta_context.project_dir = f
            gameta_context.load()
            context = Context(self.create, obj=gameta_context)
            mock_context.return_value = context
            result = self.runner.invoke(self.create, ['-n', params['name'], '-d', join(f, params['directory']), '-o'])
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                f"Creating virtualenv in {join(f, params['directory'])} with the following config: "
                "(site_packages: False, pip: True, symlinks: False, overwrite: True)\n"
                f"Registering virtualenv in {join(f, params['directory'])} as {params['name']}\n"
                f"Successfully registered {params['name']}\n"
                f"Successfully created virtualenv {params['name']}\n"
            )
            self.assertCountEqual(listdir(f), ['test', '.gameta', '.gitignore'])
            self.assertTrue(
                all(
                    i in listdir(join(f, params['directory']))
                    for i in ['bin', 'lib64', 'lib', 'include', 'pyvenv.cfg']
                )
            )
            self.assertTrue(
                all(
                    i in listdir(join(f, params['directory'], 'bin'))
                    for i in [
                        'activate', 'activate.fish', 'activate.csh', 'pip', 'pip3', 'easy_install', 'python3', 'python'
                    ]
                )
            )
            with open(join(f, '.gameta'), 'r') as m:
                self.assertEqual(
                    json.load(m),
                    {
                        "version": '0.3.0',
                        "repositories": {
                            "gameta": {
                                "__metarepo__": True,
                                "path": ".",
                                "tags": ["metarepo"],
                                "url": "git@github.com:genius-systems/gameta.git"
                            }
                        },
                        "virtualenvs": {
                            'test': join(f, params['directory'])
                        }
                    }
                )


class TestVenvRegister(TestCase):
    def setUp(self) -> None:
        self.maxDiff = None
        self.register = register
        self.runner = CliRunner()

    @patch('gameta.cli.click.Context.ensure_object')
    def test_venv_add_key_parameters_not_provided(self, mock_ensure_object):
        with self.runner.isolated_filesystem() as f:
            copyfile(join(dirname(__file__), 'data', '.gameta'), join(f, '.gameta'))
            context = GametaContext()
            context.project_dir = f
            context.load()
            mock_ensure_object.return_value = context
            result = self.runner.invoke(self.register)
            self.assertEqual(result.exit_code, 2)
            self.assertEqual(
                result.output,
                "Usage: register [OPTIONS]\n"
                "Try 'register --help' for help.\n"
                "\n"
                "Error: Missing option '--name' / '-n'.\n"
            )

    @patch('gameta.cli.click.Context.ensure_object')
    def test_venv_register_path_does_not_exist(self, mock_ensure_object):
        params = {
            'directory': 'test',
            'name': 'test'
        }
        with self.runner.isolated_filesystem() as f:
            context = GametaContext()
            context.project_dir = f
            context.load()
            mock_ensure_object.return_value = context
            result = self.runner.invoke(self.register, ['-n', params['name'], '-p', join(f, params['directory'])])
            self.assertEqual(result.exit_code, 1)
            self.assertEqual(
                result.output,
                f"Error: Path {join(f, params['directory'])} does not exist\n"
            )

    @patch('gameta.cli.click.Context.ensure_object')
    def test_venv_register_invalid_virtualenv(self, mock_ensure_object):
        params = {
            'directory': 'test',
            'name': 'test'
        }
        with self.runner.isolated_filesystem() as f:
            makedirs(join(f, 'test', 'bin'))
            with open(join(f, 'test', 'bin', 'activate'), 'w'):
                pass
            context = GametaContext()
            context.project_dir = f
            context.load()
            mock_ensure_object.return_value = context
            result = self.runner.invoke(self.register, ['-n', params['name'], '-p', join(f, params['directory'])])
            self.assertEqual(result.exit_code, 1)
            self.assertEqual(
                result.output,
                f"Error: Path {join(f, params['directory'])} is not a valid virtualenv\n"
            )

    @patch('gameta.cli.click.Context.ensure_object')
    def test_venv_register_virtualenv_no_meta_file(self, mock_ensure_object):
        params = {
            'directory': 'test',
            'name': 'test'
        }
        with self.runner.isolated_filesystem() as f:
            venv.create(params['directory'], clear=False, with_pip=True, symlinks=False, system_site_packages=False)
            context = GametaContext()
            context.project_dir = f
            context.load()
            mock_ensure_object.return_value = context
            result = self.runner.invoke(self.register, ['-n', params['name'], '-p', join(f, params['directory'])])
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                f"Registering virtualenv in {join(f, params['directory'])} as {params['name']}\n"
                f"Successfully registered {params['name']}\n"
            )
            self.assertTrue(exists(join(f, '.gameta')))
            with open(join(f, '.gameta')) as m:
                self.assertEqual(
                    json.load(m),
                    {
                        "version": __version__,
                        'repositories': {},
                        'virtualenvs': {
                            params['name']: join(f, params['directory'])
                        }
                    }
                )

    @patch('gameta.cli.click.Context.ensure_object')
    def test_venv_register_virtualenv_adding_new_virtualenv(self, mock_ensure_object):
        params = {
            'directory1': 'test1',
            'directory2': 'test2',
            'name1': 'test1',
            'name2': 'test2'
        }
        with self.runner.isolated_filesystem() as f:
            venv.create(params['directory1'], clear=False, with_pip=True, symlinks=False, system_site_packages=False)
            venv.create(params['directory2'], clear=False, with_pip=True, symlinks=False, system_site_packages=False)
            with open(join(dirname(__file__), 'data', '.gameta'), 'r') as m1:
                output = json.load(m1)
                with open(join(f, '.gameta'), 'w') as m2:
                    output.update({'virtualenvs': {params['name1']: join(f, params['directory1'])}})
                    json.dump(output, m2)
            context = GametaContext()
            context.project_dir = f
            context.load()
            mock_ensure_object.return_value = context
            result = self.runner.invoke(self.register, ['-n', params['name2'], '-p', join(f, params['directory2'])])
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                f"Registering virtualenv in {join(f, params['directory2'])} as {params['name2']}\n"
                f"Successfully registered {params['name2']}\n"
            )
            self.assertTrue(exists(join(f, '.gameta')))
            with open(join(f, '.gameta')) as m:
                self.assertEqual(
                    json.load(m),
                    {
                        "version": '0.3.0',
                        'repositories': {
                            "gameta": {
                                "__metarepo__": True,
                                "path": ".",
                                "tags": ["metarepo"],
                                "url": "git@github.com:genius-systems/gameta.git"
                            }
                        },
                        'virtualenvs': {
                            params['name1']: join(f, params['directory1']),
                            params['name2']: join(f, params['directory2'])
                        }
                    }
                )

    @patch('gameta.cli.click.Context.ensure_object')
    def test_venv_register_virtualenv_overwriting_existing_virtualenv(self, mock_ensure_object):
        params = {
            'directory': 'test',
            'directory2': 'test2',
            'name': 'test',
        }
        with self.runner.isolated_filesystem() as f:
            venv.create(params['directory'], clear=False, with_pip=True, symlinks=False, system_site_packages=False)
            venv.create(params['directory2'], clear=False, with_pip=True, symlinks=False, system_site_packages=False)
            with open(join(dirname(__file__), 'data', '.gameta'), 'r') as m1:
                output = json.load(m1)
                with open(join(f, '.gameta'), 'w') as m2:
                    output.update({'virtualenvs': {params['name']: join(f, params['directory'])}})
                    json.dump(output, m2)
            context = GametaContext()
            context.project_dir = f
            context.load()
            mock_ensure_object.return_value = context
            result = self.runner.invoke(
                self.register,
                [
                    '-n', params['name'],
                    '-p', join(f, params['directory2']),
                    '-o'
                ]
            )
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                f"Registering virtualenv in {join(f, params['directory2'])} as {params['name']}\n"
                f"Successfully registered {params['name']}\n"
            )
            self.assertTrue(exists(join(f, '.gameta')))
            with open(join(f, '.gameta')) as m:
                self.assertEqual(
                    json.load(m),
                    {
                        "version": '0.3.0',
                        'repositories': {
                            "gameta": {
                                "__metarepo__": True,
                                "path": ".",
                                "tags": ["metarepo"],
                                "url": "git@github.com:genius-systems/gameta.git"
                            }
                        },
                        'virtualenvs': {
                            params['name']: join(f, params['directory2']),
                        }
                    }
                )

    @patch('gameta.cli.click.Context.ensure_object')
    def test_venv_register_virtualenv_existing_virtualenv_not_overwritten(self, mock_ensure_object):
        params = {
            'directory': 'test',
            'directory2': 'test2',
            'name': 'test',
        }
        with self.runner.isolated_filesystem() as f:
            venv.create(params['directory'], clear=False, with_pip=True, symlinks=False, system_site_packages=False)
            venv.create(params['directory2'], clear=False, with_pip=True, symlinks=False, system_site_packages=False)
            with open(join(dirname(__file__), 'data', '.gameta'), 'r') as m1:
                output = json.load(m1)
                with open(join(f, '.gameta'), 'w') as m2:
                    output.update({'virtualenvs': {params['name']: join(f, params['directory'])}})
                    json.dump(output, m2)
            context = GametaContext()
            context.project_dir = f
            context.load()
            mock_ensure_object.return_value = context
            result = self.runner.invoke(self.register, ['-n', params['name'], '-p', join(f, params['directory2'])])
            self.assertEqual(result.exit_code, 1)
            self.assertEqual(
                result.output,
                f"Error: Virtualenv {params['name']} exists and overwrite flag is False\n"
            )
            self.assertTrue(exists(join(f, '.gameta')))
            with open(join(f, '.gameta')) as m:
                self.assertEqual(
                    json.load(m),
                    {
                        "version": '0.3.0',
                        'repositories': {
                            "gameta": {
                                "__metarepo__": True,
                                "path": ".",
                                "tags": ["metarepo"],
                                "url": "git@github.com:genius-systems/gameta.git"
                            }
                        },
                        'virtualenvs': {
                            params['name']: join(f, params['directory']),
                        }
                    }
                )


class TestVenvUnregister(TestCase):
    def setUp(self) -> None:
        self.maxDiff = None
        self.unregister = unregister
        self.runner = CliRunner()

    @patch('gameta.cli.click.Context.ensure_object')
    def test_venv_unregister_key_parameters_not_provided(self, mock_ensure_object):
        with self.runner.isolated_filesystem() as f:
            copyfile(join(dirname(__file__), 'data', '.gameta'), join(f, '.gameta'))
            context = GametaContext()
            context.project_dir = f
            context.load()
            mock_ensure_object.return_value = context
            result = self.runner.invoke(self.unregister)
            self.assertEqual(result.exit_code, 2)
            self.assertEqual(
                result.output,
                "Usage: unregister [OPTIONS]\n"
                "Try 'unregister --help' for help.\n"
                "\n"
                "Error: Missing option '--name' / '-n'.\n"
            )

    @patch('gameta.cli.click.Context.ensure_object')
    def test_venv_unregister_virtualenv_does_not_exist(self, mock_ensure_object):
        params = {
            'name': 'test'
        }
        with self.runner.isolated_filesystem() as f:
            copyfile(join(dirname(__file__), 'data', '.gameta'), join(f, '.gameta'))
            context = GametaContext()
            context.project_dir = f
            context.load()
            mock_ensure_object.return_value = context
            result = self.runner.invoke(self.unregister, ['-n', params['name']])
            self.assertEqual(result.exit_code, 1)
            self.assertEqual(
                result.output,
                f"Error: Virtualenv {params['name']} has not been registered\n"
            )

    @patch('gameta.cli.click.Context.ensure_object')
    def test_venv_unregister_virtualenv_unregistered(self, mock_ensure_object):
        params = {
            'name': 'test',
            'directory': 'test'
        }
        with self.runner.isolated_filesystem() as f:
            venv.create(params['directory'], clear=False, with_pip=True, symlinks=False, system_site_packages=False)
            with open(join(dirname(__file__), 'data', '.gameta'), 'r') as m1:
                output = json.load(m1)
                with open(join(f, '.gameta'), 'w') as m2:
                    output.update({'virtualenvs': {params['name']: join(f, params['directory'])}})
                    json.dump(output, m2)
            context = GametaContext()
            context.project_dir = f
            context.load()
            mock_ensure_object.return_value = context
            result = self.runner.invoke(self.unregister, ['-n', params['name']])
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                f"Unregistering virtualenv {params['name']}\n"
                f"Virtualenv {params['name']} successfully unregistered\n"
            )
            self.assertCountEqual(listdir(f), ['test', '.gameta', '.gitignore'])
            self.assertTrue(
                all(
                    i in listdir(join(f, params['directory']))
                    for i in ['bin', 'lib64', 'lib', 'include', 'pyvenv.cfg']
                )
            )
            self.assertTrue(
                all(
                    i in listdir(join(f, params['directory'], 'bin'))
                    for i in [
                        'activate', 'activate.fish', 'activate.csh', 'pip', 'pip3', 'easy_install', 'python3', 'python'
                    ]
                )
            )
            with open(join(f, '.gameta')) as m:
                self.assertEqual(
                    json.load(m),
                    {
                        "version": '0.3.0',
                        'repositories': {
                            "gameta": {
                                "__metarepo__": True,
                                "path": ".",
                                "tags": ["metarepo"],
                                "url": "git@github.com:genius-systems/gameta.git"
                            }
                        },
                        'virtualenvs': {}
                    }
                )

    @patch('gameta.cli.click.Context.ensure_object')
    def test_venv_unregister_virtualenv_unregistered_and_deleted(self, mock_ensure_object):
        params = {
            'name': 'test',
            'directory': 'test'
        }
        with self.runner.isolated_filesystem() as f:
            venv.create(params['directory'], clear=False, with_pip=True, symlinks=False, system_site_packages=False)
            with open(join(dirname(__file__), 'data', '.gameta'), 'r') as m1:
                output = json.load(m1)
                with open(join(f, '.gameta'), 'w') as m2:
                    output.update({'virtualenvs': {params['name']: join(f, params['directory'])}})
                    json.dump(output, m2)
            context = GametaContext()
            context.project_dir = f
            context.load()
            mock_ensure_object.return_value = context
            result = self.runner.invoke(self.unregister, ['-n', params['name'], '-d'])
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                f"Deleting virtualenv {params['name']} in path {join(f, params['directory'])}\n"
                f"Unregistering virtualenv {params['name']}\n"
                f"Virtualenv {params['name']} successfully unregistered\n"
            )
            self.assertCountEqual(listdir(f), ['.gameta', '.gitignore'])
            with open(join(f, '.gameta')) as m:
                self.assertEqual(
                    json.load(m),
                    {
                        "version": '0.3.0',
                        'repositories': {
                            "gameta": {
                                "__metarepo__": True,
                                "path": ".",
                                "tags": ["metarepo"],
                                "url": "git@github.com:genius-systems/gameta.git"
                            }
                        },
                        'virtualenvs': {}
                    }
                )

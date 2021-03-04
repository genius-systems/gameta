import json
import zipfile
from os import listdir
from os.path import join, dirname, exists
from shutil import copyfile
from unittest import TestCase
from unittest.mock import patch

from click.testing import CliRunner

from gameta.context import GametaContext
from gameta.repos import add, delete, ls, update


class TestReposAdd(TestCase):
    def setUp(self) -> None:
        self.maxDiff = None
        self.runner = CliRunner()
        self.add = add

    @patch('gameta.cli.click.Context.ensure_object')
    def test_repos_add_key_parameters_not_provided(self, mock_ensure_object):
        with self.runner.isolated_filesystem() as f:
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'git.zip'), 'r') as template:
                template.extractall(f)
            copyfile(join(dirname(__file__), 'data', '.meta'), join(f, '.meta'))
            context = GametaContext()
            context.project_dir = f
            context.load()
            mock_ensure_object.return_value = context
            result = self.runner.invoke(self.add)
            self.assertEqual(result.exit_code, 2)
            self.assertEqual(
                result.output,
                "Usage: add [OPTIONS]\n"
                "Try 'add --help' for help.\n"
                "\n"
                "Error: Missing option '--name' / '-n'.\n"
            )

    @patch('gameta.cli.click.Context.ensure_object')
    def test_repos_add_repository_added_to_meta_file_and_create_gitignore_and_clone(self, mock_ensure_object):
        params = {
            'name': 'GitPython',
            'url': 'https://github.com/gitpython-developers/GitPython.git',
            'path': 'GitPython'
        }
        with self.runner.isolated_filesystem() as f:
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'git.zip'), 'r') as template:
                template.extractall(f)
            copyfile(join(dirname(__file__), 'data', '.meta'), join(f, '.meta'))
            context = GametaContext()
            context.project_dir = f
            context.load()
            mock_ensure_object.return_value = context
            result = self.runner.invoke(
                self.add, ['--name', params['name'], '--url', params['url'], '--path', params['path']]
            )
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                f'Adding git repository {params["name"]}, {params["url"]} to '
                f'{join(f, params["path"])}\n'
                f'Repository {params["name"]} has been added locally\n'
                f'Adding {params["name"]} to .meta file\n'
                f'Successfully added repository {params["name"]}\n'
            )
            self.assertTrue(exists(join(f, 'GitPython')))
            self.assertTrue(all(i in listdir(join(f, 'GitPython')) for i in ['git', 'doc', 'test']))
            with open(join(f, '.meta'), 'r') as m:
                self.assertEqual(
                    json.load(m),
                    {
                        "projects": {
                            "gameta": {
                                "path": ".",
                                "tags": ["metarepo"],
                                "url": "git@github.com:genius-systems/gameta.git",
                                '__metarepo__': True
                            },
                            "GitPython": {
                                'url': 'https://github.com/gitpython-developers/GitPython.git',
                                'path': 'GitPython',
                                '__metarepo__': False
                            }
                        }
                    }
                )
            self.assertTrue(exists(join(f, '.gitignore')))
            with open(join(f, '.gitignore'), 'r') as g:
                self.assertCountEqual(g.readlines(), ['GitPython/\n'])

    @patch('gameta.cli.click.Context.ensure_object')
    def test_repos_add_repository_added_to_meta_file_and_add_path_to_gitignore_and_clone(self, mock_ensure_object):
        params = {
            'name': 'GitPython',
            'url': 'https://github.com/gitpython-developers/GitPython.git',
            'path': 'GitPython'
        }
        with self.runner.isolated_filesystem() as f:
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'git.zip'), 'r') as template:
                template.extractall(f)
            copyfile(join(dirname(__file__), 'data', '.meta'), join(f, '.meta'))
            copyfile(join(dirname(__file__), 'data', '.gitignore'), join(f, '.gitignore'))
            context = GametaContext()
            context.project_dir = f
            context.load()
            mock_ensure_object.return_value = context
            result = self.runner.invoke(
                self.add, ['--name', params['name'], '--url', params['url'], '--path', params['path']]
            )
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                f'Adding git repository {params["name"]}, {params["url"]} to '
                f'{join(f, params["path"])}\n'
                f'Repository {params["name"]} has been added locally\n'
                f'Adding {params["name"]} to .meta file\n'
                f'Successfully added repository {params["name"]}\n'
            )
            self.assertTrue(exists(join(f, 'GitPython')))
            self.assertTrue(all(i in listdir(join(f, 'GitPython')) for i in ['git', 'doc', 'test']))
            with open(join(f, '.meta'), 'r') as m:
                self.assertEqual(
                    json.load(m),
                    {
                        "projects": {
                            "gameta": {
                                "path": ".",
                                "tags": ["metarepo"],
                                "url": "git@github.com:genius-systems/gameta.git",
                                '__metarepo__': True
                            },
                            "GitPython": {
                                'url': 'https://github.com/gitpython-developers/GitPython.git',
                                'path': 'GitPython',
                                '__metarepo__': False
                            }
                        }
                    }
                )
            self.assertTrue(exists(join(f, '.gitignore')))
            with open(join(f, '.gitignore'), 'r') as g:
                self.assertTrue('GitPython/\n' in g.readlines())

    @patch('gameta.cli.click.Context.ensure_object')
    def test_repos_add_invalid_repository(self, mock_ensure_object):
        params = {
            'name': 'GitPython',
            'url': 'https://test.git',
            'path': 'GitPython',
        }
        with self.runner.isolated_filesystem() as f:
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'git.zip'), 'r') as template:
                template.extractall(f)
            copyfile(join(dirname(__file__), 'data', '.meta'), join(f, '.meta'))
            context = GametaContext()
            context.project_dir = f
            context.load()
            mock_ensure_object.return_value = context
            result = self.runner.invoke(
                self.add, ['--name', params['name'], '--url', params['url'], '--path', params['path']]
            )
            self.assertEqual(result.exit_code, 1)
            self.assertEqual(
                result.output,
                f'Adding git repository {params["name"]}, {params["url"]} to '
                f'{join(f, params["path"])}\n'
                f'Error: Error cloning {params["name"]} into directory {join(f, params["path"])}: '
                f"GitCommandError.Cmd('git') failed due to: exit code(128)\n"
                f"  cmdline: git clone -v {params['url']} {join(f, params['path'])}\n"
                f"  stderr: 'Cloning into '{join(f, params['path'])}'...\n" +
                "fatal: unable to access '{url}': Could not resolve host: {host}\n'\n".format(
                    url=params["url"] + '/', host=params["url"].split('https://')[1]
                )
            )
            self.assertFalse(exists(join(f, 'GitPython')))
            with open(join(f, '.meta'), 'r') as m:
                self.assertEqual(
                    json.load(m),
                    {
                        "projects": {
                            "gameta": {
                                "path": ".",
                                "tags": ["metarepo"],
                                "url": "git@github.com:genius-systems/gameta.git",
                                '__metarepo__': True
                            }
                        }
                    }
                )

    @patch('gameta.cli.click.Context.ensure_object')
    def test_repos_add_repository_already_exists_in_meta_file(self, mock_ensure_object):
        params = {
            'name': 'GitPython',
            'url': 'https://github.com/gitpython-developers/GitPython.git',
            'path': 'GitPython',
        }
        with self.runner.isolated_filesystem() as f:
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'git.zip'), 'r') as template:
                template.extractall(f)
            with open(join(dirname(__file__), 'data', '.meta'), 'r') as m1:
                output = json.load(m1)
                with open(join(f, '.meta'), 'w+') as m2:
                    output['projects']['GitPython'] = {
                        "url": 'https://github.com/gitpython-developers/GitPython.git',
                        'path': 'GitPython',
                        "tags": ['a', 'b', 'c'],
                        '__metarepo__': False
                    }
                    json.dump(output, m2)
            context = GametaContext()
            context.project_dir = f
            context.load()
            mock_ensure_object.return_value = context
            result = self.runner.invoke(
                self.add, ['--name', params['name'], '--url', params['url'], '--path', params['path']]
            )
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                f'Adding git repository {params["name"]}, {params["url"]} to '
                f'{join(f, params["path"])}\n'
                f'Repository {params["name"]} has been added locally\n'
                f'Repository {params["name"]} has already been added to .meta file\n'
            )
            self.assertTrue(exists(join(f, 'GitPython')))
            self.assertTrue(all(i in listdir(join(f, 'GitPython')) for i in ['git', 'doc', 'test']))
            with open(join(f, '.meta'), 'r') as m:
                self.assertEqual(
                    json.load(m),
                    {
                        "projects": {
                            "gameta": {
                                "path": ".",
                                "tags": ["metarepo"],
                                "url": "git@github.com:genius-systems/gameta.git",
                                '__metarepo__': True
                            },
                            "GitPython": {
                                'url': 'https://github.com/gitpython-developers/GitPython.git',
                                'path': 'GitPython',
                                "tags": ['a', 'b', 'c'],
                                '__metarepo__': False
                            }
                        }
                    }
                )

    @patch('gameta.cli.click.Context.ensure_object')
    def test_repos_add_repository_already_exists_in_meta_file_overwritten(self, mock_ensure_object):
        params = {
            'name': 'GitPython',
            'url': 'https://github.com/gitpython-developers/gitdb.git',
            'path': 'GitPython',
        }
        with self.runner.isolated_filesystem() as f:
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'git.zip'), 'r') as template:
                template.extractall(f)
            with open(join(dirname(__file__), 'data', '.meta'), 'r') as m1:
                output = json.load(m1)
                with open(join(f, '.meta'), 'w+') as m2:
                    output['projects']['GitPython'] = {
                        "url": 'https://github.com/gitpython-developers/GitPython.git',
                        'path': 'GitPython',
                        "__metarepo__": False,
                    }
                    json.dump(output, m2)
            context = GametaContext()
            context.project_dir = f
            context.load()
            mock_ensure_object.return_value = context
            result = self.runner.invoke(
                self.add, ['--name', params['name'], '--url', params['url'], '--path', params['path'], '-o']
            )
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                f'Adding git repository {params["name"]}, {params["url"]} to '
                f'{join(f, params["path"])}\n'
                f'Repository {params["name"]} has been added locally\n'
                f'Overwriting repository {params["name"]} in .meta file\n'
                f'Successfully added repository {params["name"]}\n'
            )
            self.assertTrue(exists(join(f, 'GitPython')))
            self.assertTrue(all(i in listdir(join(f, 'GitPython')) for i in ['gitdb', 'doc', 'setup.py']))
            with open(join(f, '.meta'), 'r') as m:
                self.assertEqual(
                    json.load(m),
                    {
                        "projects": {
                            "gameta": {
                                "path": ".",
                                "tags": ["metarepo"],
                                "url": "git@github.com:genius-systems/gameta.git",
                                '__metarepo__': True
                            },
                            "GitPython": {
                                'url': 'https://github.com/gitpython-developers/gitdb.git',
                                'path': 'GitPython',
                                '__metarepo__': False
                            }
                        }
                    }
                )
            self.assertTrue(exists(join(f, '.gitignore')))
            with open(join(f, '.gitignore'), 'r') as g:
                self.assertCountEqual(g.readlines(), ['GitPython/\n'])

    @patch('gameta.cli.click.Context.ensure_object')
    def test_repos_add_repository_already_exists_locally(self, mock_ensure_object):
        params = {
            'name': 'GitPython',
            'url': 'https://github.com/gitpython-developers/GitPython.git',
            'path': 'GitPython',
        }
        with self.runner.isolated_filesystem() as f:
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'git.zip'), 'r') as template:
                template.extractall(f)
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'gitpython.zip'), 'r') as template:
                template.extractall(f)
            copyfile(join(dirname(__file__), 'data', '.meta'), join(f, '.meta'))
            context = GametaContext()
            context.project_dir = f
            context.load()
            mock_ensure_object.return_value = context
            result = self.runner.invoke(
                self.add, ['--name', params['name'], '--url', params['url'], '--path', params['path']]
            )
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                f'Adding git repository {params["name"]}, {params["url"]} to '
                f'{join(f, params["path"])}\n'
                f'Repository {params["name"]} exists locally, skipping clone\n'
                f'Repository {params["name"]} has been added locally\n'
                f'Adding {params["name"]} to .meta file\n'
                f'Successfully added repository {params["name"]}\n'
            )
            self.assertTrue(exists(join(f, 'GitPython')))
            self.assertTrue(all(i in listdir(join(f, 'GitPython')) for i in ['git', 'doc', 'test']))
            with open(join(f, '.meta'), 'r') as m:
                self.assertEqual(
                    json.load(m),
                    {
                        "projects": {
                            "gameta": {
                                "path": ".",
                                "tags": ["metarepo"],
                                "url": "git@github.com:genius-systems/gameta.git",
                                '__metarepo__': True
                            },
                            "GitPython": {
                                'url': 'https://github.com/gitpython-developers/GitPython.git',
                                'path': 'GitPython',
                                '__metarepo__': False
                            }
                        }
                    }
                )
            self.assertTrue(exists(join(f, '.gitignore')))
            with open(join(f, '.gitignore'), 'r') as g:
                self.assertCountEqual(g.readlines(), ['GitPython/\n'])

    @patch('gameta.cli.click.Context.ensure_object')
    def test_repos_add_repository_already_exists_locally_and_in_meta_file(self, mock_ensure_object):
        params = {
            'name': 'GitPython',
            'url': 'https://github.com/gitpython-developers/GitPython.git',
            'path': 'GitPython',
        }
        with self.runner.isolated_filesystem() as f:
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'git.zip'), 'r') as template:
                template.extractall(f)
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'gitpython.zip'), 'r') as template:
                template.extractall(f)
            with open(join(dirname(__file__), 'data', '.meta'), 'r') as m1:
                output = json.load(m1)
                with open(join(f, '.meta'), 'w+') as m2:
                    output['projects']['GitPython'] = {
                        "url": 'https://github.com/gitpython-developers/GitPython.git',
                        'path': 'GitPython',
                        '__metarepo__': False
                    }
                    json.dump(output, m2)
            context = GametaContext()
            context.project_dir = f
            context.load()
            mock_ensure_object.return_value = context
            result = self.runner.invoke(
                self.add, ['--name', params['name'], '--url', params['url'], '--path', params['path']]
            )
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                f'Adding git repository {params["name"]}, {params["url"]} to '
                f'{join(f, params["path"])}\n'
                f'Repository {params["name"]} exists locally, skipping clone\n'
                f'Repository {params["name"]} has been added locally\n'
                f'Repository {params["name"]} has already been added to .meta file\n'
            )
            self.assertTrue(exists(join(f, 'GitPython')))
            self.assertTrue(all(i in listdir(join(f, 'GitPython')) for i in ['git', 'doc', 'test']))
            with open(join(f, '.meta'), 'r') as m:
                self.assertEqual(
                    json.load(m),
                    {
                        "projects": {
                            "gameta": {
                                "path": ".",
                                "tags": ["metarepo"],
                                "url": "git@github.com:genius-systems/gameta.git",
                                '__metarepo__': True
                            },
                            "GitPython": {
                                'url': 'https://github.com/gitpython-developers/GitPython.git',
                                'path': 'GitPython',
                                '__metarepo__': False
                            }
                        }
                    }
                )

    @patch('gameta.cli.click.Context.ensure_object')
    def test_repos_add_repository_already_exists_locally_parameters_differ(self, mock_ensure_object):
        params = {
            'name': 'GitPython',
            'url': 'https://test.git',
            'path': 'GitPython',
        }
        with self.runner.isolated_filesystem() as f:
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'git.zip'), 'r') as template:
                template.extractall(f)
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'gitpython.zip'), 'r') as template:
                template.extractall(f)
            copyfile(join(dirname(__file__), 'data', '.meta'), join(f, '.meta'))
            context = GametaContext()
            context.project_dir = f
            context.load()
            mock_ensure_object.return_value = context
            result = self.runner.invoke(
                self.add, ['--name', params['name'], '--url', params['url'], '--path', params['path']]
            )
            self.assertEqual(result.exit_code, 1)
            self.assertEqual(
                result.output,
                f'Adding git repository {params["name"]}, {params["url"]} to '
                f'{join(f, params["path"])}\n'
                f'Error: URL of repository at {join(f, params["name"])} '
                f'(https://github.com/gitpython-developers/GitPython.git) '
                f'does not match the requested url {params["url"]}\n'
            )
            with open(join(f, '.meta'), 'r') as m:
                self.assertEqual(
                    json.load(m),
                    {
                        "projects": {
                            "gameta": {
                                "path": ".",
                                "tags": ["metarepo"],
                                "url": "git@github.com:genius-systems/gameta.git",
                                '__metarepo__': True
                            }
                        }
                    }
                )


class TestReposDelete(TestCase):
    def setUp(self) -> None:
        self.maxDiff = None
        self.runner = CliRunner()
        self.delete = delete

    @patch('gameta.cli.click.Context.ensure_object')
    def test_repos_delete_key_parameters_not_provided(self, mock_ensure_object):
        with self.runner.isolated_filesystem() as f:
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'git.zip'), 'r') as template:
                template.extractall(f)
            copyfile(join(dirname(__file__), 'data', '.meta'), join(f, '.meta'))
            context = GametaContext()
            context.project_dir = f
            context.load()
            mock_ensure_object.return_value = context
            result = self.runner.invoke(self.delete)
            self.assertEqual(result.exit_code, 2)
            self.assertEqual(
                result.output,
                "Usage: delete [OPTIONS]\n"
                "Try 'delete --help' for help.\n"
                "\n"
                "Error: Missing option '--name' / '-n'.\n"
            )

    @patch('gameta.cli.click.Context.ensure_object')
    def test_repos_delete_repository_deleted_and_cleared_gitignore_does_not_exist(self, mock_ensure_object):
        params = {
            'name': 'GitPython'
        }
        with self.runner.isolated_filesystem() as f:
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'git.zip'), 'r') as template:
                template.extractall(f)
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'gitpython.zip'), 'r') as template:
                template.extractall(f)
            with open(join(dirname(__file__), 'data', '.meta'), 'r') as m1:
                output = json.load(m1)
                with open(join(f, '.meta'), 'w+') as m2:
                    output['projects']['GitPython'] = {
                        "url": 'https://github.com/gitpython-developers/GitPython.git',
                        'path': 'GitPython',
                        'tags': ['a', 'b', 'c'],
                        "__metarepo__": False
                    }
                    json.dump(output, m2)
            context = GametaContext()
            context.project_dir = f
            context.load()
            mock_ensure_object.return_value = context
            result = self.runner.invoke(self.delete, ['--name', params['name']])
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                f"Deleting repository {params['name']} from .meta file\n"
                f"Clearing repository {params['name']} locally\n"
                f"Repository {params['name']} successfully deleted\n"
            )
            self.assertFalse(exists(join(f, 'GitPython')))
            with open(join(f, '.meta'), 'r') as m:
                self.assertEqual(
                    json.load(m),
                    {
                        "projects": {
                            "gameta": {
                                "path": ".",
                                "tags": ["metarepo"],
                                "url": "git@github.com:genius-systems/gameta.git",
                                '__metarepo__': True
                            }
                        }
                    }
                )
            self.assertTrue(exists(join(f, '.gitignore')))
            with open(join(f, '.gitignore'), 'r') as g:
                self.assertCountEqual(g.readlines(), [])

    @patch('gameta.cli.click.Context.ensure_object')
    def test_repos_delete_repository_deleted_and_cleared_gitignore_exist_but_does_not_contain_path(self, mock_ensure_object):
        params = {
            'name': 'GitPython'
        }
        with self.runner.isolated_filesystem() as f:
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'git.zip'), 'r') as template:
                template.extractall(f)
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'gitpython.zip'), 'r') as template:
                template.extractall(f)
            with open(join(dirname(__file__), 'data', '.meta'), 'r') as m1:
                output = json.load(m1)
                with open(join(f, '.meta'), 'w+') as m2:
                    output['projects']['GitPython'] = {
                        "url": 'https://github.com/gitpython-developers/GitPython.git',
                        'path': 'GitPython',
                        'tags': ['a', 'b', 'c'],
                        "__metarepo__": False
                    }
                    json.dump(output, m2)
            copyfile(join(dirname(__file__), 'data', '.gitignore'), join(f, '.gitignore'))
            context = GametaContext()
            context.project_dir = f
            context.load()
            mock_ensure_object.return_value = context
            result = self.runner.invoke(self.delete, ['--name', params['name']])
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                f"Deleting repository {params['name']} from .meta file\n"
                f"Clearing repository {params['name']} locally\n"
                f"Repository {params['name']} successfully deleted\n"
            )
            self.assertFalse(exists(join(f, 'GitPython')))
            with open(join(f, '.meta'), 'r') as m:
                self.assertEqual(
                    json.load(m),
                    {
                        "projects": {
                            "gameta": {
                                "path": ".",
                                "tags": ["metarepo"],
                                "url": "git@github.com:genius-systems/gameta.git",
                                '__metarepo__': True
                            }
                        }
                    }
                )
            self.assertTrue(exists(join(f, '.gitignore')))
            with open(join(f, '.gitignore'), 'r') as g:
                self.assertFalse("GitPython/\n" in g.readlines())

    @patch('gameta.cli.click.Context.ensure_object')
    def test_repos_delete_repository_deleted_and_cleared_gitignore_exist_and_contains_path(self, mock_ensure_object):
        params = {
            'name': 'GitPython'
        }
        with self.runner.isolated_filesystem() as f:
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'git.zip'), 'r') as template:
                template.extractall(f)
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'gitpython.zip'), 'r') as template:
                template.extractall(f)
            with open(join(dirname(__file__), 'data', '.meta'), 'r') as m1:
                output = json.load(m1)
                with open(join(f, '.meta'), 'w+') as m2:
                    output['projects']['GitPython'] = {
                        "url": 'https://github.com/gitpython-developers/GitPython.git',
                        'path': 'GitPython',
                        'tags': ['a', 'b', 'c'],
                        "__metarepo__": False
                    }
                    json.dump(output, m2)
            with open(join(dirname(__file__), 'data', '.gitignore'), 'r') as g1:
                output = g1.readlines()
                with open(join(f, '.gitignore'), 'w+') as g2:
                    output.append('GitPython/\n')
                    g2.writelines(output)
            context = GametaContext()
            context.project_dir = f
            context.load()
            mock_ensure_object.return_value = context
            result = self.runner.invoke(self.delete, ['--name', params['name']])
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                f"Deleting repository {params['name']} from .meta file\n"
                f"Clearing repository {params['name']} locally\n"
                f"Repository {params['name']} successfully deleted\n"
            )
            self.assertFalse(exists(join(f, 'GitPython')))
            with open(join(f, '.meta'), 'r') as m:
                self.assertEqual(
                    json.load(m),
                    {
                        "projects": {
                            "gameta": {
                                "path": ".",
                                "tags": ["metarepo"],
                                "url": "git@github.com:genius-systems/gameta.git",
                                '__metarepo__': True
                            }
                        }
                    }
                )
            self.assertTrue(exists(join(f, '.gitignore')))
            with open(join(f, '.gitignore'), 'r') as g:
                self.assertFalse("GitPython/\n" in g.readlines())

    @patch('gameta.cli.click.Context.ensure_object')
    def test_repos_delete_repository_deleted_but_not_cleared(self, mock_ensure_object):
        params = {
            'name': 'GitPython'
        }
        with self.runner.isolated_filesystem() as f:
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'git.zip'), 'r') as template:
                template.extractall(f)
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'gitpython.zip'), 'r') as template:
                template.extractall(f)
            with open(join(dirname(__file__), 'data', '.meta'), 'r') as m1:
                output = json.load(m1)
                with open(join(f, '.meta'), 'w+') as m2:
                    output['projects']['GitPython'] = {
                        "url": 'https://github.com/gitpython-developers/GitPython.git',
                        'path': 'GitPython',
                        'tags': ['a', 'b', 'c'],
                        "__metarepo__": False
                    }
                    json.dump(output, m2)
            context = GametaContext()
            context.project_dir = f
            context.load()
            mock_ensure_object.return_value = context
            result = self.runner.invoke(self.delete, ['--name', params['name'], '-c'])
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                f"Deleting repository {params['name']} from .meta file\n"
                f"Repository {params['name']} successfully deleted\n"
            )
            self.assertTrue(exists(join(f, 'GitPython')))
            self.assertTrue(all(i in listdir(join(f, 'GitPython')) for i in ['git', 'doc', 'test']))
            with open(join(f, '.meta'), 'r') as m:
                self.assertEqual(
                    json.load(m),
                    {
                        "projects": {
                            "gameta": {
                                "path": ".",
                                "tags": ["metarepo"],
                                "url": "git@github.com:genius-systems/gameta.git",
                                '__metarepo__': True
                            }
                        }
                    }
                )

    @patch('gameta.cli.click.Context.ensure_object')
    def test_repos_delete_repository_does_not_exist(self, mock_ensure_object):
        params = {
            'name': 'GitPython'
        }
        with self.runner.isolated_filesystem() as f:
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'git.zip'), 'r') as template:
                template.extractall(f)
            copyfile(join(dirname(__file__), 'data', '.meta'), join(f, '.meta'))
            context = GametaContext()
            context.project_dir = f
            context.load()
            mock_ensure_object.return_value = context
            result = self.runner.invoke(self.delete, ['--name', params['name'], '-c'])
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                f"Deleting repository {params['name']} from .meta file\n"
                f"Repository {params['name']} does not exist in the .meta file, ignoring\n"
            )
            with open(join(f, '.meta'), 'r') as m:
                self.assertEqual(
                    json.load(m),
                    {
                        "projects": {
                            "gameta": {
                                "path": ".",
                                "tags": ["metarepo"],
                                "url": "git@github.com:genius-systems/gameta.git",
                                '__metarepo__': True
                            }
                        }
                    }
                )

    @patch('gameta.cli.click.Context.ensure_object')
    def test_repos_delete_repository_attempting_to_delete_metarepo(self, mock_ensure_object):
        params = {
            'name': 'gameta'
        }
        with self.runner.isolated_filesystem() as f:
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'git.zip'), 'r') as template:
                template.extractall(f)
            copyfile(join(dirname(__file__), 'data', '.meta'), join(f, '.meta'))
            context = GametaContext()
            context.project_dir = f
            context.load()
            mock_ensure_object.return_value = context
            result = self.runner.invoke(self.delete, ['--name', params['name']])
            self.assertEqual(result.exit_code, 1)
            self.assertEqual(
                result.output,
                f"Deleting repository {params['name']} from .meta file\n"
                f"Error: Cannot delete repository {params['name']} as it is a metarepo\n"
            )
            with open(join(f, '.meta'), 'r') as m:
                self.assertEqual(
                    json.load(m),
                    {
                        "projects": {
                            "gameta": {
                                "path": ".",
                                "tags": ["metarepo"],
                                "url": "git@github.com:genius-systems/gameta.git",
                                '__metarepo__': True
                            }
                        }
                    }
                )


class TestRepoLs(TestCase):
    def setUp(self) -> None:
        self.maxDiff = None
        self.runner = CliRunner()
        self.ls = ls

    @patch('gameta.cli.click.Context.ensure_object')
    def test_repos_ls_repositories_available(self, mock_ensure_object):
        with self.runner.isolated_filesystem() as f:
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'git.zip'), 'r') as template:
                template.extractall(f)
            with open(join(dirname(__file__), 'data', '.meta'), 'r') as m1:
                output = json.load(m1)
                with open(join(f, '.meta'), 'w+') as m2:
                    output['projects']['GitPython'] = {
                        "url": 'https://github.com/gitpython-developers/GitPython.git',
                        'path': 'GitPython',
                        'tags': ['a', 'b', 'c'],
                        "__metarepo__": False
                    }
                    output['projects']['genisys'] = {
                        "url": 'https://github.com/test/genisys.git',
                        "path": "core/genisys",
                        'tags': ['c', 'd', 'e'],
                        "__metarepo__": False
                    }
                    json.dump(output, m2)
            context = GametaContext()
            context.project_dir = f
            context.load()
            mock_ensure_object.return_value = context
            result = self.runner.invoke(self.ls)
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                f"Listing repositories managed in metarepo {f}\n"
                "gameta\n"
                "GitPython\n"
                "genisys\n"
            )

    @patch('gameta.cli.click.Context.ensure_object')
    def test_repos_ls_no_repositories_available(self, mock_ensure_object):
        with self.runner.isolated_filesystem() as f:
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'git.zip'), 'r') as template:
                template.extractall(f)
            with open(join(f, '.meta'), 'w') as m:
                json.dump(
                    {
                        'projects': {}
                    }, m
                )
            context = GametaContext()
            context.project_dir = f
            context.load()
            mock_ensure_object.return_value = context
            result = self.runner.invoke(self.ls)
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                f"Listing repositories managed in metarepo {f}\n"
            )


class TestRepoUpdate(TestCase):
    def setUp(self) -> None:
        self.maxDiff = None
        self.runner = CliRunner()
        self.update = update

    @patch('gameta.cli.click.Context.ensure_object')
    def test_repos_update_key_parameters_not_provided(self, mock_ensure_object):
        with self.runner.isolated_filesystem() as f:
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'git.zip'), 'r') as template:
                template.extractall(f)
            copyfile(join(dirname(__file__), 'data', '.meta_other_repos'), join(f, '.meta'))
            context = GametaContext()
            context.project_dir = f
            context.load()
            mock_ensure_object.return_value = context
            result = self.runner.invoke(self.update)
            self.assertEqual(result.exit_code, 2)
            self.assertEqual(
                result.output,
                "Usage: update [OPTIONS]\n"
                "Try 'update --help' for help.\n"
                "\n"
                "Error: Missing option '--name' / '-n'.\n"
            )

    @patch('gameta.cli.click.Context.ensure_object')
    def test_repos_update_name_does_not_exist_in_repo(self, mock_ensure_object):
        params = {
            'name': 'test'
        }
        with self.runner.isolated_filesystem() as f:
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'git.zip'), 'r') as template:
                template.extractall(f)
            copyfile(join(dirname(__file__), 'data', '.meta_other_repos'), join(f, '.meta'))
            context = GametaContext()
            context.project_dir = f
            context.load()
            mock_ensure_object.return_value = context
            result = self.runner.invoke(self.update, ['--name', params['name']])
            self.assertEqual(result.exit_code, 1)
            self.assertEqual(
                result.output,
                f'Error: Repository {params["name"]} does not exist in the .meta file, please add it first\n'
            )

    @patch('gameta.cli.click.Context.ensure_object')
    def test_repos_update_all_parameters_updated_gitignore_created(self, mock_ensure_object):
        params = {
            'name': 'GitPython',
            'new_name': 'test',
            'new_url': 'https://github.com/jantman/GitPython.git',
            'new_path': 'core/GitPython',
        }
        with self.runner.isolated_filesystem() as f:
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'git.zip'), 'r') as template:
                template.extractall(f)
            copyfile(join(dirname(__file__), 'data', '.meta_other_repos'), join(f, '.meta'))
            context = GametaContext()
            context.project_dir = f
            context.load()
            mock_ensure_object.return_value = context
            result = self.runner.invoke(
                self.update,
                [
                    '--name', params['name'],
                    '-e', params['new_name'],
                    '-u', params['new_url'],
                    '-p', params['new_path'],
                    '-s'
                ]
            )
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                f'Updating repository GitPython with new details (name: {params["new_name"]}, '
                f'url: {params["new_url"]}, path: {params["new_path"]})\n'
                f'Successfully updated repository {params["new_name"]} with new details\n'
            )
            with open(join(f, '.meta')) as m:
                self.assertEqual(
                    json.load(m),
                    {
                        'projects': {
                            "gameta": {
                                "path": ".",
                                "tags": ["metarepo"],
                                "url": "git@github.com:genius-systems/gameta.git",
                                '__metarepo__': True
                            },
                            "test": {
                                "path": "core/GitPython",
                                "tags": ["a", "b", "c"],
                                "url": "https://github.com/jantman/GitPython.git",
                                '__metarepo__': False
                            },
                            "gitdb": {
                                "path": "core/gitdb",
                                "tags": ["a", "c", "d"],
                                "url": "https://github.com/gitpython-developers/gitdb.git",
                                '__metarepo__': False
                            }
                        }
                    }
                )
            self.assertTrue(exists(join(f, '.gitignore')))
            with open(join(f, '.gitignore'), 'r') as g:
                self.assertTrue("core/GitPython/\n" in g.readlines())

    @patch('gameta.cli.click.Context.ensure_object')
    def test_repos_update_all_parameters_updated_gitignore_exists_but_does_not_contain_path(self, mock_ensure_object):
        params = {
            'name': 'GitPython',
            'new_name': 'test',
            'new_url': 'https://github.com/jantman/GitPython.git',
            'new_path': 'core/GitPython',
        }
        with self.runner.isolated_filesystem() as f:
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'git.zip'), 'r') as template:
                template.extractall(f)
            copyfile(join(dirname(__file__), 'data', '.meta_other_repos'), join(f, '.meta'))
            copyfile(join(dirname(__file__), 'data', '.gitignore'), join(f, '.gitignore'))
            context = GametaContext()
            context.project_dir = f
            context.load()
            mock_ensure_object.return_value = context
            result = self.runner.invoke(
                self.update,
                [
                    '--name', params['name'],
                    '-e', params['new_name'],
                    '-u', params['new_url'],
                    '-p', params['new_path'],
                    '-s'
                ]
            )
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                f'Updating repository GitPython with new details (name: {params["new_name"]}, '
                f'url: {params["new_url"]}, path: {params["new_path"]})\n'
                f'Successfully updated repository {params["new_name"]} with new details\n'
            )
            with open(join(f, '.meta')) as m:
                self.assertEqual(
                    json.load(m),
                    {
                        'projects': {
                            "gameta": {
                                "path": ".",
                                "tags": ["metarepo"],
                                "url": "git@github.com:genius-systems/gameta.git",
                                '__metarepo__': True
                            },
                            "test": {
                                "path": "core/GitPython",
                                "tags": ["a", "b", "c"],
                                "url": "https://github.com/jantman/GitPython.git",
                                '__metarepo__': False
                            },
                            "gitdb": {
                                "path": "core/gitdb",
                                "tags": ["a", "c", "d"],
                                "url": "https://github.com/gitpython-developers/gitdb.git",
                                '__metarepo__': False
                            }
                        }
                    }
                )
            self.assertTrue(exists(join(f, '.gitignore')))
            with open(join(f, '.gitignore'), 'r') as g:
                self.assertTrue("core/GitPython/\n" in g.readlines())

    @patch('gameta.cli.click.Context.ensure_object')
    def test_repos_update_all_parameters_updated_gitignore_exists_and_contains_path(self, mock_ensure_object):
        params = {
            'name': 'GitPython',
            'new_name': 'test',
            'new_url': 'https://github.com/jantman/GitPython.git',
            'new_path': 'core/GitPython',
            'sync': False
        }
        with self.runner.isolated_filesystem() as f:
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'git.zip'), 'r') as template:
                template.extractall(f)
            copyfile(join(dirname(__file__), 'data', '.meta_other_repos'), join(f, '.meta'))
            with open(join(dirname(__file__), 'data', '.gitignore'), 'r') as g1:
                output = g1.readlines()
                with open(join(f, '.gitignore'), 'w+') as g2:
                    output.append('GitPython/\n')
                    output.append('core/gitdb/\n')
                    g2.writelines(output)
            context = GametaContext()
            context.project_dir = f
            context.load()
            mock_ensure_object.return_value = context
            result = self.runner.invoke(
                self.update,
                [
                    '--name', params['name'],
                    '-e', params['new_name'],
                    '-u', params['new_url'],
                    '-p', params['new_path'],
                    '-s'
                ]
            )
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                f'Updating repository GitPython with new details (name: {params["new_name"]}, '
                f'url: {params["new_url"]}, path: {params["new_path"]})\n'
                f'Successfully updated repository {params["new_name"]} with new details\n'
            )
            with open(join(f, '.meta')) as m:
                self.assertEqual(
                    json.load(m),
                    {
                        'projects': {
                            "gameta": {
                                "path": ".",
                                "tags": ["metarepo"],
                                "url": "git@github.com:genius-systems/gameta.git",
                                '__metarepo__': True
                            },
                            "test": {
                                "path": "core/GitPython",
                                "tags": ["a", "b", "c"],
                                "url": "https://github.com/jantman/GitPython.git",
                                '__metarepo__': False
                            },
                            "gitdb": {
                                "path": "core/gitdb",
                                "tags": ["a", "c", "d"],
                                "url": "https://github.com/gitpython-developers/gitdb.git",
                                '__metarepo__': False
                            }
                        }
                    }
                )
            self.assertTrue(exists(join(f, '.gitignore')))
            with open(join(f, '.gitignore'), 'r') as g:
                output = g.readlines()
                self.assertTrue("core/gitdb/\n" in output)
                self.assertTrue("core/GitPython/\n" in output)

    @patch('gameta.cli.click.Context.ensure_object')
    def test_repos_update_all_parameters_updated_with_physical_sync(self, mock_ensure_object):
        params = {
            'name': 'GitPython',
            'new_name': 'test',
            'new_url': 'https://github.com/jantman/GitPython.git',
            'new_path': 'core/GitPython',
        }
        with self.runner.isolated_filesystem() as f:
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'git.zip'), 'r') as template:
                template.extractall(f)
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'gitpython.zip'), 'r') as template:
                template.extractall(f)
            copyfile(join(dirname(__file__), 'data', '.meta_other_repos'), join(f, '.meta'))
            context = GametaContext()
            context.project_dir = f
            context.load()
            mock_ensure_object.return_value = context
            result = self.runner.invoke(
                self.update,
                [
                    '--name', params['name'],
                    '-e', params['new_name'],
                    '-u', params['new_url'],
                    '-p', params['new_path']
                ]
            )
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                f'Updating repository GitPython with new details (name: {params["new_name"]}, '
                f'url: {params["new_url"]}, path: {params["new_path"]})\n'
                "Performing a physical sync\n"
                f"Cloning repository from new URL: {params['new_url']}\n"
                "Sync complete\n"
                f'Successfully updated repository {params["new_name"]} with new details\n'
            )
            with open(join(f, '.meta')) as m:
                self.assertEqual(
                    json.load(m),
                    {
                        'projects': {
                            "gameta": {
                                "path": ".",
                                "tags": ["metarepo"],
                                "url": "git@github.com:genius-systems/gameta.git",
                                '__metarepo__': True
                            },
                            "test": {
                                "path": "core/GitPython",
                                "tags": ["a", "b", "c"],
                                "url": "https://github.com/jantman/GitPython.git",
                                '__metarepo__': False
                            },
                            "gitdb": {
                                "path": "core/gitdb",
                                "tags": ["a", "c", "d"],
                                "url": "https://github.com/gitpython-developers/gitdb.git",
                                '__metarepo__': False
                            }
                        }
                    }
                )
            self.assertFalse(exists(join(f, 'GitPython')))
            self.assertTrue(exists(join(f, 'core', 'GitPython')))
            self.assertTrue(all(i in listdir(join(f, 'core', 'GitPython')) for i in ['git', 'doc']))

    @patch('gameta.cli.click.Context.ensure_object')
    def test_repos_update_no_new_path_updated_with_physical_sync(self, mock_ensure_object):
        params = {
            'name': 'GitPython',
            'new_name': 'test',
            'new_path': None,
            'new_url': 'https://github.com/jantman/GitPython.git',
        }
        with self.runner.isolated_filesystem() as f:
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'git.zip'), 'r') as template:
                template.extractall(f)
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'gitpython.zip'), 'r') as template:
                template.extractall(f)
            copyfile(join(dirname(__file__), 'data', '.meta_other_repos'), join(f, '.meta'))
            context = GametaContext()
            context.project_dir = f
            context.load()
            mock_ensure_object.return_value = context
            result = self.runner.invoke(
                self.update,
                [
                    '--name', params['name'],
                    '-e', params['new_name'],
                    '-u', params['new_url']
                ]
            )
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                f'Updating repository GitPython with new details (name: {params["new_name"]}, '
                f'url: {params["new_url"]}, path: {params["new_path"]})\n'
                "Performing a physical sync\n"
                f"Cloning repository from new URL: {params['new_url']}\n"
                "Sync complete\n"
                f'Successfully updated repository {params["new_name"]} with new details\n'
            )
            with open(join(f, '.meta')) as m:
                self.assertEqual(
                    json.load(m),
                    {
                        'projects': {
                            "gameta": {
                                "path": ".",
                                "tags": ["metarepo"],
                                "url": "git@github.com:genius-systems/gameta.git",
                                '__metarepo__': True
                            },
                            "test": {
                                "path": "GitPython",
                                "tags": ["a", "b", "c"],
                                "url": "https://github.com/jantman/GitPython.git",
                                '__metarepo__': False
                            },
                            "gitdb": {
                                "path": "core/gitdb",
                                "tags": ["a", "c", "d"],
                                "url": "https://github.com/gitpython-developers/gitdb.git",
                                '__metarepo__': False
                            }
                        }
                    }
                )
            self.assertTrue(exists(join(f, 'GitPython')))
            self.assertTrue(all(i in listdir(join(f, 'GitPython')) for i in ['git', 'doc']))

    @patch('gameta.cli.click.Context.ensure_object')
    def test_repos_update_no_new_url_updated_with_physical_sync(self, mock_ensure_object):
        params = {
            'name': 'GitPython',
            'new_name': 'test',
            'new_path': 'core/gitpython',
            'new_url': None,
        }
        with self.runner.isolated_filesystem() as f:
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'git.zip'), 'r') as template:
                template.extractall(f)
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'gitpython.zip'), 'r') as template:
                template.extractall(f)
            copyfile(join(dirname(__file__), 'data', '.meta_other_repos'), join(f, '.meta'))
            context = GametaContext()
            context.project_dir = f
            context.load()
            mock_ensure_object.return_value = context
            result = self.runner.invoke(
                self.update,
                [
                    '--name', params['name'],
                    '-e', params['new_name'],
                    '-p', params['new_path']
                ]
            )
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                f'Updating repository GitPython with new details (name: {params["new_name"]}, '
                f'url: {params["new_url"]}, path: {params["new_path"]})\n'
                "Performing a physical sync\n"
                f"Copying repository to new path: {params['new_path']}\n"
                "Sync complete\n"
                f'Successfully updated repository {params["new_name"]} with new details\n'
            )
            with open(join(f, '.meta')) as m:
                self.assertEqual(
                    json.load(m),
                    {
                        'projects': {
                            "gameta": {
                                "path": ".",
                                "tags": ["metarepo"],
                                "url": "git@github.com:genius-systems/gameta.git",
                                '__metarepo__': True
                            },
                            "test": {
                                "path": "core/gitpython",
                                "tags": ["a", "b", "c"],
                                "url": "https://github.com/gitpython-developers/GitPython.git",
                                '__metarepo__': False
                            },
                            "gitdb": {
                                "path": "core/gitdb",
                                "tags": ["a", "c", "d"],
                                "url": "https://github.com/gitpython-developers/gitdb.git",
                                '__metarepo__': False
                            }
                        }
                    }
                )
            self.assertFalse(exists(join(f, 'GitPython')))
            self.assertTrue(exists(join(f, 'core', 'gitpython')))
            self.assertTrue(all(i in listdir(join(f, 'core', 'gitpython')) for i in ['git', 'doc', 'test']))

    @patch('gameta.cli.click.Context.ensure_object')
    def test_repos_update_only_name_change_updated_with_physical_sync(self, mock_ensure_object):
        params = {
            'name': 'GitPython',
            'new_name': 'test',
            'new_path': None,
            'new_url': None,
        }
        with self.runner.isolated_filesystem() as f:
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'git.zip'), 'r') as template:
                template.extractall(f)
            with zipfile.ZipFile(join(dirname(__file__), 'data', 'gitpython.zip'), 'r') as template:
                template.extractall(f)
            copyfile(join(dirname(__file__), 'data', '.meta_other_repos'), join(f, '.meta'))
            context = GametaContext()
            context.project_dir = f
            context.load()
            mock_ensure_object.return_value = context
            result = self.runner.invoke(
                self.update,
                [
                    '--name', params['name'],
                    '-e', params['new_name']
                ]
            )
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                f'Updating repository GitPython with new details (name: {params["new_name"]}, '
                f'url: {params["new_url"]}, path: {params["new_path"]})\n'
                "Performing a physical sync\n"
                "No physical changes\n"
                "Sync complete\n"
                f'Successfully updated repository {params["new_name"]} with new details\n'
            )
            with open(join(f, '.meta')) as m:
                self.assertEqual(
                    json.load(m),
                    {
                        'projects': {
                            "gameta": {
                                "path": ".",
                                "tags": ["metarepo"],
                                "url": "git@github.com:genius-systems/gameta.git",
                                '__metarepo__': True
                            },
                            "test": {
                                "path": "GitPython",
                                "tags": ["a", "b", "c"],
                                "url": "https://github.com/gitpython-developers/GitPython.git",
                                '__metarepo__': False
                            },
                            "gitdb": {
                                "path": "core/gitdb",
                                "tags": ["a", "c", "d"],
                                "url": "https://github.com/gitpython-developers/gitdb.git",
                                '__metarepo__': False
                            }
                        }
                    }
                )
            self.assertTrue(exists(join(f, 'GitPython')))
            self.assertTrue(all(i in listdir(join(f, 'GitPython')) for i in ['git', 'doc', 'test']))

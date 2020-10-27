import json
from os.path import join, dirname
from shutil import copyfile
from unittest import TestCase
from unittest.mock import patch

from click.testing import CliRunner

from gameta import GametaContext
from gameta.params import add, delete


class TestAdd(TestCase):
    def setUp(self) -> None:
        self.runner = CliRunner()
        self.add = add

    @patch('gameta.click.Context.ensure_object')
    def test_add_parameters_missing_key_parameters(self, mock_ensure_object):
        with self.runner.isolated_filesystem() as f:
            copyfile(join(dirname(__file__), 'data', '.meta_other_repos'), join(f, '.meta'))
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
                "Error: Missing option '--parameter' / '-p'.\n"
            )

    @patch('gameta.click.Context.ensure_object')
    def test_add_parameters_skip_user_prompt_default_values(self, mock_ensure_object):
        params = {
            'parameter': 'test'
        }
        with self.runner.isolated_filesystem() as f:
            copyfile(join(dirname(__file__), 'data', '.meta_other_repos'), join(f, '.meta'))
            context = GametaContext()
            context.project_dir = f
            context.load()
            mock_ensure_object.return_value = context
            result = self.runner.invoke(self.add, ['-p', params['parameter'], '-y'])
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                f"Adding parameter {params['parameter']}\n"
                f"Adding {params['parameter']} value None for gameta\n"
                f"Adding {params['parameter']} value None for GitPython\n"
                f"Adding {params['parameter']} value None for gitdb\n"
                f"Successfully added parameter {params['parameter']} to .meta file\n"
            )
            with open(join(f, '.meta'), 'r') as m:
                self.assertEqual(
                    json.load(m),
                    {
                        'projects': {
                            'GitPython': {
                                'path': 'GitPython',
                                'tags': ['a', 'b', 'c'],
                                params['parameter']: None,
                                'url': 'https://github.com/gitpython-developers/GitPython.git'
                            },
                            'gameta': {
                                'path': '.',
                                'tags': ['metarepo'],
                                params['parameter']: None,
                                'url': 'git@github.com:genius-systems/gameta.git'
                            },
                            'gitdb': {
                                'path': 'core/gitdb',
                                'tags': ['a', 'c', 'd'],
                                params['parameter']: None,
                                'url': 'https://github.com/gitpython-developers/gitdb.git'
                            }
                        }
                    }
                )

    @patch('gameta.click.Context.ensure_object')
    def test_add_parameters_skip_user_prompt_user_provided_default_value(self, mock_ensure_object):
        params = {
            'parameter': 'test',
            'value': 'hello_world'
        }
        with self.runner.isolated_filesystem() as f:
            copyfile(join(dirname(__file__), 'data', '.meta_other_repos'), join(f, '.meta'))
            context = GametaContext()
            context.project_dir = f
            context.load()
            mock_ensure_object.return_value = context
            result = self.runner.invoke(self.add, ['-p', params['parameter'], '-y', '-v', params['value']])
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                f"Adding parameter {params['parameter']}\n"
                f"Adding {params['parameter']} value {params['value']} for gameta\n"
                f"Adding {params['parameter']} value {params['value']} for GitPython\n"
                f"Adding {params['parameter']} value {params['value']} for gitdb\n"
                f"Successfully added parameter {params['parameter']} to .meta file\n"
            )
            with open(join(f, '.meta'), 'r') as m:
                self.assertEqual(
                    json.load(m),
                    {
                        'projects': {
                            'GitPython': {
                                'path': 'GitPython',
                                'tags': ['a', 'b', 'c'],
                                params['parameter']: params['value'],
                                'url': 'https://github.com/gitpython-developers/GitPython.git'
                            },
                            'gameta': {
                                'path': '.',
                                'tags': ['metarepo'],
                                params['parameter']: params['value'],
                                'url': 'git@github.com:genius-systems/gameta.git'
                            },
                            'gitdb': {
                                'path': 'core/gitdb',
                                'tags': ['a', 'c', 'd'],
                                params['parameter']: params['value'],
                                'url': 'https://github.com/gitpython-developers/gitdb.git'
                            }
                        }
                    }
                )

    @patch('gameta.click.Context.ensure_object')
    def test_add_parameters_skip_user_prompt_default_type_not_in_choice(self, mock_ensure_object):
        params = {
            'parameter': 'test',
            'type': 'test'
        }
        with self.runner.isolated_filesystem() as f:
            copyfile(join(dirname(__file__), 'data', '.meta_other_repos'), join(f, '.meta'))
            context = GametaContext()
            context.project_dir = f
            context.load()
            mock_ensure_object.return_value = context
            result = self.runner.invoke(self.add, ['-p', params['parameter'], '-y', '-t', params['type']])
            self.assertEqual(result.exit_code, 2)
            self.assertEqual(
                result.output,
                "Usage: add [OPTIONS]\n"
                "Try 'add --help' for help.\n"
                "\n"
                "Error: Invalid value for '--type' / '-t': invalid choice: test. "
                "(choose from int, float, str, bool, dict, list)\n"
            )

    @patch('gameta.click.Context.ensure_object')
    def test_add_parameters_user_prompt_all_value_prompted(self, mock_ensure_object):
        params = {
            'parameter': 'test',
            'value': 'hello_world',
            'user_prompt': ['gameta', 'GitPython', 'gitdb']
        }
        with self.runner.isolated_filesystem() as f:
            copyfile(join(dirname(__file__), 'data', '.meta_other_repos'), join(f, '.meta'))
            context = GametaContext()
            context.project_dir = f
            context.load()
            mock_ensure_object.return_value = context
            result = self.runner.invoke(
                self.add, ['-p', params['parameter'], '-v', params['value']], input='\n'.join(params['user_prompt'])
            )
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                f"Adding parameter {params['parameter']}\n"
                f"Please enter the parameter value for repository gameta or >* to skip [hello_world]: "
                f"{params['user_prompt'][0]}\n"
                f"Adding {params['parameter']} value {params['user_prompt'][0]} for gameta\n"
                f"Please enter the parameter value for repository GitPython or >* to skip [hello_world]: "
                f"{params['user_prompt'][1]}\n"
                f"Adding {params['parameter']} value {params['user_prompt'][1]} for GitPython\n"
                f"Please enter the parameter value for repository gitdb or >* to skip [hello_world]: "
                f"{params['user_prompt'][2]}\n"
                f"Adding {params['parameter']} value {params['user_prompt'][2]} for gitdb\n"
                f"Successfully added parameter {params['parameter']} to .meta file\n"
            )
            with open(join(f, '.meta'), 'r') as m:
                self.assertEqual(
                    json.load(m),
                    {
                        'projects': {
                            'GitPython': {
                                'path': 'GitPython',
                                'tags': ['a', 'b', 'c'],
                                params['parameter']: params['user_prompt'][1],
                                'url': 'https://github.com/gitpython-developers/GitPython.git'
                            },
                            'gameta': {
                                'path': '.',
                                'tags': ['metarepo'],
                                params['parameter']: params['user_prompt'][0],
                                'url': 'git@github.com:genius-systems/gameta.git'
                            },
                            'gitdb': {
                                'path': 'core/gitdb',
                                'tags': ['a', 'c', 'd'],
                                params['parameter']: params['user_prompt'][2],
                                'url': 'https://github.com/gitpython-developers/gitdb.git'
                            }
                        }
                    }
                )

    @patch('gameta.click.Context.ensure_object')
    def test_add_parameters_user_prompt_skipping_with_user_provided_default_value(self, mock_ensure_object):
        params = {
            'parameter': 'test',
            'value': 'hello_world',
            'user_prompt': ['gameta', '>*', 'gitdb']
        }
        with self.runner.isolated_filesystem() as f:
            copyfile(join(dirname(__file__), 'data', '.meta_other_repos'), join(f, '.meta'))
            context = GametaContext()
            context.project_dir = f
            context.load()
            mock_ensure_object.return_value = context
            result = self.runner.invoke(
                self.add, ['-p', params['parameter'], '-v', params['value']], input='\n'.join(params['user_prompt'])
            )
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                f"Adding parameter {params['parameter']}\n"
                f"Please enter the parameter value for repository gameta or >* to skip [hello_world]: "
                f"{params['user_prompt'][0]}\n"
                f"Adding {params['parameter']} value {params['user_prompt'][0]} for gameta\n"
                f"Please enter the parameter value for repository GitPython or >* to skip [hello_world]: "
                f"{params['user_prompt'][1]}\n"
                f"Skip token was entered, defaulting to default value {params['value']}\n"
                f"Adding {params['parameter']} value {params['value']} for GitPython\n"
                f"Please enter the parameter value for repository gitdb or >* to skip [hello_world]: "
                f"{params['user_prompt'][2]}\n"
                f"Adding {params['parameter']} value {params['user_prompt'][2]} for gitdb\n"
                f"Successfully added parameter {params['parameter']} to .meta file\n"
            )
            with open(join(f, '.meta'), 'r') as m:
                self.assertEqual(
                    json.load(m),
                    {
                        'projects': {
                            'GitPython': {
                                'path': 'GitPython',
                                'tags': ['a', 'b', 'c'],
                                params['parameter']: params['value'],
                                'url': 'https://github.com/gitpython-developers/GitPython.git'
                            },
                            'gameta': {
                                'path': '.',
                                'tags': ['metarepo'],
                                params['parameter']: params['user_prompt'][0],
                                'url': 'git@github.com:genius-systems/gameta.git'
                            },
                            'gitdb': {
                                'path': 'core/gitdb',
                                'tags': ['a', 'c', 'd'],
                                params['parameter']: params['user_prompt'][2],
                                'url': 'https://github.com/gitpython-developers/gitdb.git'
                            }
                        }
                    }
                )

    @patch('gameta.click.Context.ensure_object')
    def test_add_parameters_user_prompt_complex_user_input(self, mock_ensure_object):
        params = {
            'parameter': 'test',
            'value': 'hello_world',
            'type': 'dict',
            'user_prompt': [{'a': [1, 2, 3]}, {'a': [4, 5, 6]}, {'a': [1, 6, 7], 'c': [4, 2, 8]}]
        }
        with self.runner.isolated_filesystem() as f:
            copyfile(join(dirname(__file__), 'data', '.meta_other_repos'), join(f, '.meta'))
            context = GametaContext()
            context.project_dir = f
            context.load()
            mock_ensure_object.return_value = context
            result = self.runner.invoke(
                self.add, ['-p', params['parameter'], '-v', params['value'], '--type', params['type']],
                input='\n'.join([json.dumps(p) for p in params['user_prompt']])
            )
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                f"Adding parameter {params['parameter']}\n"
                f"Please enter the parameter value for repository gameta or >* to skip [hello_world]: "
                f"{json.dumps(params['user_prompt'][0])}\n"
                f"Adding {params['parameter']} value {params['user_prompt'][0]} for gameta\n"
                f"Please enter the parameter value for repository GitPython or >* to skip [hello_world]: "
                f"{json.dumps(params['user_prompt'][1])}\n"
                f"Adding {params['parameter']} value {params['user_prompt'][1]} for GitPython\n"
                f"Please enter the parameter value for repository gitdb or >* to skip [hello_world]: "
                f"{json.dumps(params['user_prompt'][2])}\n"
                f"Adding {params['parameter']} value {params['user_prompt'][2]} for gitdb\n"
                f"Successfully added parameter {params['parameter']} to .meta file\n"
            )
            with open(join(f, '.meta'), 'r') as m:
                self.assertEqual(
                    json.load(m),
                    {
                        'projects': {
                            'GitPython': {
                                'path': 'GitPython',
                                'tags': ['a', 'b', 'c'],
                                params['parameter']: params['user_prompt'][1],
                                'url': 'https://github.com/gitpython-developers/GitPython.git'
                            },
                            'gameta': {
                                'path': '.',
                                'tags': ['metarepo'],
                                params['parameter']: params['user_prompt'][0],
                                'url': 'git@github.com:genius-systems/gameta.git'
                            },
                            'gitdb': {
                                'path': 'core/gitdb',
                                'tags': ['a', 'c', 'd'],
                                params['parameter']: params['user_prompt'][2],
                                'url': 'https://github.com/gitpython-developers/gitdb.git'
                            }
                        }
                    }
                )

    @patch('gameta.click.Context.ensure_object')
    def test_add_parameters_user_prompt_user_input_does_not_match_required_type(self, mock_ensure_object):
        params = {
            'parameter': 'test',
            'value': 'hello_world',
            'type': 'dict',
            'user_prompt': [{'a': [1, 2, 3]}, ['a', [4, 5, 6]], {'a': [1, 6, 7], 'c': [4, 2, 8]}]
        }
        with self.runner.isolated_filesystem() as f:
            copyfile(join(dirname(__file__), 'data', '.meta_other_repos'), join(f, '.meta'))
            context = GametaContext()
            context.project_dir = f
            context.load()
            mock_ensure_object.return_value = context
            result = self.runner.invoke(
                self.add, ['-p', params['parameter'], '-v', params['value'], '--type', params['type']],
                input='\n'.join([json.dumps(p) for p in params['user_prompt']])
            )
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                f"Adding parameter {params['parameter']}\n"
                f"Please enter the parameter value for repository gameta or >* to skip [hello_world]: "
                f"{json.dumps(params['user_prompt'][0])}\n"
                f"Adding {params['parameter']} value {params['user_prompt'][0]} for gameta\n"
                f"Please enter the parameter value for repository GitPython or >* to skip [hello_world]: "
                f"{json.dumps(params['user_prompt'][1])}\n"
                f"Value {params['user_prompt'][1]} (type: {type(params['user_prompt'][1])}) entered is not the "
                f"required type {dict}, defaulting to default value {params['value']}\n"
                f"Adding {params['parameter']} value {params['value']} for GitPython\n"
                f"Please enter the parameter value for repository gitdb or >* to skip [hello_world]: "
                f"{json.dumps(params['user_prompt'][2])}\n"
                f"Adding {params['parameter']} value {params['user_prompt'][2]} for gitdb\n"
                f"Successfully added parameter {params['parameter']} to .meta file\n"
            )
            with open(join(f, '.meta'), 'r') as m:
                self.assertEqual(
                    json.load(m),
                    {
                        'projects': {
                            'GitPython': {
                                'path': 'GitPython',
                                'tags': ['a', 'b', 'c'],
                                params['parameter']: params['value'],
                                'url': 'https://github.com/gitpython-developers/GitPython.git'
                            },
                            'gameta': {
                                'path': '.',
                                'tags': ['metarepo'],
                                params['parameter']: params['user_prompt'][0],
                                'url': 'git@github.com:genius-systems/gameta.git'
                            },
                            'gitdb': {
                                'path': 'core/gitdb',
                                'tags': ['a', 'c', 'd'],
                                params['parameter']: params['user_prompt'][2],
                                'url': 'https://github.com/gitpython-developers/gitdb.git'
                            }
                        }
                    }
                )


class TestDelete(TestCase):
    def setUp(self) -> None:
        self.runner = CliRunner()
        self.delete = delete

    @patch('gameta.click.Context.ensure_object')
    def test_add_parameters_missing_key_parameters(self, mock_ensure_object):
        with self.runner.isolated_filesystem() as f:
            copyfile(join(dirname(__file__), 'data', '.meta_other_repos'), join(f, '.meta'))
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
                "Error: Missing option '--parameter' / '-p'.\n"
            )

    @patch('gameta.click.Context.ensure_object')
    def test_delete_parameters_parameter_does_not_exist(self, mock_ensure_object):
        params = {
            'parameter': 'test'
        }
        with self.runner.isolated_filesystem() as f:
            copyfile(join(dirname(__file__), 'data', '.meta_other_repos'), join(f, '.meta'))
            context = GametaContext()
            context.project_dir = f
            context.load()
            mock_ensure_object.return_value = context
            result = self.runner.invoke(self.delete, ['-p', params['parameter']])
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                f"Deleting parameter {params['parameter']}\n"
                f"Successfully deleted parameter {params['parameter']} from .meta file\n"
            )
            with open(join(f, '.meta'), 'r') as m:
                self.assertEqual(
                    json.load(m),
                    {
                        'projects': {
                            'GitPython': {
                                'path': 'GitPython',
                                'tags': ['a', 'b', 'c'],
                                'url': 'https://github.com/gitpython-developers/GitPython.git'
                            },
                            'gameta': {
                                'path': '.',
                                'tags': ['metarepo'],
                                'url': 'git@github.com:genius-systems/gameta.git'
                            },
                            'gitdb': {
                                'path': 'core/gitdb',
                                'tags': ['a', 'c', 'd'],
                                'url': 'https://github.com/gitpython-developers/gitdb.git'
                            }
                        }
                    }
                )

    @patch('gameta.click.Context.ensure_object')
    def test_delete_parameters_all_parameters_deleted(self, mock_ensure_object):
        params = {
            'parameter': 'test'
        }
        with self.runner.isolated_filesystem() as f:
            with open(join(dirname(__file__), 'data', '.meta_other_repos'), 'r') as m1:
                output = json.load(m1)
                with open(join(f, '.meta'), 'w+') as m2:
                    output['projects']['gameta'].update({"test": {'a': [1, 2, 3]}})
                    output['projects']['GitPython'].update({'test': {'a': [4, 5, 6]}})
                    output['projects']['gitdb'].update({'test': {'a': [1, 6, 7], 'c': [4, 2, 8]}})
                    json.dump(output, m2)
            context = GametaContext()
            context.project_dir = f
            context.load()
            mock_ensure_object.return_value = context
            result = self.runner.invoke(self.delete, ['-p', params['parameter']])
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                f"Deleting parameter {params['parameter']}\n"
                f"Successfully deleted parameter {params['parameter']} from .meta file\n"
            )
            with open(join(f, '.meta'), 'r') as m:
                self.assertEqual(
                    json.load(m),
                    {
                        'projects': {
                            'GitPython': {
                                'path': 'GitPython',
                                'tags': ['a', 'b', 'c'],
                                'url': 'https://github.com/gitpython-developers/GitPython.git'
                            },
                            'gameta': {
                                'path': '.',
                                'tags': ['metarepo'],
                                'url': 'git@github.com:genius-systems/gameta.git'
                            },
                            'gitdb': {
                                'path': 'core/gitdb',
                                'tags': ['a', 'c', 'd'],
                                'url': 'https://github.com/gitpython-developers/gitdb.git'
                            }
                        }
                    }
                )

    @patch('gameta.click.Context.ensure_object')
    def test_delete_parameters_partial_parameter_deleted(self, mock_ensure_object):
        params = {
            'parameter': 'test'
        }
        with self.runner.isolated_filesystem() as f:
            with open(join(dirname(__file__), 'data', '.meta_other_repos'), 'r') as m1:
                output = json.load(m1)
                with open(join(f, '.meta'), 'w+') as m2:
                    output['projects']['gameta'].update({"test": {'a': [1, 2, 3]}})
                    output['projects']['gitdb'].update({'test': {'a': [1, 6, 7], 'c': [4, 2, 8]}})
                    json.dump(output, m2)
            context = GametaContext()
            context.project_dir = f
            context.load()
            mock_ensure_object.return_value = context
            result = self.runner.invoke(self.delete, ['-p', params['parameter']])
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                f"Deleting parameter {params['parameter']}\n"
                f"Successfully deleted parameter {params['parameter']} from .meta file\n"
            )
            with open(join(f, '.meta'), 'r') as m:
                self.assertEqual(
                    json.load(m),
                    {
                        'projects': {
                            'GitPython': {
                                'path': 'GitPython',
                                'tags': ['a', 'b', 'c'],
                                'url': 'https://github.com/gitpython-developers/GitPython.git'
                            },
                            'gameta': {
                                'path': '.',
                                'tags': ['metarepo'],
                                'url': 'git@github.com:genius-systems/gameta.git'
                            },
                            'gitdb': {
                                'path': 'core/gitdb',
                                'tags': ['a', 'c', 'd'],
                                'url': 'https://github.com/gitpython-developers/gitdb.git'
                            }
                        }
                    }
                )

    @patch('gameta.click.Context.ensure_object')
    def test_delete_parameters_attempting_to_delete_reserved_parameters(self, mock_ensure_object):
        params = {
            'parameter': 'url'
        }
        with self.runner.isolated_filesystem() as f:
            with open(join(dirname(__file__), 'data', '.meta_other_repos'), 'r') as m1:
                output = json.load(m1)
                with open(join(f, '.meta'), 'w+') as m2:
                    output['projects']['gameta'].update({"test": {'a': [1, 2, 3]}})
                    output['projects']['GitPython'].update({'test': {'a': [4, 5, 6]}})
                    output['projects']['gitdb'].update({'test': {'a': [1, 6, 7], 'c': [4, 2, 8]}})
                    json.dump(output, m2)
            context = GametaContext()
            context.project_dir = f
            context.load()
            mock_ensure_object.return_value = context
            result = self.runner.invoke(self.delete, ['-p', params['parameter']])
            self.assertEqual(result.exit_code, 1)
            self.assertEqual(
                result.output,
                f"Error: Parameter {params['parameter']} is a reserved parameter ['url', 'path', 'tags']\n"
            )
            with open(join(f, '.meta'), 'r') as m:
                self.assertEqual(
                    json.load(m),
                    {
                        'projects': {
                            'GitPython': {
                                'path': 'GitPython',
                                'tags': ['a', 'b', 'c'],
                                'url': 'https://github.com/gitpython-developers/GitPython.git',
                                'test': {'a': [4, 5, 6]}
                            },
                            'gameta': {
                                'path': '.',
                                'tags': ['metarepo'],
                                'url': 'git@github.com:genius-systems/gameta.git',
                                'test': {'a': [1, 2, 3]}
                            },
                            'gitdb': {
                                'path': 'core/gitdb',
                                'tags': ['a', 'c', 'd'],
                                'url': 'https://github.com/gitpython-developers/gitdb.git',
                                'test': {'a': [1, 6, 7], 'c': [4, 2, 8]}
                            }
                        }
                    }
                )

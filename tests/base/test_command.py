from unittest import TestCase

from gameta.base.command import Command, SHELL


class TestCommand(TestCase):
    def setUp(self) -> None:
        self.command = Command

    def test_command_virtualenv_shell_command(self):
        test_inputs = {
            'commands': ['git clone https://github.com/libgit2/libgit2'],
            'venv': 'path/to/venv'
        }
        self.command = Command(
            commands=test_inputs['commands'],
            params={},
            shell=False,
            venv='path/to/venv'
        )
        self.assertEqual(
            self.command.virtualenv(test_inputs['commands']),
            ['. path/to/venv/bin/activate'] + test_inputs['commands']
        )

    def test_command_shell_bash_function(self):
        self.assertEqual(
            self.command.shell([
                "generate_version_info () { echo \"HELLO_WORLD=\\\"$1\\\"\" >> output.env; }; "
                "generate_version_info $(git rev-parse --abbrev-ref HEAD)"
            ]),
            f'{SHELL} -c "generate_version_info () '
            '{ echo \"HELLO_WORLD=\\\"$1\\\"\" >> output.env; }; '
            f'generate_version_info $(git rev-parse --abbrev-ref HEAD)"'
        )

    def test_command_shell_pipe_command(self):
        self.assertEqual(
            self.command.shell([
                'aws ecr get-login-password --region region | '
                'docker login --username AWS --password-stdin aws_account_id.dkr.ecr.region.amazonaws.com'
            ]),
            f'{SHELL} -c "aws ecr get-login-password --region region | '
            f'docker login --username AWS --password-stdin aws_account_id.dkr.ecr.region.amazonaws.com"'
        )

    def test_command_shell_multiple_commands(self):
        self.assertEqual(
            self.command.shell([
                'git clone https://github.com/libgit2/libgit2',
                'git fetch --all --tags --prune',
                'git merge'
            ]),
            f'{SHELL} -c "git clone https://github.com/libgit2/libgit2 && '
            f'git fetch --all --tags --prune && git merge"'
        )

    def test_command_tokenise_valid_command(self):
        self.assertEqual(
            self.command.tokenise('git clone https://github.com/libgit2/libgit2'),
            ['git', 'clone', 'https://github.com/libgit2/libgit2']
        )

    def test_command_tokenise_shell_command(self):
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

    def test_command_tokenise_empty_string(self):
        self.assertEqual(self.command.tokenise(''), [])

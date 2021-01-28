from unittest import TestCase

from gameta.base.command import Command, SHELL


class TestCommand(TestCase):
    def setUp(self) -> None:
        self.command = Command

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

    def test_command_tokenise(self):
        self.assertEqual(
            self.command.tokenise('git clone https://github.com/libgit2/libgit2'),
            ['git', 'clone', 'https://github.com/libgit2/libgit2']
        )

from unittest import TestCase

from gameta.base import Parameter
from gameta.base.errors import CommandError


class TestParameter(TestCase):

    def test_parameter_substitute_parameters_missing(self):
        with self.assertRaisesRegex(CommandError, 'Parameter \$TEST was not provided'):
            Parameter('cp {$TEST} {$DEST}').substitute({})

    def test_parameter_substitute_no_mapping_field(self):
        self.assertEqual(
            Parameter('cp {TEST} {DEST}').substitute(TEST='hello', DEST='world'),
            'cp hello world'
        )

    def test_parameter_substitute_no_substitution(self):
        self.assertEqual(
            Parameter('cp hello world').substitute(TEST='hello', DEST='world'),
            'cp hello world'
        )

    def test_parameter_substitute_standard_parameters(self):
        self.assertEqual(
            Parameter('cp {$TEST} {$DEST}').substitute({'$TEST': 'hello', '$DEST': 'world'}),
            'cp hello world'
        )
        self.assertEqual(
            Parameter('cp {TEST} {DEST}').substitute({'TEST': 'hello', 'DEST': 'world'}),
            'cp hello world'
        )
        self.assertEqual(
            Parameter('cp {test} {dest}').substitute({'test': 'hello', 'dest': 'world'}),
            'cp hello world'
        )

    def test_parameter_substitute_shell_script(self):
        self.assertEqual(
            Parameter('cp {__shell__:echo \'hello\'} {$DEST}').substitute({'$DEST': 'world'}),
            'cp hello world'
        )

    def test_parameter_substitute_or_parameter(self):
        self.assertEqual(
            Parameter('cp {test|$TEST|TEST} {DEST}').substitute({'TEST': 'hello', 'DEST': 'world'}),
            'cp hello world'
        )

    def test_parameter_substitute_or_shell_parameter(self):
        self.assertEqual(
            Parameter('cp {test|__shell__:echo \'hello\'|TEST} {DEST}').substitute({'TEST': 'test', 'DEST': 'world'}),
            'cp hello world'
        )

    def test_parameter_escaped_characters(self):
        self.assertEqual(
            Parameter('export {{"asdf": "hello"}} >> test.json && cp test.json {DEST}').substitute(
                {'DEST': 'world'}
            ),
            """export {"asdf": "hello"} >> test.json && cp test.json world"""
        )

    def test_parameter_invalid_parameter(self):
        with self.assertRaises(CommandError) as c:
            Parameter('cp {*&$&^#} {DEST}').substitute({'TEST': 'hello', 'DEST': 'world'})
        self.assertEqual(str(c.exception), 'Invalid parameter(s): *&$&^#')

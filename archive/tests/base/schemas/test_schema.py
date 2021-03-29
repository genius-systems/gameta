from unittest import TestCase

from gameta.base import to_schema_tuple, to_schema_str


class TestToSchemaTuple(TestCase):
    def setUp(self) -> None:
        self.maxDiff = None
        self.to_schema_tuple = to_schema_tuple

    def test_to_schema_tuple_none(self):
        with self.assertRaises(TypeError):
            self.to_schema_tuple(None)

    def test_to_schema_tuple_empty_string(self):
        with self.assertRaises(AttributeError):
            self.to_schema_tuple('')

    def test_to_schema_tuple_invalid_string(self):
        with self.assertRaises(AttributeError):
            self.to_schema_tuple('121.15.a')

    def test_to_schema_tuple_valid_version(self):
        self.assertEqual((121, 15, 1), self.to_schema_tuple('121.15.1a1'))


class TestToSchemaStr(TestCase):
    def setUp(self) -> None:
        self.maxDiff = None
        self.to_schema_str = to_schema_str
    
    def test_to_schema_str_none(self):
        with self.assertRaises(TypeError):
            self.to_schema_str(None)

    def test_to_schema_str_empty_tuple(self):
        with self.assertRaises(TypeError):
            self.to_schema_str(tuple())

    def test_to_schema_tuple_invalid_tuple(self):
        with self.assertRaises(TypeError):
            self.to_schema_str((1, 2, '3'))

    def test_to_schema_tuple_valid_version(self):
        self.assertEqual('1.3.4', self.to_schema_str((1, 3, 4)))

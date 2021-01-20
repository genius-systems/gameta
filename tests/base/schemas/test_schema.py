from unittest import TestCase

from gameta.base import get_schema_version


class TestGetSchemaVersion(TestCase):
    def setUp(self) -> None:
        self.get_schema_version = get_schema_version

    def test_get_schema_version_none(self):
        with self.assertRaises(TypeError):
            get_schema_version(None)

    def test_get_schema_version_empty_string(self):
        with self.assertRaises(AttributeError):
            get_schema_version('')

    def test_get_schema_version_invalid_string(self):
        with self.assertRaises(AttributeError):
            get_schema_version('121.15.a')

    def test_get_schema_version_valid_version(self):
        self.assertEqual((121, 15, 1), get_schema_version('121.15.1a1'))

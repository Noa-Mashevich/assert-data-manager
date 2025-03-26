import os

from django.test import TestCase

from studio.file_utils import FileUtils
from studio.models import Schema, SchemaManager


class TestSchema(TestCase):
    def test_schemas(self):
        versions = SchemaManager.get_supported_versions()
        for version in versions:
            schema = Schema.objects.create(version)
            self.assertEqual(schema.version, version)
            self.assertIsNotNone(schema.schema_data)

        with self.assertRaises(ValueError):
            Schema.objects.create('x.y.z')

    @staticmethod
    def get_test_dir() -> str:
        filepath = os.path.realpath(__file__)
        return os.path.dirname(filepath)

    @staticmethod
    def get_data_path(file_name: str, sub_dir: str) -> str:
        return FileUtils.join_path(TestSchema.get_test_dir(), 'data', sub_dir, file_name)

    def test_schema_validation(self):
        schema = Schema.objects.create('1.0.0')

        success, error_message = schema.validate({})

        self.assertEqual(success, False)
        self.assertGreater(len(error_message), 0)

        data_file_name = TestSchema.get_data_path('test_schema_v1.0.0.json', 'schema')
        data = FileUtils.read_dict(data_file_name)
        success, error_message = schema.validate(data)

        self.assertEqual(success, False)
        self.assertGreater(len(error_message), 0)

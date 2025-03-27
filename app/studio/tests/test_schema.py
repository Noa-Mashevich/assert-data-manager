from django.test import TestCase

from studio.file_utils import FileUtils
from studio.models import Schema, SchemaManager

from .utils import TestUtils


class TestSchema(TestCase):
    def test_schemas(self):
        versions = SchemaManager.get_supported_versions()
        for version in versions:
            schema = Schema.objects.create_from_version(version)
            self.assertEqual(schema.version, version)
            self.assertIsNotNone(schema.schema_data)

        with self.assertRaises(ValueError):
            Schema.objects.create_from_version('x.y.z')

    def test_schema_validation(self):
        schema = Schema.objects.create_from_version('1.0.0')

        success, error_message = schema.validate({})

        self.assertEqual(success, False)
        self.assertGreater(len(error_message), 0)

        data_file_name = TestUtils.get_data_path('test_schema_v1.0.0_1.json', 'schema')
        data = FileUtils.read_dict(data_file_name)
        success, error_message = schema.validate(data)

        self.assertEqual(success, False)
        self.assertGreater(len(error_message), 0)

        data_file_name = TestUtils.get_data_path('test_schema_v1.0.0_2.json', 'schema')
        data = FileUtils.read_dict(data_file_name)
        success, error_message = schema.validate(data)

        self.assertEqual(success, True)
        self.assertEqual(len(error_message), 0)

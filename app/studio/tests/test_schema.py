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
        schema_data = [
            {
                'version': '1.0.0',
                'files': [
                    {'file_name': 'test_schema_v1.0.0_1.json', 'result': False},
                    {'file_name': 'test_schema_v1.0.0_2.json', 'result': True},
                ],
            },
            {
                'version': '1.0.1',
                'files': [
                    {
                        'file_name': 'test_schema_v1.0.1_09_The_Beckman_Elevation-BB_2025-03-31_08-14.json',  # noqa
                        'result': True,
                    },
                    {
                        'file_name': 'test_schema_v1.0.1_9_Beckman_Dor_Elevation-B_2025-03-23_11-56.json',  # noqa
                        'result': False,
                    },
                ],
            },
        ]

        for data in schema_data:
            version = data.get('version')

            schema = Schema.objects.create_from_version(version)

            success, error_message = schema.validate({})

            self.assertEqual(success, False)
            self.assertGreater(len(error_message), 0)

            files = data.get('files')

            for file in files:
                file_name = file.get('file_name')
                result = file.get('result')

                file_path = TestUtils.get_data_path(file_name, 'schema')
                data = FileUtils.read_dict(file_path)
                success, error_message = schema.validate(data)

                self.assertEqual(success, result)

                if result:
                    self.assertEqual(len(error_message), 0)
                else:
                    self.assertGreater(len(error_message), 0)

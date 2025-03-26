from django.test import TestCase

from studio.models import Schema, SchemaManager


class TestSchema(TestCase):
    def test_valid_schemas(self):
        versions = SchemaManager.get_supported_versions()
        for version in versions:
            schema = Schema.objects.create(version)
            self.assertIsNotNone(schema.schema_data)

    def test_invalid_schema(self):
        with self.assertRaises(ValueError):
            Schema.objects.create('x.y.z')

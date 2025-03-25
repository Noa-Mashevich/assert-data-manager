from django.test import TestCase

from studio.models import Schema


class TestSchema(TestCase):
    def test_schema_creation(self):
        schema = Schema.objects.create('1.0.0')

        self.assertIsNotNone(schema.schema_data)

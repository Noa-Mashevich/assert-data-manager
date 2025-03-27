from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from studio.file_utils import FileUtils

from .utils import TestUtils


class TestValidatorApi(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_validator(self):
        url = reverse('validator-validate')

        response = self.client.post(url, data='', content_type='application/json')

        self.assertEqual(response.status_code, 400)

        response = self.client.post(url, data='{}', content_type='application/json')
        self.assertEqual(response.content, b'Missing version in input data')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content, b'Missing version in input data')

        response = self.client.post(
            url, data='{"version": "1.0.0"}', content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.content[0:86],
            b'Failed validating data, version "1.0.0", reason: \'corePlanName\' is a required property',
        )

        data_file_name = TestUtils.get_data_path('test_schema_v1.0.0_2.json', 'schema')
        data = FileUtils.read_content(data_file_name)
        response = self.client.post(url, data=data, content_type='application/json')

        self.assertEqual(response.status_code, 200)

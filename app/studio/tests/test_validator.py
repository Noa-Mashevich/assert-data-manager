from django.test import TestCase
from rest_framework.test import APIRequestFactory

from studio.views.validator import ValidatorViewSet
from studio.file_utils import FileUtils

from .utils import TestUtils


class TestValidatorApi(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()

    def test_validator(self):
        view = ValidatorViewSet.as_view({'post': 'validate'})

        with self.assertRaises(Exception):
            request = self.factory.post(f'/validator')
            view(request)

        with self.assertRaises(Exception):
            request = self.factory.post(f'/validator', {})
            view(request)

        with self.assertRaises(Exception):
            request = self.factory.post(f'/validator', {'version': '1.0.0'})
            view(request)

        data_file_name = TestUtils.get_data_path('test_schema_v1.0.0_2.json', 'schema')
        data = FileUtils.read_dict(data_file_name)
        request = self.factory.post(f'/validator', data, format='json')
        response = view(request)

        self.assertEqual(response.status_code, 200)

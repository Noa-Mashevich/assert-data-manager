from django.test import TestCase
from rest_framework.test import APIRequestFactory

from studio.views.validator import ValidatorViewSet


class TestValidatorApi(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()

    def test_validator_errors(self):
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

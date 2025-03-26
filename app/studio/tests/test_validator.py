from django.test import TestCase
from rest_framework.test import APIRequestFactory

from studio.views.validator import ValidatorViewSet


class TestValidatorApi(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()

    def test_validator_errors(self):
        view = ValidatorViewSet.as_view({'post': 'validate'})

        request = self.factory.post(f'/validator')
        response = view(request)
        self.assertEqual(response.status_code, 400)

        request = self.factory.post(f'/validator', {})
        response = view(request)
        self.assertEqual(response.status_code, 400)

        request = self.factory.post(f'/validator', {'version': '1.0.0'})
        response = view(request)
        self.assertEqual(response.status_code, 400)

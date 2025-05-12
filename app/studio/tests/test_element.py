import json

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from studio.file_utils import FileUtils
from studio.models import FileNotification
from studio.models.element import Element, ElementCategory

from .utils import TestUtils


def create_file_notification(file_name):
    file_notification_path = TestUtils.get_data_path(
        'file_notification.json', 'file_notification'
    )
    message = FileUtils.read_dict(file_notification_path)
    payload = json.loads(message['Message'])
    payload['Records'][0]['s3']['object']['key'] = file_name
    FileNotification.objects.create_from_queue(json.dumps(payload))


class TestElement(TestCase):
    def test_initialization(self):
        element = Element.objects.create(name='Test name', category=ElementCategory.Door)

        element_data = element.latest_element_data

        self.assertIsNotNone(element_data)
        self.assertEqual(element_data.version, 1)

        self.assertIsNone(element.latest_valid_element_data)

        files = element_data.files

        self.assertEqual(len(files), 4)

        create_file_notification('studio/elements/1/files/1.json')

        element_data = element.latest_valid_element_data

        self.assertIsNotNone(element_data)
        self.assertEqual(element_data.version, 1)

        files = element_data.files

        self.assertEqual(len(files), 4)

    def test_upgrade(self):
        element = Element.objects.create(name='Test name', category=ElementCategory.Door)

        element_data = element.latest_element_data

        self.assertIsNotNone(element_data)
        self.assertEqual(element_data.version, 1)

        self.assertIsNone(element.latest_valid_element_data)

        create_file_notification('studio/elements/1/files/1.json')

        element_data = element.latest_valid_element_data

        self.assertIsNotNone(element_data)
        self.assertEqual(element_data.version, 1)

        previous_element_data = element.previous_element_data

        self.assertIsNone(previous_element_data)

        element.upgrade()

        element_data = element.latest_element_data

        self.assertIsNotNone(element_data)
        self.assertEqual(element_data.version, 2)

        element_data = element.latest_valid_element_data

        self.assertIsNotNone(element_data)
        self.assertEqual(element_data.version, 1)

        create_file_notification('studio/elements/1/files/5.json')

        element_data = element.latest_element_data

        self.assertIsNotNone(element_data)
        self.assertEqual(element_data.version, 2)

        element_data = element.latest_valid_element_data

        self.assertIsNotNone(element_data)
        self.assertEqual(element_data.version, 2)

        previous_element_data = element.previous_element_data

        self.assertIsNotNone(previous_element_data)
        self.assertEqual(previous_element_data.version, 1)


class ElementApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def check_data_for_element(self, data, is_created):
        self.assertIsNotNone(data.get('id'))
        self.assertIsNotNone(data.get('name'))
        self.assertIsNotNone(data.get('category'))

        element_data = data.get('element_data')

        self.assertIsNotNone(element_data)
        self.assertIsNotNone(element_data.get('id'))
        self.assertIsNotNone(element_data.get('version'))
        self.assertIsNotNone(element_data.get('status'))
        self.assertIsNotNone(element_data.get('created_at'))
        self.assertIsNotNone(element_data.get('updated_at'))
        self.assertIsNone(element_data.get('deleted_at'))

        files = element_data.get('files')

        self.assertIsNotNone(files)
        self.assertEqual(len(files), 4)
        for x in files:
            self.assertIsNotNone(x.get('id'))
            self.assertIsNotNone(x.get('type'))
            self.assertIsNotNone(x.get('content_type'))
            self.assertIsNotNone(x.get('status'))
            if is_created:
                self.assertIsNotNone(x.get('upload_url'))
                self.assertIsNone(x.get('download_url'))
            else:
                self.assertIsNone(x.get('upload_url'))
                self.assertIsNotNone(x.get('download_url'))

    def test_create_element(self):
        url = reverse('element-list')

        response = self.client.post(
            url,
            data='{"name": "Test name", "category": 6}',
            content_type='application/json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data = json.loads(response.content)

        self.check_data_for_element(data, True)

    def test_get_elements(self):
        url = reverse('element-list')

        self.client.post(
            url,
            data='{"name": "Test name #1", "category": 6}',
            content_type='application/json',
        )
        self.client.post(
            url,
            data='{"name": "Test name #2", "category": 6}',
            content_type='application/json',
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = json.loads(response.content)
        results = data.get('results')

        self.assertEqual(len(results), 0)

        create_file_notification('studio/elements/1/files/1.json')
        create_file_notification('studio/elements/2/files/5.json')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = json.loads(response.content)
        results = data.get('results')

        self.assertEqual(len(results), 2)
        for result in results:
            self.check_data_for_element(result, False)

    def test_get_specific_element(self):
        url = reverse('element-detail', kwargs={'pk': 1})

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        url = reverse('element-list')

        self.client.post(
            url,
            data='{"name": "Test name #1", "category": 6}',
            content_type='application/json',
        )

        create_file_notification('studio/elements/1/files/1.json')

        url = reverse('element-detail', kwargs={'pk': 1})

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = json.loads(response.content)

        self.check_data_for_element(data, False)

    def test_upgrade_element(self):
        # TODO
        self.assertTrue(True)

    def test_get_element_versions(self):
        url = reverse('element-list')

        self.client.post(
            url,
            data='{"name": "Test name #1", "category": 6}',
            content_type='application/json',
        )

        # TODO: perform a few upgrades.

        url = reverse('element-id-version-list', kwargs={'element_id': '1'})

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = json.loads(response.content)
        results = data.get('results')

        self.assertEqual(len(results), 1)

    def test_get_specific_element_version(self):
        # TODO
        self.assertTrue(True)

    def test_get_element_version_changes(self):
        # TODO
        self.assertTrue(True)

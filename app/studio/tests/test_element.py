import json

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from studio.file_utils import FileUtils
from studio.models import FileNotification
from studio.models.element import Element, ElementCategory
from studio.models.element_data_change_type import ElementDataChangeType

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
        create_file_notification('studio/elements/1/files/2.dxf')
        create_file_notification('studio/elements/1/files/3.rfa')
        create_file_notification('studio/elements/1/files/4.jpg')

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
        create_file_notification('studio/elements/1/files/2.dxf')
        create_file_notification('studio/elements/1/files/3.rfa')
        create_file_notification('studio/elements/1/files/4.jpg')

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
        create_file_notification('studio/elements/1/files/6.dxf')
        create_file_notification('studio/elements/1/files/7.rfa')
        create_file_notification('studio/elements/1/files/8.jpg')

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

        self.check_data_for_element_data(element_data, is_created)

    def check_data_for_element_data(self, data, is_created):
        self.assertIsNotNone(data.get('id'))
        self.assertIsNotNone(data.get('version'))
        self.assertIsNotNone(data.get('status'))
        self.assertIsNotNone(data.get('created_at'))
        self.assertIsNotNone(data.get('updated_at'))
        self.assertIsNone(data.get('deleted_at'))

        files = data.get('files')

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

    def get_paginated(self, url, previous_results=None):
        all_results = previous_results if previous_results else []

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        results = data.get('results', [])
        next_url = data.get('next', None)

        all_results.extend(results)

        if next_url is None:
            return all_results

        return self.get_paginated(next_url, all_results)

    def test_create_element(self):
        url = reverse('element-list')

        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(
            url,
            data='{"name": "Test name"}',
            content_type='application/json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(
            url,
            data='{"category": 6}',
            content_type='application/json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(
            url,
            data='{"name": "Test name", "category": 12211221}',
            content_type='application/json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

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

        results = self.get_paginated(url)

        self.assertEqual(len(results), 0)

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

        results = self.get_paginated(url)

        self.assertEqual(len(results), 0)

        create_file_notification('studio/elements/1/files/1.json')
        create_file_notification('studio/elements/1/files/2.dxf')
        create_file_notification('studio/elements/1/files/3.rfa')
        create_file_notification('studio/elements/1/files/4.jpg')

        results = self.get_paginated(url)

        self.assertEqual(len(results), 1)
        for result in results:
            self.check_data_for_element(result, False)

        create_file_notification('studio/elements/2/files/5.json')
        create_file_notification('studio/elements/2/files/6.dxf')
        create_file_notification('studio/elements/2/files/7.rfa')
        create_file_notification('studio/elements/2/files/8.jpg')

        results = self.get_paginated(url)

        self.assertEqual(len(results), 2)

        for result in results:
            self.check_data_for_element(result, False)

    def test_get_element(self):
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
        create_file_notification('studio/elements/1/files/2.dxf')
        create_file_notification('studio/elements/1/files/3.rfa')
        create_file_notification('studio/elements/1/files/4.jpg')

        url = reverse('element-detail', kwargs={'pk': 1})

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = json.loads(response.content)

        self.check_data_for_element(data, False)

    def test_upgrade_element(self):
        url = reverse('element-list')

        self.client.post(
            url,
            data='{"name": "Test name #1", "category": 6}',
            content_type='application/json',
        )

        url = reverse('element-upgrade', kwargs={'pk': '1'})

        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = json.loads(response.content)

        self.check_data_for_element(data, True)

        self.assertEqual(data.get('element_data').get('version'), 2)

        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = json.loads(response.content)

        self.check_data_for_element(data, True)

        self.assertEqual(data.get('element_data').get('version'), 3)

    def test_get_element_versions(self):
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

        url_1 = reverse('element-upgrade', kwargs={'pk': '1'})
        url_2 = reverse('element-upgrade', kwargs={'pk': '2'})

        self.client.post(url_1)
        self.client.post(url_2)
        self.client.post(url_1)
        self.client.post(url_2)
        self.client.post(url_1)
        self.client.post(url_2)

        for element_id in [1, 2]:
            url = reverse('element-id-version-list', kwargs={'element_id': element_id})

            results = self.get_paginated(url)

            self.assertEqual(len(results), 4)

            for result in results:
                self.check_data_for_element(result, False)

    def test_get_element_version(self):
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

        url = reverse('element-upgrade', kwargs={'pk': '1'})
        url_2 = reverse('element-upgrade', kwargs={'pk': '2'})

        self.client.post(url)
        self.client.post(url_2)
        self.client.post(url)
        self.client.post(url_2)
        self.client.post(url)
        self.client.post(url_2)

        for version in [1, 2, 3, 4]:
            url = reverse(
                'element-id-version-detail', kwargs={'element_id': '1', 'pk': version}
            )

            response = self.client.get(url)

            self.assertEqual(response.status_code, status.HTTP_200_OK)

            data = json.loads(response.content)

            self.check_data_for_element(data, False)

            element_data = data.get('element_data')

            self.assertEqual(element_data.get('version'), version)

    def test_get_element_version_changes(self):
        url = reverse('element-list')

        self.client.post(
            url,
            data='{"name": "WD_Single Hung 3050", "category": 7}',
            content_type='application/json',
        )

        create_file_notification('studio/elements/1/files/1.json')
        create_file_notification('studio/elements/1/files/2.dxf')
        create_file_notification('studio/elements/1/files/3.rfa')
        create_file_notification('studio/elements/1/files/4.jpg')

        url = reverse(
            'element-id-version-id-changes-list',
            kwargs={'element_id': '1', 'version_id': 1},
        )

        results = self.get_paginated(url)

        self.assertEqual(len(results), 33)

        for x in results:
            self.assertEqual(x.get('type'), ElementDataChangeType.Minor)
            self.assertTrue('added property' in x.get('description'))

        url = reverse('element-upgrade', kwargs={'pk': '1'})

        self.client.post(url)

        create_file_notification('studio/elements/1/files/5.json')
        create_file_notification('studio/elements/1/files/6.dxf')
        create_file_notification('studio/elements/1/files/7.rfa')
        create_file_notification('studio/elements/1/files/8.jpg')

        url = reverse(
            'element-id-version-id-changes-list',
            kwargs={'element_id': '1', 'version_id': 2},
        )

        results = self.get_paginated(url)

        self.assertEqual(len(results), 4)

        removed_property = results[0]

        self.assertEqual(removed_property.get('type'), ElementDataChangeType.Major)
        self.assertTrue('removed property' in removed_property.get('description'))

        changed_property_type = results[1]

        self.assertEqual(changed_property_type.get('type'), ElementDataChangeType.Major)
        self.assertTrue(
            'changed type for property' in changed_property_type.get('description')
        )

        added_property = results[2]

        self.assertEqual(added_property.get('type'), ElementDataChangeType.Minor)
        self.assertTrue('added property' in added_property.get('description'))

        changed_property_value = results[3]

        self.assertEqual(changed_property_value.get('type'), ElementDataChangeType.Patch)
        self.assertTrue(
            'changed value for property' in changed_property_value.get('description')
        )

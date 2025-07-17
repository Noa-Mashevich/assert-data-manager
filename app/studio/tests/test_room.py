import json

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from studio.models.data_change_type import DataChangeType
from studio.file_utils import FileUtils
from studio.models import FileNotification
from studio.models.element import (
    Element,
    ElementCategory,
)
from studio.models.room import (
    Room,
    RoomCategory,
)
from studio.models.room_element import RoomElement

from .utils import TestUtils


def create_file_notification(file_name):
    file_notification_path = TestUtils.get_data_path(
        'file_notification.json', 'file_notification'
    )
    message = FileUtils.read_dict(file_notification_path)
    payload = json.loads(message['Message'])
    payload['Records'][0]['s3']['object']['key'] = file_name
    FileNotification.objects.create_from_queue(json.dumps(payload))


class TestRoom(TestCase):
    def create_elements(self):
        Element.objects.create(name='Test name #1', category=ElementCategory.Door)
        create_file_notification('studio/elements/1/files/1.json')
        create_file_notification('studio/elements/1/files/2.dxf')
        create_file_notification('studio/elements/1/files/3.rfa')
        create_file_notification('studio/elements/1/files/4.png')

        Element.objects.create(name='Test name #2', category=ElementCategory.Door)
        create_file_notification('studio/elements/2/files/5.json')
        create_file_notification('studio/elements/2/files/6.dxf')
        create_file_notification('studio/elements/2/files/7.rfa')
        create_file_notification('studio/elements/2/files/8.png')

        Element.objects.create(name='Test name #3', category=ElementCategory.Door)
        create_file_notification('studio/elements/3/files/9.json')
        create_file_notification('studio/elements/3/files/10.dxf')
        create_file_notification('studio/elements/3/files/11.rfa')
        create_file_notification('studio/elements/3/files/12.png')

        Element.objects.create(name='Test name #4', category=ElementCategory.Door)
        create_file_notification('studio/elements/4/files/13.json')
        create_file_notification('studio/elements/4/files/14.dxf')
        create_file_notification('studio/elements/4/files/15.rfa')
        create_file_notification('studio/elements/4/files/16.png')

    def test_initialization(self):
        self.create_elements()

        room = Room.objects.create(
            name='Test name',
            category=RoomCategory.Loft,
            function='Test function',
            type='Test type',
        )

        room_data = room.latest_room_data

        self.assertIsNotNone(room_data)
        self.assertEqual(room_data.version, 1)

        self.assertIsNone(room.latest_valid_room_data)

        files = room_data.files

        self.assertEqual(len(files), 2)

        create_file_notification('studio/rooms/1/files/17.json')
        create_file_notification('studio/rooms/1/files/18.png')

        room_data = room.latest_valid_room_data

        self.assertIsNotNone(room_data)
        self.assertEqual(room_data.version, 1)

        files = room_data.files

        self.assertEqual(len(files), 2)

        room_elements = RoomElement.objects.filter(room_data=room_data)

        self.assertEqual(len(room_elements), 2)

    def test_upgrade(self):
        self.create_elements()

        room = Room.objects.create(
            name='Test name',
            category=RoomCategory.Loft,
            function='Test function',
            type='Test type',
        )

        room_data = room.latest_room_data

        self.assertIsNotNone(room_data)
        self.assertEqual(room_data.version, 1)

        self.assertIsNone(room.latest_valid_room_data)

        create_file_notification('studio/rooms/1/files/17.json')
        create_file_notification('studio/rooms/1/files/18.png')

        room_data = room.latest_valid_room_data

        self.assertIsNotNone(room_data)
        self.assertEqual(room_data.version, 1)

        previous_room_data = room.previous_room_data

        self.assertIsNone(previous_room_data)

        room_elements = RoomElement.objects.filter(room_data=room_data)

        self.assertEqual(len(room_elements), 2)
        self.assertEqual(room_elements[0].id, 1)
        self.assertEqual(room_elements[1].id, 2)

        room.upgrade()

        room_data = room.latest_room_data

        self.assertIsNotNone(room_data)
        self.assertEqual(room_data.version, 2)

        room_data = room.latest_valid_room_data

        self.assertIsNotNone(room_data)
        self.assertEqual(room_data.version, 1)

        create_file_notification('studio/rooms/1/files/23.json')
        create_file_notification('studio/rooms/1/files/24.png')

        room_data = room.latest_room_data

        self.assertIsNotNone(room_data)
        self.assertEqual(room_data.version, 2)

        room_data = room.latest_valid_room_data

        self.assertIsNotNone(room_data)
        self.assertEqual(room_data.version, 2)

        previous_room_data = room.previous_room_data

        self.assertIsNotNone(previous_room_data)
        self.assertEqual(previous_room_data.version, 1)

        room_elements = RoomElement.objects.filter(room_data=room_data)

        self.assertEqual(len(room_elements), 2)
        self.assertEqual(room_elements[0].id, 3)
        self.assertEqual(room_elements[1].id, 4)


class RoomApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def check_data_for_room(self, data):
        self.assertIsNotNone(data.get('id'))
        self.assertIsNotNone(data.get('name'))
        self.assertIsNotNone(data.get('category'))
        self.assertIsNotNone(data.get('function'))
        self.assertIsNotNone(data.get('type'))

        room_data = data.get('room_data')

        self.assertIsNotNone(room_data)

        self.check_data_for_room_data(room_data)

    def check_data_for_room_data(self, data):
        self.assertIsNotNone(data.get('id'))
        self.assertIsNotNone(data.get('version'))
        self.assertIsNotNone(data.get('status'))

        files = data.get('files')

        self.assertIsNotNone(files)
        self.assertEqual(len(files), 2)

        for x in files:
            self.check_data_for_file(x)

        room_elements = data.get('elements')

        self.assertIsNotNone(room_elements)

        for x in room_elements:
            self.check_data_for_room_element(x)

        self.assertIsNotNone(data.get('data'))
        self.assertIsNotNone(data.get('data_hash'))

        self.assertIsNotNone(data.get('created_at'))
        self.assertIsNotNone(data.get('updated_at'))
        self.assertIsNone(data.get('deleted_at'))

    def check_data_for_file(self, data):
        self.assertIsNotNone(data.get('id'))
        self.assertIsNotNone(data.get('type'))
        self.assertIsNotNone(data.get('content_type'))
        self.assertIsNotNone(data.get('status'))
        upload_url = data.get('upload_url')
        download_url = data.get('download_url')
        if upload_url is not None:
            self.assertIsNone(download_url)
        if download_url is not None:
            self.assertIsNone(upload_url)

    def check_data_for_room_element(self, data):
        self.assertIsNotNone(data.get('room_id'))
        self.assertIsNotNone(data.get('room_version'))
        self.assertIsNotNone(data.get('element_id'))
        self.assertIsNotNone(data.get('element_version'))

        files = data.get('files')

        self.assertIsNotNone(files)
        self.assertEqual(len(files), 2)

        for x in files:
            self.check_data_for_file(x)

        self.assertIsNotNone(data.get('data'))
        self.assertIsNotNone(data.get('data_hash'))

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

    def create_elements(self):
        url = reverse('element-list')

        self.client.post(
            url,
            data='{"name": "Test name #1", "category": "door"}',
            content_type='application/json',
        )

        create_file_notification('studio/elements/1/files/1.json')
        create_file_notification('studio/elements/1/files/2.dxf')
        create_file_notification('studio/elements/1/files/3.rfa')
        create_file_notification('studio/elements/1/files/4.png')

        self.client.post(
            url,
            data='{"name": "Test name #2", "category": "door"}',
            content_type='application/json',
        )

        create_file_notification('studio/elements/2/files/5.json')
        create_file_notification('studio/elements/2/files/6.dxf')
        create_file_notification('studio/elements/2/files/7.rfa')
        create_file_notification('studio/elements/2/files/8.png')

        self.client.post(
            url,
            data='{"name": "Test name #3", "category": "door"}',
            content_type='application/json',
        )

        create_file_notification('studio/elements/3/files/9.json')
        create_file_notification('studio/elements/3/files/10.dxf')
        create_file_notification('studio/elements/3/files/11.rfa')
        create_file_notification('studio/elements/3/files/12.png')

        self.client.post(
            url,
            data='{"name": "Test name #4", "category": "door"}',
            content_type='application/json',
        )

        create_file_notification('studio/elements/4/files/13.json')
        create_file_notification('studio/elements/4/files/14.dxf')
        create_file_notification('studio/elements/4/files/15.rfa')
        create_file_notification('studio/elements/4/files/16.png')

    def test_create_room(self):
        url = reverse('room-list')

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
            data='{"category": "closet"}',
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
            data='{"name": "Test name", "category": "closet", "function": "Test function"}',
            content_type='application/json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data = json.loads(response.content)

        self.check_data_for_room(data)

    def test_create_room_elements(self):
        self.create_elements()

        url = reverse('room-list')

        self.client.post(
            url,
            data='{"name": "Test name #1", "category": "kitchen", "function": "Test function #1"}',
            content_type='application/json',
        )

        create_file_notification('studio/rooms/1/files/17.json')
        create_file_notification('studio/rooms/1/files/18.png')

        url = reverse('room-detail', kwargs={'pk': 1})

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = json.loads(response.content)

        self.check_data_for_room(data)

        room_elements = data.get('room_data').get('elements')

        self.assertEqual(len(room_elements), 2)

        roomelement_0 = room_elements[0]
        roomelement_1 = room_elements[1]

        self.assertEqual(roomelement_0.get('room_id'), 1)
        self.assertEqual(roomelement_0.get('room_version'), 1)
        self.assertEqual(roomelement_0.get('element_id'), 1)
        self.assertEqual(roomelement_0.get('element_version'), 1)
        self.assertEqual(roomelement_1.get('room_id'), 1)
        self.assertEqual(roomelement_1.get('room_version'), 1)
        self.assertEqual(roomelement_1.get('element_id'), 2)
        self.assertEqual(roomelement_1.get('element_version'), 1)

        for room_element in room_elements:
            self.assertEqual(room_element.get('data'), {})
            self.assertEqual(
                room_element.get('data_hash'), '99914b932bd37a50b983c5e7c90ae93b'
            )

        for x in room_elements:
            files = x.get('files')

            self.assertEqual(len(files), 2)

            for y in files:
                self.assertIsNone(y.get('download_url'))
                self.assertIsNotNone(y.get('upload_url'))

        create_file_notification('studio/roomelements/1/files/19.json')
        create_file_notification('studio/roomelements/2/files/21.json')

        url = reverse('room-detail', kwargs={'pk': 1})

        response = self.client.get(url)

        data = json.loads(response.content)

        self.check_data_for_room(data)

        room_elements = data.get('room_data').get('elements')

        for room_element in room_elements:
            data = room_element.get('data')
            self.assertIsNotNone(data)
            self.assertGreater(len(data), 0)
            self.assertNotEqual(
                room_element.get('data_hash'), '99914b932bd37a50b983c5e7c90ae93b'
            )

        url = reverse('room-upgrade', kwargs={'pk': '1'})

        self.client.post(url)

        create_file_notification('studio/rooms/1/files/23.json')
        create_file_notification('studio/rooms/1/files/24.png')

        url = reverse('room-detail', kwargs={'pk': 1})

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = json.loads(response.content)

        self.check_data_for_room(data)

        room_elements = data.get('room_data').get('elements')

        self.assertEqual(len(room_elements), 2)

        self.assertEqual(room_elements[0].get('room_id'), 1)
        self.assertEqual(room_elements[0].get('room_version'), 2)
        self.assertEqual(room_elements[0].get('element_id'), 3)
        self.assertEqual(room_elements[0].get('element_version'), 1)
        self.assertEqual(room_elements[1].get('room_id'), 1)
        self.assertEqual(room_elements[1].get('room_version'), 2)
        self.assertEqual(room_elements[1].get('element_id'), 4)
        self.assertEqual(room_elements[1].get('element_version'), 1)

        for x in room_elements:
            files = x.get('files')

            self.assertEqual(len(files), 2)

            for y in files:
                self.assertIsNone(y.get('download_url'))
                self.assertIsNotNone(y.get('upload_url'))

    def test_get_rooms(self):
        url = reverse('room-list')

        results = self.get_paginated(url)

        self.assertEqual(len(results), 0)

        self.client.post(
            url,
            data='{"name": "Test name #1", "category": "kitchen", "function": "Test function #1"}',
            content_type='application/json',
        )
        self.client.post(
            url,
            data='{"name": "Test name #2", "category": "kitchen", "function": "Test function #2"}',
            content_type='application/json',
        )

        results = self.get_paginated(url)

        self.assertEqual(len(results), 0)

        create_file_notification('studio/rooms/1/files/1.json')

        results = self.get_paginated(url)

        self.assertEqual(len(results), 0)

        create_file_notification('studio/rooms/1/files/2.png')

        results = self.get_paginated(url)

        self.assertEqual(len(results), 1)
        for result in results:
            self.check_data_for_room(result)

        create_file_notification('studio/rooms/2/files/3.json')
        create_file_notification('studio/rooms/2/files/4.png')

        results = self.get_paginated(url)

        self.assertEqual(len(results), 2)

        for result in results:
            self.check_data_for_room(result)

    def test_get_room(self):
        url = reverse('room-detail', kwargs={'pk': 1})

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        url = reverse('room-list')

        self.client.post(
            url,
            data='{"name": "Test name #1", "category": "kitchen", "function": "Test function #1"}',
            content_type='application/json',
        )

        create_file_notification('studio/rooms/1/files/1.json')
        create_file_notification('studio/rooms/1/files/2.png')

        url = reverse('room-detail', kwargs={'pk': 1})

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = json.loads(response.content)

        self.check_data_for_room(data)

    def test_upgrade_room(self):
        url = reverse('room-list')

        self.client.post(
            url,
            data='{"name": "Test name #1", "category": "kitchen", "function": "Test function #1"}',
            content_type='application/json',
        )

        url = reverse('room-upgrade', kwargs={'pk': '1'})

        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = json.loads(response.content)

        self.check_data_for_room(data)

        self.assertEqual(data.get('room_data').get('version'), 2)

        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = json.loads(response.content)

        self.check_data_for_room(data)

        self.assertEqual(data.get('room_data').get('version'), 3)

    def test_get_room_versions(self):
        url = reverse('room-list')

        self.client.post(
            url,
            data='{"name": "Test name #1", "category": "kitchen", "function": "Test function #1"}',
            content_type='application/json',
        )
        self.client.post(
            url,
            data='{"name": "Test name #2", "category": "kitchen", "function": "Test function #2"}',
            content_type='application/json',
        )

        url_1 = reverse('room-upgrade', kwargs={'pk': '1'})
        url_2 = reverse('room-upgrade', kwargs={'pk': '2'})

        self.client.post(url_1)
        self.client.post(url_2)
        self.client.post(url_1)
        self.client.post(url_2)
        self.client.post(url_1)
        self.client.post(url_2)

        for room_id in [1, 2]:
            url = reverse('room-id-version-list', kwargs={'room_id': room_id})

            results = self.get_paginated(url)

            self.assertEqual(len(results), 4)

            for result in results:
                self.check_data_for_room(result)

    def test_get_room_version(self):
        url = reverse('room-list')

        self.client.post(
            url,
            data='{"name": "Test name #1", "category": "kitchen", "function": "Test function #1"}',
            content_type='application/json',
        )
        self.client.post(
            url,
            data='{"name": "Test name #2", "category": "kitchen", "function": "Test function #2"}',
            content_type='application/json',
        )

        url = reverse('room-upgrade', kwargs={'pk': '1'})
        url_2 = reverse('room-upgrade', kwargs={'pk': '2'})

        self.client.post(url)
        self.client.post(url_2)
        self.client.post(url)
        self.client.post(url_2)
        self.client.post(url)
        self.client.post(url_2)

        for version in [1, 2, 3, 4]:
            url = reverse(
                'room-id-version-detail', kwargs={'room_id': '1', 'pk': version}
            )

            response = self.client.get(url)

            self.assertEqual(response.status_code, status.HTTP_200_OK)

            data = json.loads(response.content)

            self.check_data_for_room(data)

            room_data = data.get('room_data')

            self.assertEqual(room_data.get('version'), version)

    def test_get_room_version_changes(self):
        self.create_elements()

        url = reverse('room-list')

        self.client.post(
            url,
            data='{"name": "Test name #1", "category": "kitchen", "function": "Test function #1"}',
            content_type='application/json',
        )

        create_file_notification('studio/rooms/1/files/17.json')
        create_file_notification('studio/rooms/1/files/18.png')

        url = reverse(
            'room-id-version-id-changes-list',
            kwargs={'room_id': '1', 'version_id': 1},
        )

        results = self.get_paginated(url)

        self.assertEqual(len(results), 12)

        for x in results:
            self.assertEqual(x.get('type'), DataChangeType.Minor)
            self.assertTrue('added property' in x.get('description'))

        url = reverse('room-upgrade', kwargs={'pk': '1'})

        self.client.post(url)

        url = reverse(
            'room-id-version-id-changes-list',
            kwargs={'room_id': '1', 'version_id': 2},
        )

        results = self.get_paginated(url)

        self.assertEqual(len(results), 0)

        create_file_notification('studio/rooms/1/files/23.json')
        create_file_notification('studio/rooms/1/files/24.png')

        url = reverse(
            'room-id-version-id-changes-list',
            kwargs={'room_id': '1', 'version_id': 2},
        )

        results = self.get_paginated(url)

        self.assertEqual(len(results), 5)

        removed_property = results[0]

        self.assertEqual(removed_property.get('type'), DataChangeType.Major)
        self.assertTrue('removed property' in removed_property.get('description'))

        changed_property_type = results[1]

        self.assertEqual(changed_property_type.get('type'), DataChangeType.Major)
        self.assertTrue(
            'changed type for property' in changed_property_type.get('description')
        )

        changed_elements_property = results[2]

        self.assertEqual(changed_elements_property.get('type'), DataChangeType.Minor)
        self.assertTrue(
            'changed value for property' in changed_elements_property.get('description')
        )

        added_property = results[3]

        self.assertEqual(added_property.get('type'), DataChangeType.Minor)
        self.assertTrue('added property' in added_property.get('description'))

        changed_property_value = results[4]

        self.assertEqual(changed_property_value.get('type'), DataChangeType.Patch)
        self.assertTrue(
            'changed value for property' in changed_property_value.get('description')
        )

    def test_delete_room(self):
        self.create_elements()

        url = reverse('room-list')

        self.client.post(
            url,
            data='{"name": "Test name #1", "category": "kitchen", "function": "Test function #1"}',
            content_type='application/json',
        )

        create_file_notification('studio/rooms/1/files/17.json')
        create_file_notification('studio/rooms/1/files/18.png')

        results = self.get_paginated(url)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].get('room_data').get('version'), 1)

        url = reverse('room-upgrade', kwargs={'pk': '1'})

        self.client.post(url)

        url = reverse('room-list')

        results = self.get_paginated(url)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].get('room_data').get('version'), 1)

        create_file_notification('studio/rooms/1/files/23.json')
        create_file_notification('studio/rooms/1/files/24.png')

        results = self.get_paginated(url)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].get('room_data').get('version'), 2)

        url = reverse('room-detail', kwargs={'pk': 1})

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        url = reverse('room-list')

        results = self.get_paginated(url)

        self.assertEqual(len(results), 0)

        url = reverse('room-detail', kwargs={'pk': 1})

        response = self.client.get(url)

        data = json.loads(response.content)

        self.assertIsNone(data.get('room_data'))

        url = reverse('room-id-version-list', kwargs={'room_id': 1})

        results = self.get_paginated(url)

        self.assertEqual(len(results), 2)

        for x in results:
            self.assertIsNotNone(x.get('room_data').get('deleted_at'))

        for version in [1, 2]:
            url = reverse(
                'room-id-version-detail', kwargs={'room_id': '1', 'pk': version}
            )

            response = self.client.get(url)

            self.assertEqual(response.status_code, status.HTTP_200_OK)

            data = json.loads(response.content)

            self.assertIsNotNone(data.get('room_data').get('deleted_at'))

    def test_delete_room_version(self):
        self.create_elements()

        url = reverse('room-list')

        self.client.post(
            url,
            data='{"name": "Test name #1", "category": "kitchen", "function": "Test function #1"}',
            content_type='application/json',
        )

        create_file_notification('studio/rooms/1/files/17.json')
        create_file_notification('studio/rooms/1/files/18.png')

        self.client.post(
            url,
            data='{"name": "Test name #2", "category": "kitchen", "function": "Test function #2"}',
            content_type='application/json',
        )

        create_file_notification('studio/rooms/2/files/23.json')
        create_file_notification('studio/rooms/2/files/24.png')

        results = self.get_paginated(url)

        self.assertEqual(len(results), 2)

        for x in results:
            self.assertEqual(x.get('room_data').get('version'), 1)

        url_1 = reverse('room-upgrade', kwargs={'pk': '1'})
        url_2 = reverse('room-upgrade', kwargs={'pk': '2'})

        self.client.post(url_1)

        create_file_notification('studio/rooms/1/files/25.json')
        create_file_notification('studio/rooms/1/files/26.png')

        self.client.post(url_2)

        create_file_notification('studio/rooms/2/files/27.json')
        create_file_notification('studio/rooms/2/files/28.png')

        url = reverse('room-list')

        results = self.get_paginated(url)

        self.assertEqual(len(results), 2)

        for x in results:
            self.assertEqual(x.get('room_data').get('version'), 2)

        url = reverse('room-id-version-detail', kwargs={'room_id': '1', 'pk': 2})

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        url = reverse('room-id-version-list', kwargs={'room_id': '1'})

        results = self.get_paginated(url)

        self.assertEqual(results[0].get('room_data').get('version'), 2)
        self.assertIsNotNone(results[0].get('room_data').get('deleted_at'))
        self.assertEqual(results[1].get('room_data').get('version'), 1)
        self.assertIsNone(results[1].get('room_data').get('deleted_at'))

        url = reverse('room-list')

        results = self.get_paginated(url)

        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].get('room_data').get('version'), 1)

        url = reverse('room-id-version-detail', kwargs={'room_id': '1', 'pk': 1})

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        url = reverse('room-id-version-list', kwargs={'room_id': '1'})

        results = self.get_paginated(url)

        self.assertEqual(results[0].get('room_data').get('version'), 2)
        self.assertIsNotNone(results[0].get('room_data').get('deleted_at'))
        self.assertEqual(results[1].get('room_data').get('version'), 1)
        self.assertIsNotNone(results[1].get('room_data').get('deleted_at'))

        url = reverse('room-list')

        results = self.get_paginated(url)

        self.assertEqual(len(results), 1)

        url = reverse('room-detail', kwargs={'pk': 1})

        response = self.client.get(url)

        data = json.loads(response.content)

        self.assertIsNone(data.get('room_data'))

        url = reverse('room-id-version-list', kwargs={'room_id': 1})

        results = self.get_paginated(url)

        self.assertEqual(len(results), 2)

        for x in results:
            self.assertIsNotNone(x.get('room_data').get('deleted_at'))

        for version in [1, 2]:
            url = reverse(
                'room-id-version-detail', kwargs={'room_id': '1', 'pk': version}
            )

            response = self.client.get(url)

            self.assertEqual(response.status_code, status.HTTP_200_OK)

            data = json.loads(response.content)

            self.assertIsNotNone(data.get('room_data').get('deleted_at'))

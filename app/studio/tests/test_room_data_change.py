from django.test import TestCase

from studio.models.data_change_type import DataChangeType
from studio.models.room_data_change import compare_room_data


class TestRoomDataChange(TestCase):
    def test_data_comparison(self):
        json_data_1 = {}
        json_data_2 = {}

        changes = compare_room_data(json_data_1, json_data_2)

        self.assertEqual(len(changes), 0)

        json_data_1 = {
            'a': 12,
            'b': 21,
            'c': {
                'd': 1,
                'e': 2,
            },
            'd': 3,
            'elements': [
                {
                    "room_id": 1,
                    "room_version": 1,
                    "element_id": 1,
                    "element_version": 1,
                },
                {
                    "room_id": 1,
                    "room_version": 1,
                    "element_id": 2,
                    "element_version": 1,
                },
            ],
        }
        json_data_2 = {
            'b': '21',
            'c': {
                'd': 2,
                'e': 2,
            },
            'd': 3,
            'e': 4,
            'elements': [
                {
                    "room_id": 1,
                    "room_version": 1,
                    "element_id": 1,
                    "element_version": 1,
                },
                {
                    "room_id": 1,
                    "room_version": 1,
                    "element_id": 2,
                    "element_version": 1,
                },
            ],
        }

        changes = compare_room_data(json_data_1, json_data_2)

        self.assertEqual(len(changes), 4)
        self.assertEqual(
            len([x for x in changes if x.get('type') == DataChangeType.Major]), 2
        )
        self.assertEqual(
            len([x for x in changes if x.get('type') == DataChangeType.Minor]), 1
        )
        self.assertEqual(
            len([x for x in changes if x.get('type') == DataChangeType.Patch]), 1
        )

        json_data_1 = {
            'a': 12,
            'b': 21,
            'c': {
                'd': 1,
                'e': 2,
            },
            'd': 3,
            'elements': [
                {
                    "room_id": 1,
                    "room_version": 1,
                    "element_id": 1,
                    "element_version": 1,
                },
                {
                    "room_id": 1,
                    "room_version": 1,
                    "element_id": 2,
                    "element_version": 1,
                },
            ],
        }
        json_data_2 = {
            'b': '21',
            'c': {
                'd': 2,
                'e': 2,
            },
            'd': 3,
            'e': 4,
            'elements': [
                {
                    "room_id": 1,
                    "room_version": 1,
                    "element_id": 1,
                    "element_version": 2,
                },
                {
                    "room_id": 1,
                    "room_version": 1,
                    "element_id": 3,
                    "element_version": 1,
                },
            ],
        }

        changes = compare_room_data(json_data_1, json_data_2)

        self.assertEqual(len(changes), 5)
        self.assertEqual(
            len([x for x in changes if x.get('type') == DataChangeType.Major]), 2
        )
        self.assertEqual(
            len([x for x in changes if x.get('type') == DataChangeType.Minor]), 1
        )
        self.assertEqual(
            len([x for x in changes if x.get('type') == DataChangeType.Patch]), 2
        )

from traceback import print_exc
from django.test import TestCase
from django.test.client import json

from studio.models.data_change_type import DataChangeType
from studio.models.room_data_change import compare_room_data

json_data_1 = {
    "room_name": "string",
    "floor_number": 10,
    "area_sqm": 0,
    "ceiling_height": 0,
    "stretch_lines": [
        {
            "max": 0,
            "firstPoint": {"X": 0, "Y": 0, "Z": 0},
            "secondPoint": {"X": 0, "Y": 0, "Z": 0},
            "type": "ReferenceLine",
        }
    ],
    "Outline": [{"X": 0, "Y": 0, "Z": 2}],
    "elements": [
        {
            "id": 0,
            "type": "door",
            "position": {"x": 2, "y": 3},
            "dimensions": {"width": 9000000000, "height": 0},
        }
    ],
    "lighting": {"natural_light": True, "artificial_lights": 0, "dimmer_controls": True},
    "ventilation": {"air_conditioning": True, "heating": True, "air_exchange_rate": 0},
    "technology": {
        "projector": True,
        "video_conferencing": True,
        "sound_system": True,
        "whiteboard": True,
    },
    "building": "string",
    "wing": "string",
    "access_level": "string",
    "maintenance_contact": "string",
    "capacity": 0,
    "booking_system": "string",
    "last_renovation": "2025-08-20",
}


class TestRoomDataChangeValueTracking(TestCase):
    """Test room comparison function"""

    def test_room_string_value_changes(self):
        """Test room string value changes"""

        json_data_2 = json_data_1.copy()
        json_data_2["room_name"] = "new_name"
        changes = compare_room_data(json_data_1, json_data_2)
        self.assertEqual(len(changes), 1)

        change = changes[0]

        if "changed" in change['description']:
            self.assertNotEqual(change['previous_value'], change['new_value'])

        self.assertEqual(change['type'], DataChangeType.Patch)

    def test_room_number_value_changes(self):
        """Test room number value changes"""

        json_data_2 = json_data_1.copy()
        json_data_2["area_sqm"] = 150
        changes = compare_room_data(json_data_1, json_data_2)
        self.assertEqual(len(changes), 1)

        change = changes[0]

        if "changed" in change['description']:
            self.assertNotEqual(change['previous_value'], change['new_value'])

        self.assertEqual(change['type'], DataChangeType.Patch)

    def test_room_value_deleted(self):
        """Test room number value deleted"""

        json_data_2 = json_data_1.copy()
        del json_data_2["floor_number"]
        changes = compare_room_data(json_data_1, json_data_2)
        self.assertEqual(len(changes), 1)

        change = changes[0]

        if "removed" in change['description']:
            self.assertEqual(change['new_value'], None)

        self.assertEqual(change['type'], DataChangeType.Major)

    def test_room_value_added(self):
        """Test room number value added"""

        json_data_2 = json_data_1.copy()
        json_data_2["room_type"] = "string"
        changes = compare_room_data(json_data_1, json_data_2)
        self.assertEqual(len(changes), 1)

        change = changes[0]

        if "added" in change['description']:
            self.assertEqual(change['previous_value'], None)
            self.assertNotEqual(change['new_value'], None)

        self.assertEqual(change['type'], DataChangeType.Minor)


def test_room_boolean_value_changes(self):
    """Test room boolean value changes"""
    json_data_2 = json_data_1.copy()
    json_data_2["lighting"]["natural_light"] = False

    changes = compare_room_data(json_data_1, json_data_2)
    self.assertEqual(len(changes), 1)
    change = changes[0]
    self.assertEqual(change['type'], DataChangeType.Patch)
    self.assertEqual(change['previous_value'], True)
    self.assertEqual(change['new_value'], False)


def test_room_stretch_lines_changes(self):
    """Test room stretch_lines changes (should be Major)"""
    json_data_2 = json_data_1.copy()
    json_data_2["stretch_lines"][0]["max"] = 100

    changes = compare_room_data(json_data_1, json_data_2)
    self.assertEqual(len(changes), 1)
    change = changes[0]
    self.assertEqual(change['type'], DataChangeType.Major)
    self.assertEqual(change['property'], 'stretch_lines')


def test_room_multiple_changes(self):
    """Test multiple property changes in one update"""
    json_data_2 = json_data_1.copy()
    json_data_2["room_name"] = "new_name"
    json_data_2["area_sqm"] = 150
    json_data_2["new_property"] = "new_value"

    changes = compare_room_data(json_data_1, json_data_2)
    self.assertEqual(len(changes), 3)

    # Check that we have one of each type
    change_types = [c['type'] for c in changes]
    self.assertIn(DataChangeType.Patch, change_types)
    self.assertIn(DataChangeType.Minor, change_types)


def test_room_nested_object_changes(self):
    """Test changes in nested objects"""
    json_data_2 = json_data_1.copy()
    json_data_2["lighting"]["artificial_lights"] = 5

    changes = compare_room_data(json_data_1, json_data_2)
    self.assertEqual(len(changes), 1)
    change = changes[0]
    self.assertEqual(change['property'], 'lighting.artificial_lights')
    self.assertEqual(change['previous_value'], 0)
    self.assertEqual(change['new_value'], 5)

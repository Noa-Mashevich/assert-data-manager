from django.test import TestCase

from studio.models.data_change_type import DataChangeType
from studio.models.element_data_change import compare_element_data

# Base test data for element tests
json_data_1 = {
    "element_name": "Test Element",
    "element_type": "door",
    "dimensions": {"width": 100, "height": 200, "depth": 50},
    "properties": {
        "material": "wood",
        "color": "brown",
        "fire_rated": True,
        "acoustic_rating": 45,
    },
    "location": {"x": 10.5, "y": 20.3, "z": 0},
    "metadata": {
        "manufacturer": "ABC Doors",
        "model": "D-100",
        "serial_number": "SN123456",
        "installation_date": "2024-01-15",
    },
    "tags": ["entrance", "main", "accessible"],
    "status": "active",
    "version": 1.0,
}


class TestElementDataChangeValueTracking(TestCase):
    """Test element comparison function"""

    def test_element_string_value_changes(self):
        """Test element string value changes"""

        json_data_2 = json_data_1.copy()
        json_data_2["element_name"] = "Updated Element"
        changes = compare_element_data(json_data_1, json_data_2)
        self.assertEqual(len(changes), 1)

        change = changes[0]

        if "changed" in change['description']:
            self.assertNotEqual(change['previous_value'], change['new_value'])

        self.assertEqual(change['type'], DataChangeType.Patch)

    def test_element_number_value_changes(self):
        """Test element number value changes"""

        json_data_2 = json_data_1.copy()
        json_data_2["dimensions"]["width"] = 150
        changes = compare_element_data(json_data_1, json_data_2)
        self.assertEqual(len(changes), 1)

        change = changes[0]

        if "changed" in change['description']:
            self.assertNotEqual(change['previous_value'], change['new_value'])

        self.assertEqual(change['type'], DataChangeType.Patch)

    def test_element_value_deleted(self):
        """Test element value deleted"""

        json_data_2 = json_data_1.copy()
        del json_data_2["element_type"]
        changes = compare_element_data(json_data_1, json_data_2)
        self.assertEqual(len(changes), 1)

        change = changes[0]

        if "removed" in change['description']:
            self.assertEqual(change['new_value'], None)

        self.assertEqual(change['type'], DataChangeType.Major)

    def test_element_value_added(self):
        """Test element value added"""

        json_data_2 = json_data_1.copy()
        json_data_2["new_property"] = "new_value"
        changes = compare_element_data(json_data_1, json_data_2)
        self.assertEqual(len(changes), 1)

        change = changes[0]

        if "added" in change['description']:
            self.assertEqual(change['previous_value'], None)
            self.assertNotEqual(change['new_value'], None)

        self.assertEqual(change['type'], DataChangeType.Minor)

    def test_element_boolean_value_changes(self):
        """Test element boolean value changes"""
        json_data_2 = json_data_1.copy()
        json_data_2["properties"]["fire_rated"] = False

        changes = compare_element_data(json_data_1, json_data_2)
        self.assertEqual(len(changes), 1)
        change = changes[0]
        self.assertEqual(change['type'], DataChangeType.Patch)
        self.assertEqual(change['previous_value'], True)
        self.assertEqual(change['new_value'], False)

    def test_element_multiple_changes(self):
        """Test multiple property changes in one update"""
        json_data_2 = json_data_1.copy()
        json_data_2["element_name"] = "Updated Element"
        json_data_2["dimensions"]["width"] = 150
        json_data_2["new_property"] = "new_value"

        changes = compare_element_data(json_data_1, json_data_2)
        self.assertEqual(len(changes), 3)

        # Check that we have one of each type
        change_types = [c['type'] for c in changes]
        self.assertIn(DataChangeType.Patch, change_types)
        self.assertIn(DataChangeType.Minor, change_types)

    def test_element_nested_object_changes(self):
        """Test changes in nested objects"""
        json_data_2 = json_data_1.copy()
        json_data_2["properties"]["acoustic_rating"] = 50

        changes = compare_element_data(json_data_1, json_data_2)
        self.assertEqual(len(changes), 1)
        change = changes[0]
        self.assertEqual(change['property'], 'properties.acoustic_rating')
        self.assertEqual(change['previous_value'], 45)
        self.assertEqual(change['new_value'], 50)

    def test_element_array_changes(self):
        """Test changes in array properties"""
        json_data_2 = json_data_1.copy()
        json_data_2["tags"] = ["entrance", "main", "accessible", "fire_exit"]

        changes = compare_element_data(json_data_1, json_data_2)
        self.assertEqual(len(changes), 1)
        change = changes[0]
        self.assertEqual(change['property'], 'tags')
        self.assertNotEqual(change['previous_value'], change['new_value'])

    def test_element_type_changes(self):
        """Test type changes (should be Major)"""
        json_data_2 = json_data_1.copy()
        json_data_2["properties"]["acoustic_rating"] = "high"

        changes = compare_element_data(json_data_1, json_data_2)
        self.assertEqual(len(changes), 1)
        change = changes[0]
        self.assertEqual(change['type'], DataChangeType.Major)
        self.assertEqual(change['property'], 'properties.acoustic_rating')

    def test_element_float_value_changes(self):
        """Test float value changes"""
        json_data_2 = json_data_1.copy()
        json_data_2["location"]["x"] = 15.7

        changes = compare_element_data(json_data_1, json_data_2)
        self.assertEqual(len(changes), 1)
        change = changes[0]
        self.assertEqual(change['type'], DataChangeType.Patch)
        self.assertEqual(change['previous_value'], 10.5)
        self.assertEqual(change['new_value'], 15.7)

    def test_element_complex_nested_changes(self):
        """Test changes in deeply nested objects"""
        json_data_2 = json_data_1.copy()
        json_data_2["metadata"]["manufacturer"] = "XYZ Doors"

        changes = compare_element_data(json_data_1, json_data_2)
        self.assertEqual(len(changes), 1)
        change = changes[0]
        self.assertEqual(change['property'], 'metadata.manufacturer')
        self.assertEqual(change['previous_value'], "ABC Doors")
        self.assertEqual(change['new_value'], "XYZ Doors")

    def test_element_multiple_nested_changes(self):
        """Test multiple changes in nested objects"""
        json_data_2 = json_data_1.copy()
        json_data_2["dimensions"]["width"] = 150
        json_data_2["dimensions"]["height"] = 250
        json_data_2["properties"]["color"] = "white"

        changes = compare_element_data(json_data_1, json_data_2)
        self.assertEqual(len(changes), 3)

        # All should be Patch changes
        for change in changes:
            self.assertEqual(change['type'], DataChangeType.Patch)

    def test_element_empty_data_comparison(self):
        """Test comparison with empty data"""
        empty_data = {}

        changes = compare_element_data(json_data_1, empty_data)
        # Should detect all properties as removed
        self.assertGreater(len(changes), 0)

        changes = compare_element_data(empty_data, json_data_1)
        # Should detect all properties as added
        self.assertGreater(len(changes), 0)

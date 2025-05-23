from django.test import TestCase

from studio.models.data_change_type import DataChangeType
from studio.models.room_data_change import compare_room_data


class TestRoomDataChange(TestCase):
    def test_data_comparison_for_basic_properties(self):
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
        }
        json_data_2 = {
            'b': '21',
            'c': {
                'd': 2,
                'e': 2,
            },
            'd': 3,
            'e': 4,
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

    def test_data_comparison_for_room_size(self):
        json_data_1 = {
            'Outline': [
                {'Z': 0.12, 'X': 1.2, 'Y': 12.1},
                {'Z': 0.13, 'X': 1.3, 'Y': 13.1},
            ],
        }
        json_data_2 = {
            'Outline': [
                {'Z': 0.12, 'X': 1.2, 'Y': 12.1},
                {'Z': 0.13, 'X': 1.3, 'Y': 13.1},
            ],
        }

        changes = compare_room_data(json_data_1, json_data_2)

        self.assertEqual(len(changes), 0)

        json_data_1 = {
            'Outline': [
                {'Z': 0.1200000001, 'X': 1.2, 'Y': 12.1},
                {'Z': 0.13, 'X': 1.3, 'Y': 13.1},
            ],
        }
        json_data_2 = {
            'Outline': [
                {'Z': 0.12, 'X': 1.2, 'Y': 12.1},
                {'Z': 0.13, 'X': 1.3, 'Y': 13.1},
            ],
        }

        changes = compare_room_data(json_data_1, json_data_2)

        self.assertEqual(len(changes), 1)
        self.assertEqual(
            len([x for x in changes if x.get('type') == DataChangeType.Major]), 1
        )

        json_data_1 = {
            'Outline': [
                {'Z': 0.12, 'X': 1.2, 'Y': 12.1},
                {'Z': 0.13, 'X': 1.3, 'Y': 13.1},
            ],
        }
        json_data_2 = {
            'Outline': [
                {'Z': 0.12, 'X': 1.2, 'Y': 12.1},
                {'Z': 0.13, 'X': 1.3, 'Y': 13.1},
                {'Z': 0.14, 'X': 1.4, 'Y': 14.1},
            ],
        }

        changes = compare_room_data(json_data_1, json_data_2)

        self.assertEqual(len(changes), 1)
        self.assertEqual(
            len([x for x in changes if x.get('type') == DataChangeType.Major]), 1
        )

    def test_data_comparison_for_stretch_lines(self):
        json_data_1 = {
            'stretch_lines': [
                {
                    'max': 359.99999999999994,
                    'firstPoint': {
                        'Z': -155.99999999999997,
                        'Y': -2857.6498660945035,
                        'X': -7681.624315085905,
                    },
                    'secondPoint': {
                        'Z': -155.99999999999997,
                        'Y': -2857.649866094506,
                        'X': -7746.124315085905,
                    },
                    'type': 'ReferenceLine',
                },
                {
                    'max': 359.99999999999994,
                    'firstPoint': {
                        'Z': -155.99999999999997,
                        'Y': -2857.6498660945035,
                        'X': -7681.624315085905,
                    },
                    'secondPoint': {
                        'Z': -155.99999999999997,
                        'Y': -2857.649866094506,
                        'X': -7746.124315085905,
                    },
                    'type': 'ReferenceLine',
                },
            ],
        }
        json_data_2 = {
            'stretch_lines': [
                {
                    'max': 359.99999999999994,
                    'firstPoint': {
                        'Z': -155.99999999999997,
                        'Y': -2857.6498660945035,
                        'X': -7681.624315085905,
                    },
                    'secondPoint': {
                        'Z': -155.99999999999997,
                        'Y': -2857.649866094506,
                        'X': -7746.124315085905,
                    },
                    'type': 'ReferenceLine',
                },
                {
                    'max': 359.99999999999994,
                    'firstPoint': {
                        'Z': -155.99999999999997,
                        'Y': -2857.6498660945035,
                        'X': -7681.624315085905,
                    },
                    'secondPoint': {
                        'Z': -155.99999999999997,
                        'Y': -2857.649866094506,
                        'X': -7746.124315085905,
                    },
                    'type': 'ReferenceLine',
                },
            ],
        }

        changes = compare_room_data(json_data_1, json_data_2)

        self.assertEqual(len(changes), 0)

        json_data_1 = {
            'stretch_lines': [
                {
                    'max': 359.9999999999996,
                    'firstPoint': {
                        'Z': -155.99999999999997,
                        'Y': -2857.6498660945035,
                        'X': -7681.624315085905,
                    },
                    'secondPoint': {
                        'Z': -155.99999999999997,
                        'Y': -2857.649866094506,
                        'X': -7746.124315085905,
                    },
                    'type': 'ReferenceLine',
                },
                {
                    'max': 359.99999999999994,
                    'firstPoint': {
                        'Z': -155.99999999999997,
                        'Y': -2857.6498660945035,
                        'X': -7681.624315085905,
                    },
                    'secondPoint': {
                        'Z': -155.99999999999997,
                        'Y': -2857.649866094506,
                        'X': -7746.124315085905,
                    },
                    'type': 'ReferenceLine',
                },
            ],
        }
        json_data_2 = {
            'stretch_lines': [
                {
                    'max': 359.99999999999994,
                    'firstPoint': {
                        'Z': -155.99999999999997,
                        'Y': -2857.6498660945035,
                        'X': -7681.624315085905,
                    },
                    'secondPoint': {
                        'Z': -155.99999999999997,
                        'Y': -2857.649866094506,
                        'X': -7746.124315085905,
                    },
                    'type': 'ReferenceLine',
                },
                {
                    'max': 359.99999999999994,
                    'firstPoint': {
                        'Z': -155.99999999999997,
                        'Y': -2857.6498660945035,
                        'X': -7681.624315085905,
                    },
                    'secondPoint': {
                        'Z': -155.99999999999997,
                        'Y': -2857.649866094506,
                        'X': -7746.124315085905,
                    },
                    'type': 'ReferenceLine',
                },
            ],
        }

        changes = compare_room_data(json_data_1, json_data_2)

        self.assertEqual(len(changes), 1)
        self.assertEqual(
            len([x for x in changes if x.get('type') == DataChangeType.Major]), 1
        )

        json_data_1 = {
            'stretch_lines': [
                {
                    'max': 359.99999999999994,
                    'firstPoint': {
                        'Z': -155.99999999999997,
                        'Y': -2857.6498660945035,
                        'X': -7681.624315085905,
                    },
                    'secondPoint': {
                        'Z': -155.99999999999997,
                        'Y': -2857.649866094506,
                        'X': -7746.124315085905,
                    },
                    'type': 'ReferenceLine',
                },
                {
                    'max': 359.99999999999994,
                    'firstPoint': {
                        'Z': -155.99999999999997,
                        'Y': -2857.6498660945035,
                        'X': -7681.624315085905,
                    },
                    'secondPoint': {
                        'Z': -155.99999999999997,
                        'Y': -2857.649866094506,
                        'X': -7746.124315085905,
                    },
                    'type': 'ReferenceLine',
                },
            ],
        }
        json_data_2 = {
            'stretch_lines': [
                {
                    'max': 359.99999999999994,
                    'firstPoint': {
                        'Z': -155.99999999999997,
                        'Y': -2857.6498660945035,
                        'X': -7681.624315085905,
                    },
                    'secondPoint': {
                        'Z': -155.99999999999997,
                        'Y': -2857.649866094506,
                        'X': -7746.124315085905,
                    },
                    'type': 'ReferenceLine',
                },
                {
                    'max': 359.99999999999994,
                    'firstPoint': {
                        'Z': -155.99999999999997,
                        'Y': -2857.6498660945035,
                        'X': -7681.624315085905,
                    },
                    'secondPoint': {
                        'Z': -155.99999999999997,
                        'Y': -2857.649866094506,
                        'X': -7746.124315085905,
                    },
                    'type': 'ReferenceLine',
                },
                {
                    'max': 359.99999999999994,
                    'firstPoint': {
                        'Z': -155.99999999999997,
                        'Y': -2857.6498660945035,
                        'X': -7681.624315085905,
                    },
                    'secondPoint': {
                        'Z': -155.99999999999997,
                        'Y': -2857.649866094506,
                        'X': -7746.124315085905,
                    },
                    'type': 'ReferenceLine',
                },
            ],
        }

        changes = compare_room_data(json_data_1, json_data_2)

        self.assertEqual(len(changes), 1)
        self.assertEqual(
            len([x for x in changes if x.get('type') == DataChangeType.Major]), 1
        )

    def test_data_comparison_for_elements(self):
        json_data_1 = {
            'elements': [
                {
                    'element_id': 1,
                    'element_version': 1,
                },
                {
                    'element_id': 2,
                    'element_version': 1,
                },
            ],
        }
        json_data_2 = {
            'elements': [
                {
                    'element_id': 1,
                    'element_version': 1,
                },
                {
                    'element_id': 2,
                    'element_version': 1,
                },
            ],
        }

        changes = compare_room_data(json_data_1, json_data_2)

        self.assertEqual(len(changes), 0)

        json_data_1 = {
            'elements': [
                {
                    'element_id': 1,
                    'element_version': 1,
                },
                {
                    'element_id': 2,
                    'element_version': 1,
                },
            ],
        }
        json_data_2 = {
            'elements': [
                {
                    'element_id': 1,
                    'element_version': 1,
                },
                {
                    'element_id': 3,
                    'element_version': 1,
                },
            ],
        }

        changes = compare_room_data(json_data_1, json_data_2)

        self.assertEqual(len(changes), 1)
        self.assertEqual(
            len([x for x in changes if x.get('type') == DataChangeType.Minor]), 1
        )

        json_data_1 = {
            'elements': [
                {
                    'element_id': 1,
                    'element_version': 1,
                },
                {
                    'element_id': 2,
                    'element_version': 1,
                },
            ],
        }
        json_data_2 = {
            'elements': [
                {
                    'element_id': 1,
                    'element_version': 1,
                },
                {
                    'element_id': 2,
                    'element_version': 1,
                },
                {
                    'element_id': 3,
                    'element_version': 1,
                },
            ],
        }

        changes = compare_room_data(json_data_1, json_data_2)

        self.assertEqual(len(changes), 1)
        self.assertEqual(
            len([x for x in changes if x.get('type') == DataChangeType.Minor]), 1
        )

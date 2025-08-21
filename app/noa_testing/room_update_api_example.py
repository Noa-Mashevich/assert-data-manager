#!/usr/bin/env python
"""
ROOM UPDATE API ENDPOINT - REAL-WORLD EXAMPLES

This example shows how to use the room update API endpoint with realistic
room data structures from actual tests, including stretch lines, outlines,
and other room properties.
"""

import json
import requests


def test_room_update_api():
    """Test the room update API endpoint with realistic data"""

    base_url = "http://localhost:8000"
    room_id = 1

    # EXAMPLE 1: Initial Room Creation (First Version)
    print("🏢 EXAMPLE 1: INITIAL ROOM CREATION")
    print("=" * 80)

    initial_room_data = {
        "data": {
            "room_name": "Conference Room A",
            "room_type": "conference",
            "floor_number": 2,
            "area_sqm": 45.5,
            "ceiling_height": 2.8,
            "stretch_lines": [
                {
                    "max": 359.99999999999994,
                    "firstPoint": {
                        "Z": -155.99999999999997,
                        "Y": -2857.6498660945035,
                        "X": -7681.624315085905,
                    },
                    "secondPoint": {
                        "Z": -155.99999999999997,
                        "Y": -2857.649866094506,
                        "X": -7746.124315085905,
                    },
                    "type": "ReferenceLine",
                },
                {
                    "max": 359.99999999999994,
                    "firstPoint": {
                        "Z": -155.99999999999997,
                        "Y": -2857.6498660945035,
                        "X": -7681.624315085905,
                    },
                    "secondPoint": {
                        "Z": -155.99999999999997,
                        "Y": -2857.649866094506,
                        "X": -7746.124315085905,
                    },
                    "type": "ReferenceLine",
                },
            ],
            "Outline": [
                {"Z": 0.12, "X": 1.2, "Y": 12.1},
                {"Z": 0.13, "X": 1.3, "Y": 13.1},
                {"Z": 0.14, "X": 1.4, "Y": 14.1},
                {"Z": 0.15, "X": 1.5, "Y": 15.1},
            ],
            "elements": [
                {
                    "id": 1,
                    "type": "door",
                    "position": {"x": 0, "y": 2.5},
                    "dimensions": {"width": 0.9, "height": 2.1},
                },
                {
                    "id": 2,
                    "type": "window",
                    "position": {"x": 2, "y": 0},
                    "dimensions": {"width": 1.2, "height": 1.5},
                },
            ],
            "lighting": {
                "natural_light": True,
                "artificial_lights": 4,
                "dimmer_controls": True,
            },
            "ventilation": {
                "air_conditioning": True,
                "heating": True,
                "air_exchange_rate": 2.5,
            },
        },
        "additional_info": {
            "building": "Main Building",
            "wing": "East Wing",
            "access_level": "Level 2",
            "maintenance_contact": "facilities@company.com",
        },
    }

    print("Initial room data structure:")
    print(json.dumps(initial_room_data, indent=2))

    # EXAMPLE 2: Room Update - Adding Technology and Changing Layout
    print("\n\n🏢 EXAMPLE 2: ROOM UPDATE - ADDING TECHNOLOGY")
    print("=" * 80)

    updated_room_data = {
        "data": {
            "room_name": "Conference Room A",
            "room_type": "conference",
            "floor_number": 2,
            "area_sqm": 45.5,
            "ceiling_height": 2.8,
            "stretch_lines": [
                {
                    "max": 359.99999999999994,
                    "firstPoint": {
                        "Z": -155.99999999999997,
                        "Y": -2857.6498660945035,
                        "X": -7681.624315085905,
                    },
                    "secondPoint": {
                        "Z": -155.99999999999997,
                        "Y": -2857.649866094506,
                        "X": -7746.124315085905,
                    },
                    "type": "ReferenceLine",
                },
                {
                    "max": 359.99999999999994,
                    "firstPoint": {
                        "Z": -155.99999999999997,
                        "Y": -2857.6498660945035,
                        "X": -7681.624315085905,
                    },
                    "secondPoint": {
                        "Z": -155.99999999999997,
                        "Y": -2857.649866094506,
                        "X": -7746.124315085905,
                    },
                    "type": "ReferenceLine",
                },
                # Added new stretch line
                {
                    "max": 359.99999999999994,
                    "firstPoint": {
                        "Z": -155.99999999999997,
                        "Y": -2857.6498660945035,
                        "X": -7746.124315085905,
                    },
                    "secondPoint": {
                        "Z": -155.99999999999997,
                        "Y": -2857.649866094506,
                        "X": -7810.624315085905,
                    },
                    "type": "ReferenceLine",
                },
            ],
            "Outline": [
                {"Z": 0.12, "X": 1.2, "Y": 12.1},
                {"Z": 0.13, "X": 1.3, "Y": 13.1},
                {"Z": 0.14, "X": 1.4, "Y": 14.1},
                {"Z": 0.15, "X": 1.5, "Y": 15.1},
                {"Z": 0.16, "X": 1.6, "Y": 16.1},  # Added new point
            ],
            "elements": [
                {
                    "id": 1,
                    "type": "door",
                    "position": {"x": 0, "y": 2.5},
                    "dimensions": {"width": 0.9, "height": 2.1},
                },
                {
                    "id": 2,
                    "type": "window",
                    "position": {"x": 2, "y": 0},
                    "dimensions": {"width": 1.2, "height": 1.5},
                },
                # Added new elements
                {
                    "id": 3,
                    "type": "projector_screen",
                    "position": {"x": 7, "y": 2.5},
                    "dimensions": {"width": 2.4, "height": 1.8},
                },
                {
                    "id": 4,
                    "type": "speaker",
                    "position": {"x": 4, "y": 0.5},
                    "dimensions": {"width": 0.3, "height": 0.3},
                },
                {
                    "id": 5,
                    "type": "speaker",
                    "position": {"x": 4, "y": 4.5},
                    "dimensions": {"width": 0.3, "height": 0.3},
                },
            ],
            "lighting": {
                "natural_light": True,
                "artificial_lights": 6,  # Increased from 4
                "dimmer_controls": True,
                "motion_sensors": True,  # Added
            },
            "ventilation": {
                "air_conditioning": True,
                "heating": True,
                "air_exchange_rate": 3.0,  # Increased from 2.5
            },
            "technology": {  # New property
                "projector": True,
                "video_conferencing": True,
                "sound_system": True,
                "whiteboard": True,
                "smart_board": False,
            },
        },
        "additional_info": {
            "building": "Main Building",
            "wing": "East Wing",
            "access_level": "Level 2",
            "maintenance_contact": "facilities@company.com",
            "capacity": 12,  # Added
            "booking_system": "Outlook",  # Added
            "last_renovation": "2024-01-15",  # Added
        },
    }

    print("Updated room data structure:")
    print(json.dumps(updated_room_data, indent=2))

    # EXAMPLE 3: Major Renovation - Changing Room Structure
    print("\n\n🏢 EXAMPLE 3: MAJOR RENOVATION - STRUCTURAL CHANGES")
    print("=" * 80)

    renovation_data = {
        "data": {
            "room_name": "Conference Room A",
            "room_type": "conference",
            "floor_number": 2,
            "area_sqm": 60.0,  # Increased area
            "ceiling_height": 3.2,  # Increased height
            "stretch_lines": [
                {
                    "max": 359.99999999999994,
                    "firstPoint": {
                        "Z": -155.99999999999997,
                        "Y": -2857.6498660945035,
                        "X": -7681.624315085905,
                    },
                    "secondPoint": {
                        "Z": -155.99999999999997,
                        "Y": -2857.649866094506,
                        "X": -7846.124315085905,  # Extended
                    },
                    "type": "ReferenceLine",
                },
                {
                    "max": 359.99999999999994,
                    "firstPoint": {
                        "Z": -155.99999999999997,
                        "Y": -2857.6498660945035,
                        "X": -7846.124315085905,
                    },
                    "secondPoint": {
                        "Z": -155.99999999999997,
                        "Y": -2857.649866094506,
                        "X": -8010.624315085905,  # Extended
                    },
                    "type": "ReferenceLine",
                },
            ],
            "Outline": [
                {"Z": 0.12, "X": 1.2, "Y": 12.1},
                {"Z": 0.13, "X": 1.3, "Y": 13.1},
                {"Z": 0.14, "X": 1.4, "Y": 14.1},
                {"Z": 0.15, "X": 1.5, "Y": 15.1},
                {"Z": 0.16, "X": 1.6, "Y": 16.1},
                {"Z": 0.17, "X": 1.7, "Y": 17.1},  # Added
                {"Z": 0.18, "X": 1.8, "Y": 18.1},  # Added
            ],
            "elements": [
                {
                    "id": 1,
                    "type": "door",
                    "position": {"x": 0, "y": 3.0},  # Moved
                    "dimensions": {"width": 1.2, "height": 2.4},  # Larger door
                },
                {
                    "id": 2,
                    "type": "window",
                    "position": {"x": 3, "y": 0},  # Moved
                    "dimensions": {"width": 1.8, "height": 1.8},  # Larger window
                },
                {
                    "id": 3,
                    "type": "projector_screen",
                    "position": {"x": 9, "y": 3.0},  # Moved
                    "dimensions": {"width": 3.0, "height": 2.0},  # Larger screen
                },
                {
                    "id": 4,
                    "type": "speaker",
                    "position": {"x": 5, "y": 0.5},
                    "dimensions": {"width": 0.3, "height": 0.3},
                },
                {
                    "id": 5,
                    "type": "speaker",
                    "position": {"x": 5, "y": 5.5},  # Moved
                    "dimensions": {"width": 0.3, "height": 0.3},
                },
                {
                    "id": 6,
                    "type": "acoustic_panel",  # New element type
                    "position": {"x": 2, "y": 1},
                    "dimensions": {"width": 1.0, "height": 2.0},
                },
            ],
            "lighting": {
                "natural_light": True,
                "artificial_lights": 8,  # Increased
                "dimmer_controls": True,
                "motion_sensors": True,
                "led_lighting": True,  # Added
            },
            "ventilation": {
                "air_conditioning": True,
                "heating": True,
                "air_exchange_rate": 4.0,  # Increased
                "hvac_zones": 2,  # Added
            },
            "technology": {
                "projector": True,
                "video_conferencing": True,
                "sound_system": True,
                "whiteboard": True,
                "smart_board": True,  # Changed from False
                "wireless_presentation": True,  # Added
            },
            "acoustics": {  # New property
                "sound_absorption": "high",
                "noise_reduction": "medium",
                "reverberation_time": 0.6,
            },
        },
        "additional_info": {
            "building": "Main Building",
            "wing": "East Wing",
            "access_level": "Level 2",
            "maintenance_contact": "facilities@company.com",
            "capacity": 18,  # Increased
            "booking_system": "Outlook",
            "last_renovation": "2024-03-15",  # Updated
            "renovation_cost": 25000,  # Added
            "energy_rating": "A+",  # Added
        },
    }

    print("Renovation data structure:")
    print(json.dumps(renovation_data, indent=2))

    # API CALL EXAMPLES
    print("\n\n🚀 API CALL EXAMPLES")
    print("=" * 80)

    # Example API calls (commented out for safety)
    print(
        """
    # Example 1: Create initial room
    response = requests.post(
        f"{base_url}/studio/room/{room_id}/upgrade_with_data/",
        json=initial_room_data,
        headers={'Content-Type': 'application/json'}
    )

    # Example 2: Update room with technology
    response = requests.post(
        f"{base_url}/studio/room/{room_id}/upgrade_with_data/",
        json=updated_room_data,
        headers={'Content-Type': 'application/json'}
    )

    # Example 3: Major renovation
    response = requests.post(
        f"{base_url}/studio/room/{room_id}/upgrade_with_data/",
        json=renovation_data,
        headers={'Content-Type': 'application/json'}
    )
    """
    )

    print("\n📊 EXPECTED CHANGE TYPES:")
    print("=" * 80)
    print("🔴 MAJOR (0): stretch_lines, Outline, removed properties, type changes")
    print("🟡 MINOR (1): elements, added properties, first-time creation")
    print("🟢 PATCH (2): Value changes for existing properties")
    print("\nSpecial room properties:")
    print("- stretch_lines: Always Major (affects room structure)")
    print("- Outline: Always Major (affects room shape)")
    print("- elements: Always Minor (furniture/fixtures)")


if __name__ == "__main__":
    test_room_update_api()

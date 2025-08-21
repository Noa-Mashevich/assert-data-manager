#!/usr/bin/env python
"""
ROOM DATA CHANGE TRACKING - COMPREHENSIVE EXAMPLE

This example demonstrates how the room data change tracking system works
with real-world room data scenarios including stretch lines, room outlines,
elements, and other room properties.
"""

import json
from typing import Dict, Any


# Simulate the room data change tracking logic
def flatten_dict(dd, separator='.', prefix=''):
    """Same flattening function as in the actual code"""
    return (
        {
            prefix + separator + k if prefix else k: v
            for kk, vv in dd.items()
            for k, v in flatten_dict(vv, separator, kk).items()
        }
        if isinstance(dd, dict)
        else {prefix: dd}
    )


def compare_room_data(previous_data, current_data):
    """Simulated room data comparison logic"""
    changes = []

    if previous_data is None:
        # First-time creation
        current_data_flattened = flatten_dict(current_data)
        for x in current_data_flattened.keys():
            changes.append(
                {
                    'type': 1,  # Minor
                    'property': x,
                    'description': f"added property '{x}'",
                    'previous_value': None,
                    'new_value': current_data_flattened[x],
                }
            )
        return changes

    current_data_flattened = flatten_dict(current_data)
    previous_data_flattened = flatten_dict(previous_data)

    # Special processing for stretch_lines (Major change)
    previous_stretch_lines = previous_data.get('stretch_lines', [])
    previous_data_flattened.pop('stretch_lines', None)
    current_stretch_lines = current_data.get('stretch_lines', [])
    current_data_flattened.pop('stretch_lines', None)

    if json.dumps(current_stretch_lines) != json.dumps(previous_stretch_lines):
        changes.append(
            {
                'type': 0,  # Major
                'property': 'stretch_lines',
                'description': "changed value for property 'stretch_lines'",
                'previous_value': previous_stretch_lines,
                'new_value': current_stretch_lines,
            }
        )

    # Special processing for Outline (Major change)
    previous_outline = previous_data.get('Outline', [])
    previous_data_flattened.pop('Outline', None)
    current_outline = current_data.get('Outline', [])
    current_data_flattened.pop('Outline', None)

    if json.dumps(current_outline) != json.dumps(previous_outline):
        changes.append(
            {
                'type': 0,  # Major
                'property': 'Outline',
                'description': "changed value for property 'Outline'",
                'previous_value': previous_outline,
                'new_value': current_outline,
            }
        )

    # Special processing for elements (Minor change)
    previous_elements = previous_data.get('elements', [])
    previous_data_flattened.pop('elements', None)
    current_elements = current_data.get('elements', [])
    current_data_flattened.pop('elements', None)

    if json.dumps(current_elements) != json.dumps(previous_elements):
        changes.append(
            {
                'type': 1,  # Minor
                'property': 'elements',
                'description': "changed value for property 'elements'",
                'previous_value': previous_elements,
                'new_value': current_elements,
            }
        )

    # Regular property comparison (same as element data)
    removed_properties = {
        x: previous_data_flattened[x]
        for x in previous_data_flattened
        if x not in current_data_flattened
    }

    for removed_property_name in removed_properties.keys():
        changes.append(
            {
                'type': 0,  # Major
                'property': removed_property_name,
                'description': f"removed property '{removed_property_name}'",
                'previous_value': removed_properties[removed_property_name],
                'new_value': None,
            }
        )

    type_changed_properties = {
        x: current_data_flattened[x]
        for x in current_data_flattened
        if x in previous_data_flattened
        and type(current_data_flattened[x]) != type(previous_data_flattened[x])
    }

    for type_changed_property_name in type_changed_properties.keys():
        changes.append(
            {
                'type': 0,  # Major
                'property': type_changed_property_name,
                'description': f"changed type for property '{type_changed_property_name}'",
                'previous_value': previous_data_flattened[type_changed_property_name],
                'new_value': current_data_flattened[type_changed_property_name],
            }
        )

    added_properties = {
        x: current_data_flattened[x]
        for x in current_data_flattened
        if x not in previous_data_flattened
    }

    for added_property_name in added_properties.keys():
        changes.append(
            {
                'type': 1,  # Minor
                'property': added_property_name,
                'description': f"added property '{added_property_name}'",
                'previous_value': None,
                'new_value': current_data_flattened[added_property_name],
            }
        )

    value_changed_properties = {
        x: current_data_flattened[x]
        for x in current_data_flattened
        if x in previous_data_flattened
        and type(current_data_flattened[x]) == type(previous_data_flattened[x])
        and current_data_flattened[x] != previous_data_flattened[x]
    }

    for value_changed_property_name in value_changed_properties.keys():
        changes.append(
            {
                'type': 2,  # Patch
                'property': value_changed_property_name,
                'description': f"changed value for property '{value_changed_property_name}'",
                'previous_value': previous_data_flattened[value_changed_property_name],
                'new_value': current_data_flattened[value_changed_property_name],
            }
        )

    changes.sort(key=lambda x: x.get('type'))
    return changes


def print_changes(changes):
    """Pretty print the detected changes"""
    print("\n" + "=" * 80)
    print("DETECTED CHANGES:")
    print("=" * 80)

    type_names = {0: "MAJOR", 1: "MINOR", 2: "PATCH"}

    for i, change in enumerate(changes, 1):
        print(f"\n{i}. [{type_names[change['type']]}] {change['description']}")
        print(f"   Property: {change['property']}")
        print(f"   Previous: {change['previous_value']}")
        print(f"   New:      {change['new_value']}")


# EXAMPLE 1: Office Room - Initial Creation
print("🏢 EXAMPLE 1: OFFICE ROOM - INITIAL CREATION")
print("=" * 80)

initial_office_data = {
    "room_name": "Main Office",
    "room_type": "office",
    "floor_number": 2,
    "area_sqm": 25.5,
    "ceiling_height": 2.7,
    "stretch_lines": [{"x": 0, "y": 0, "length": 5.0}, {"x": 5, "y": 0, "length": 4.0}],
    "Outline": [{"x": 0, "y": 0}, {"x": 5, "y": 0}, {"x": 5, "y": 4}, {"x": 0, "y": 4}],
    "elements": [
        {"id": 1, "type": "door", "position": {"x": 0, "y": 2}},
        {"id": 2, "type": "window", "position": {"x": 2, "y": 0}},
    ],
    "lighting": {"natural_light": True, "artificial_lights": 3},
    "ventilation": {"air_conditioning": True, "heating": True},
}

changes = compare_room_data(None, initial_office_data)
print_changes(changes)

# EXAMPLE 2: Office Room - Adding Furniture and Changing Layout
print("\n\n🏢 EXAMPLE 2: OFFICE ROOM - ADDING FURNITURE AND CHANGING LAYOUT")
print("=" * 80)

updated_office_data = {
    "room_name": "Main Office",
    "room_type": "office",
    "floor_number": 2,
    "area_sqm": 25.5,
    "ceiling_height": 2.7,
    "stretch_lines": [
        {"x": 0, "y": 0, "length": 5.0},
        {"x": 5, "y": 0, "length": 4.0},
        {"x": 0, "y": 4, "length": 5.0},  # Added new stretch line
    ],
    "Outline": [{"x": 0, "y": 0}, {"x": 5, "y": 0}, {"x": 5, "y": 4}, {"x": 0, "y": 4}],
    "elements": [
        {"id": 1, "type": "door", "position": {"x": 0, "y": 2}},
        {"id": 2, "type": "window", "position": {"x": 2, "y": 0}},
        {"id": 3, "type": "desk", "position": {"x": 1, "y": 1}},  # Added desk
        {"id": 4, "type": "chair", "position": {"x": 1.5, "y": 1}},  # Added chair
    ],
    "lighting": {"natural_light": True, "artificial_lights": 4},  # Increased from 3 to 4
    "ventilation": {"air_conditioning": True, "heating": True},
    "furniture": {"desk_material": "wood", "chair_type": "ergonomic"},  # New property
}

changes = compare_room_data(initial_office_data, updated_office_data)
print_changes(changes)

# EXAMPLE 3: Conference Room - Major Renovation
print("\n\n🏢 EXAMPLE 3: CONFERENCE ROOM - MAJOR RENOVATION")
print("=" * 80)

conference_room_v1 = {
    "room_name": "Conference Room A",
    "room_type": "conference",
    "capacity": 8,
    "stretch_lines": [{"x": 0, "y": 0, "length": 6.0}, {"x": 6, "y": 0, "length": 4.0}],
    "Outline": [{"x": 0, "y": 0}, {"x": 6, "y": 0}, {"x": 6, "y": 4}, {"x": 0, "y": 4}],
    "elements": [
        {"id": 1, "type": "door", "position": {"x": 0, "y": 2}},
        {"id": 2, "type": "table", "position": {"x": 1, "y": 1}},
    ],
    "technology": {"projector": True, "whiteboard": True},
}

conference_room_v2 = {
    "room_name": "Conference Room A",
    "room_type": "conference",
    "capacity": 12,  # Increased capacity
    "stretch_lines": [
        {"x": 0, "y": 0, "length": 8.0},  # Extended length
        {"x": 8, "y": 0, "length": 5.0},  # Extended width
    ],
    "Outline": [
        {"x": 0, "y": 0},
        {"x": 8, "y": 0},  # Extended
        {"x": 8, "y": 5},  # Extended
        {"x": 0, "y": 5},  # Extended
    ],
    "elements": [
        {"id": 1, "type": "door", "position": {"x": 0, "y": 2.5}},
        {"id": 2, "type": "table", "position": {"x": 1, "y": 1}},
        {"id": 3, "type": "projector_screen", "position": {"x": 7, "y": 2.5}},
        {"id": 4, "type": "speaker", "position": {"x": 4, "y": 0.5}},
        {"id": 5, "type": "speaker", "position": {"x": 4, "y": 4.5}},
    ],
    "technology": {
        "projector": True,
        "whiteboard": True,
        "video_conferencing": True,  # Added
        "sound_system": True,  # Added
    },
    "acoustics": {  # New property
        "sound_absorption": "high",
        "noise_reduction": "medium",
    },
}

changes = compare_room_data(conference_room_v1, conference_room_v2)
print_changes(changes)

# EXAMPLE 4: Bathroom - Type Changes and Removals
print("\n\n🏢 EXAMPLE 4: BATHROOM - TYPE CHANGES AND REMOVALS")
print("=" * 80)

bathroom_v1 = {
    "room_name": "Bathroom 101",
    "room_type": "bathroom",
    "floor_number": 1,
    "area_sqm": 8.5,
    "stretch_lines": [{"x": 0, "y": 0, "length": 3.0}, {"x": 3, "y": 0, "length": 2.5}],
    "Outline": [
        {"x": 0, "y": 0},
        {"x": 3, "y": 0},
        {"x": 3, "y": 2.5},
        {"x": 0, "y": 2.5},
    ],
    "elements": [
        {"id": 1, "type": "toilet", "position": {"x": 0.5, "y": 0.5}},
        {"id": 2, "type": "sink", "position": {"x": 1.5, "y": 0.3}},
        {"id": 3, "type": "shower", "position": {"x": 2, "y": 1}},
    ],
    "plumbing": {"water_supply": True, "drainage": True, "hot_water": True},
    "ventilation": {"exhaust_fan": True, "window": False},
    "accessibility": "standard",  # String value
}

bathroom_v2 = {
    "room_name": "Bathroom 101",
    "room_type": "bathroom",
    "floor_number": 1,
    "area_sqm": 8.5,
    "stretch_lines": [{"x": 0, "y": 0, "length": 3.0}, {"x": 3, "y": 0, "length": 2.5}],
    "Outline": [
        {"x": 0, "y": 0},
        {"x": 3, "y": 0},
        {"x": 3, "y": 2.5},
        {"x": 0, "y": 2.5},
    ],
    "elements": [
        {"id": 1, "type": "toilet", "position": {"x": 0.5, "y": 0.5}},
        {"id": 2, "type": "sink", "position": {"x": 1.5, "y": 0.3}},
        {
            "id": 4,
            "type": "grab_bar",
            "position": {"x": 0.3, "y": 0.8},
        },  # Replaced shower with grab bar
    ],
    "plumbing": {
        "water_supply": True,
        "drainage": True,
        # Removed hot_water
    },
    "ventilation": {"exhaust_fan": True, "window": True},  # Changed from False to True
    "accessibility": {  # Changed from string to object
        "level": "enhanced",
        "features": ["grab_bars", "wide_door", "low_sink"],
    },
    "maintenance": {  # New property
        "last_cleaned": "2024-01-15",
        "next_service": "2024-02-15",
    },
}

changes = compare_room_data(bathroom_v1, bathroom_v2)
print_changes(changes)

print("\n\n" + "=" * 80)
print("SUMMARY OF ROOM DATA CHANGE TYPES:")
print("=" * 80)
print("🔴 MAJOR (0): Stretch lines, Outline, removed properties, type changes")
print("🟡 MINOR (1): Elements, added properties, first-time creation")
print("🟢 PATCH (2): Value changes for existing properties")
print("\nSpecial handling for room-specific properties:")
print("- stretch_lines: Always Major change (affects room structure)")
print("- Outline: Always Major change (affects room shape)")
print("- elements: Always Minor change (furniture/fixtures)")

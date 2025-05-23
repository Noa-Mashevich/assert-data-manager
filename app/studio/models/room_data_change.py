import json

from django.db import models

from .data_change_type import DataChangeType
from .room_data import RoomData


def flatten_dict(dd, separator='.', prefix=''):
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
    changes = []

    current_data_flattened = flatten_dict(current_data)

    if previous_data is None:
        for x in current_data_flattened.keys():
            changes.append(
                {
                    'type': DataChangeType.Minor,
                    'description': f"added property '{x}'",
                }
            )
        return changes

    previous_data_flattened = flatten_dict(previous_data)

    # Special processing for stretch lines.
    previous_stretch_lines = previous_data.get('stretch_lines', [])
    previous_data_flattened.pop('stretch_lines', None)
    current_stretch_lines = current_data.get('stretch_lines', [])
    current_data_flattened.pop('stretch_lines', None)

    if json.dumps(current_stretch_lines) != json.dumps(previous_stretch_lines):
        changes.append(
            {
                'type': DataChangeType.Major,
                'description': f"changed value for property 'stretch_lines'",
            }
        )

    # Special processing for room size.
    previous_room_size = previous_data.get('Outline', [])
    previous_data_flattened.pop('Outline', None)
    current_room_size = current_data.get('Outline', [])
    current_data_flattened.pop('Outline', None)

    if json.dumps(current_room_size) != json.dumps(previous_room_size):
        changes.append(
            {
                'type': DataChangeType.Major,
                'description': f"changed value for property 'Outline'",
            }
        )

    # Special processing for elements.
    previous_elements = previous_data.get('elements', [])
    previous_data_flattened.pop('elements', None)
    current_elements = current_data.get('elements', [])
    current_data_flattened.pop('elements', None)

    if json.dumps(current_elements) != json.dumps(previous_elements):
        changes.append(
            {
                'type': DataChangeType.Minor,
                'description': f"changed value for property 'elements'",
            }
        )

    removed_properties = {
        x: previous_data_flattened[x]
        for x in previous_data_flattened
        if x not in current_data_flattened
    }

    for removed_property_name in removed_properties.keys():
        changes.append(
            {
                'type': DataChangeType.Major,
                'description': f"removed property '{removed_property_name}'",
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
                'type': DataChangeType.Major,
                'description': f"changed type for property '{type_changed_property_name}'",
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
                'type': DataChangeType.Minor,
                'description': f"added property '{added_property_name}'",
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
                'type': DataChangeType.Patch,
                'description': f"changed value for property '{value_changed_property_name}'",
            }
        )

    changes.sort(key=lambda x: x.get('type'))

    return changes


class RoomDataChangeManager(models.Manager):
    def create_from_data_comparison(self, previous_room_data, current_room_data):
        previous_data = (
            previous_room_data.data if previous_room_data is not None else None
        )
        current_data = current_room_data.data

        changes = compare_room_data(previous_data, current_data)

        for change in changes:
            type = int(change.get('type'))
            description = change.get('description')

            self.model.objects.create(
                room_data=current_room_data,
                type=type,
                description=description,
            )


class RoomDataChange(models.Model):
    room_data = models.ForeignKey(RoomData, on_delete=models.RESTRICT)
    type = models.IntegerField()
    description = models.TextField(default='')

    objects = RoomDataChangeManager()

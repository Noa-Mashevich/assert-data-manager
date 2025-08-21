from django.db import models

from .data_change_type import DataChangeType
from .element_data import ElementData


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


def compare_element_data(previous_data, current_data):
    changes = []

    current_data_flattened = flatten_dict(current_data)

    # Logic 1: Find properties that exist in current but NOT in previous.
    if previous_data is None:
        for x in current_data_flattened.keys():
            changes.append(
                {
                    'type': DataChangeType.Minor,
                    'property': x,
                    'description': f"added property '{x}'",
                    'previous_value': None,
                    'new_value': current_data_flattened[x],
                }
            )
        return changes

    previous_data_flattened = flatten_dict(previous_data)

    # Logic 2: Find properties that exist in previous but NOT in current.
    removed_properties = {
        x: previous_data_flattened[x]
        for x in previous_data_flattened
        if x not in current_data_flattened
    }

    for removed_property_name in removed_properties.keys():
        changes.append(
            {
                'type': DataChangeType.Major,
                'property': removed_property_name,
                'description': f"removed property '{removed_property_name}'",
                'previous_value': removed_properties[removed_property_name],
                'new_value': None,
            }
        )

    # Logic 3: Find properties that exist in both but have different data types.
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
                'property': type_changed_property_name,
                'description': f"changed type for property '{type_changed_property_name}'",
                'previous_value': previous_data_flattened[type_changed_property_name],
                'new_value': current_data_flattened[type_changed_property_name],
            }
        )

    # Logic 4: Find properties that exist in current but NOT in previous.
    added_properties = {
        x: current_data_flattened[x]
        for x in current_data_flattened
        if x not in previous_data_flattened
    }

    for added_property_name in added_properties.keys():
        changes.append(
            {
                'type': DataChangeType.Minor,
                'property': added_property_name,
                'description': f"added property '{added_property_name}'",
                'previous_value': None,
                'new_value': current_data_flattened[added_property_name],
            }
        )

    # Logic 5: Find properties that exist in both with same type but different values.
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
                'property': value_changed_property_name,
                'description': f"changed value for property '{value_changed_property_name}'",
                'previous_value': previous_data_flattened[value_changed_property_name],
                'new_value': current_data_flattened[value_changed_property_name],
            }
        )

    changes.sort(key=lambda x: x.get('type'))

    return changes


class ElementDataChangeManager(models.Manager):
    def create_from_data_comparison(self, previous_element_data, current_element_data):
        previous_data = (
            previous_element_data.data if previous_element_data is not None else None
        )
        current_data = current_element_data.data

        changes = compare_element_data(previous_data, current_data)

        for change in changes:
            type = int(change.get('type'))
            description = change.get('description')
            property = change.get('property')
            previous_value = change.get('previous_value')
            new_value = change.get('new_value')

            self.model.objects.create(
                element_data=current_element_data,
                type=type,
                description=description,
                property=property,
                previous_value=previous_value,
                new_value=new_value,
            )


class ElementDataChange(models.Model):
    element_data = models.ForeignKey('ElementData', on_delete=models.RESTRICT)
    type = models.IntegerField()
    description = models.TextField(default='')
    property = models.TextField(null=True, blank=True)
    previous_value = models.JSONField(null=True, blank=True)
    new_value = models.JSONField(null=True, blank=True)

    objects = ElementDataChangeManager()

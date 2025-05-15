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

            self.model.objects.create(
                element_data=current_element_data,
                type=type,
                description=description,
            )


class ElementDataChange(models.Model):
    element_data = models.ForeignKey(ElementData, on_delete=models.RESTRICT)
    type = models.IntegerField()
    description = models.TextField(default='')

    objects = ElementDataChangeManager()

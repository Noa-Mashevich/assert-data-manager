from django.db import models

from .element_data import ElementData
from .entity_type import EntityType
from .file import File
from .room_data import RoomData
from .room_element import RoomElement


class FileOwnershipManager(models.Manager):
    def by_file_id(self, file_id):
        return self.model.objects.filter(file_id=file_id).first()

    def create_for_entity_data(self, file_type, entity_data):
        parent_entity = entity_data.get_parent()
        entity_type = (
            parent_entity.get_entity_type()
            if parent_entity is not None
            else entity_data.get_entity_type()
        )
        entity_id = parent_entity.pk if parent_entity is not None else entity_data.pk

        file = File.objects.create_for_type(
            file_type, entity_type.get_s3_prefix(entity_id)
        )

        ownership = None
        if entity_type == EntityType.Element:
            ownership = self.model.objects.create(file=file, element_data=entity_data)
        if entity_type == EntityType.Room:
            ownership = self.model.objects.create(file=file, room_data=entity_data)
        if entity_type == EntityType.RoomElement:
            ownership = self.model.objects.create(file=file, room_element=entity_data)

        if ownership is None:
            raise ValueError('Ownership was not created')

        return ownership


class FileOwnership(models.Model):
    file = models.ForeignKey(
        File, related_name='ownership', null=True, on_delete=models.RESTRICT
    )
    element_data = models.ForeignKey(ElementData, null=True, on_delete=models.RESTRICT)
    room_data = models.ForeignKey(RoomData, null=True, on_delete=models.RESTRICT)
    room_element = models.ForeignKey(RoomElement, null=True, on_delete=models.RESTRICT)

    objects = FileOwnershipManager()

    def get_entity_type(self):
        if self.element_data is not None:
            return EntityType.Element
        if self.room_data is not None:
            return EntityType.Room
        if self.room_element is not None:
            return EntityType.RoomElement
        raise ValueError('File ownership is not linked to any entity type')

    def get_entity_id(self):
        if self.element_data is not None:
            return self.element_data.get_parent().pk
        if self.room_data is not None:
            return self.room_data.get_parent().pk
        if self.room_element is not None:
            return self.room_element.pk
        raise ValueError('File ownership is not linked to any entity id')

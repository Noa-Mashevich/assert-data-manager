from django.db import models

from .element_data import ElementData
from .entity_type import EntityType
from .file import File


class FileOwnershipManager(models.Manager):
    def by_file_id(self, file_id):
        return self.model.objects.filter(file_id=file_id).first()

    def create_for_element(self, file_type, entity_data):
        entity = entity_data.get_parent()
        entity_type = entity.get_entity_type()

        file = File.objects.create_for_type(
            file_type, entity_type.get_s3_prefix(entity.pk)
        )

        ownership = None
        if entity_type == EntityType.Element:
            ownership = self.model.objects.create(file=file, element_data=entity_data)

        if ownership is None:
            raise ValueError('Ownership was not created')

        return ownership


class FileOwnership(models.Model):
    file = models.ForeignKey(
        File, related_name='ownership', null=True, on_delete=models.RESTRICT
    )
    element_data = models.ForeignKey(ElementData, null=True, on_delete=models.RESTRICT)
    # room_element = models.ForeignKey(RoomElement, null=True, on_delete=models.RESTRICT)
    # room = models.ForeignKey(Room, null=True, on_delete=models.RESTRICT)

    objects = FileOwnershipManager()

    def get_entity_type(self):
        if self.element_data is not None:
            return EntityType.Element
        raise ValueError('File ownership is not linked to any entity type')

    def get_entity_id(self):
        if self.element_data is not None:
            return self.element_data.get_parent().pk
        raise ValueError('File ownership is not linked to any entity id')

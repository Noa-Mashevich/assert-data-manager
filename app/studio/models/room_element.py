import json

from django.db import models
from django.utils import timezone

from server.utils import (
    get_object,
    is_migration,
    is_test,
)
from studio.file_utils import FileUtils

from .element_data import ElementData
from .entity_type import EntityType
from .room_data import RoomData


class RoomElementManager(models.Manager):
    def create_from_data(self, room_data):
        data = room_data.data
        elements = data.get('elements', [])

        for info in elements:
            element_id = info.get('element_id')
            element_version = info.get('element_version')

            if element_id is None or element_version is None:
                raise ValueError('RoomElement information is not valid')

            element_data = ElementData.objects.filter(element_id=element_id).get(
                version=element_version
            )

            self.create_for_room_and_element_data(room_data, element_data)

    def create_for_room_and_element_data(self, room_data, element_data):
        from .file_ownership import FileOwnership
        from .file_type import FileType

        room_element = self.model.objects.create(
            room_data=room_data, element_data=element_data
        )

        FileOwnership.objects.create_for_entity_data(FileType.Json, room_element)
        FileOwnership.objects.create_for_entity_data(FileType.Dxf, room_element)

        return room_element


class RoomElement(models.Model):
    room_data = models.ForeignKey(RoomData, null=True, on_delete=models.RESTRICT)
    element_data = models.ForeignKey(ElementData, null=True, on_delete=models.RESTRICT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True)

    objects = RoomElementManager()

    @property
    def files(self):
        from .file import File

        return File.objects.filter(ownership__room_element=self)

    @property
    def data(self):
        from .file import File
        from .file_type import FileType

        # TODO: shall we merge element data to these instance data?

        json_files = File.objects.filter(ownership__room_element=self, type=FileType.Json)

        if len(json_files) != 1:
            raise ValueError(f'Json file not found for room-element {self.pk}')

        json_file = json_files[0]

        if not json_file.exists:
            return {}

        # Note: only for unittesting.
        if is_migration() or is_test():
            return FileUtils.read_test_file_content(json_file.s3_key)

        json_file_s3 = get_object(json_file.s3_key)
        json_data = json.load(json_file_s3['Body'])

        return json_data

    def get_parent(self):
        return None

    def get_entity_type(self):
        return EntityType.RoomElement

    def destroy(self):
        self.deleted_at = timezone.now()
        self.save()

from django.db import models
from enum import Enum

from .entity_type import EntityType
from .file_status import FileStatus
from .file_type import FileType


class RoomCategory(Enum):
    RoomCategoryNone = ''
    FamilyRoom = 'family_room'
    DiningRoom = 'dining'
    Kitchen = 'kitchen'
    Bedroom = 'bedroom'
    Loft = 'loft'
    Closet = 'closet'
    Corridor = 'corridors'
    Stairs = 'stairs'
    UtilityRoom = 'utility_room'
    Garage = 'garage'
    OutdoorArea = 'outdoor_areas'
    Bathroom = 'bathroom'
    Study = 'study'


RoomFileTypes = [FileType.Json, FileType.Png]


class RoomManager(models.Manager):
    def create(self, *args, **kwargs):
        instance = super().create(*args, **kwargs)

        from .room_data import RoomData

        RoomData.objects.create_for_room(room=instance)

        return instance

    def by_latest_valid(self):
        raw_request = self.raw(
            'SELECT DISTINCT sr.* FROM studio_room sr '
            'INNER JOIN ('
            'SELECT DISTINCT srd.* FROM studio_roomdata srd '
            'JOIN studio_fileownership sfo ON srd.id = sfo.room_data_id '
            'JOIN studio_filenotification sfn ON sfn.file_id = sfo.file_id '
            'WHERE srd.deleted_at IS NULL AND sfn.status = %s '
            'GROUP BY srd.id '
            'HAVING COUNT(sfn.id) = srd.required_file_count '
            ') rd '
            'ON sr.id = rd.room_id ',
            [int(FileStatus.Ready)],
        )
        return list(raw_request)


class Room(models.Model):
    name = models.TextField(default='')
    category = models.TextField(default=RoomCategory.RoomCategoryNone)
    function = models.TextField(default='')
    type = models.TextField(default='')

    objects = RoomManager()

    @property
    def latest_room_data(self):
        from .room_data import RoomData

        return RoomData.objects.latest(self)

    @property
    def latest_valid_room_data(self):
        from .room_data import RoomData

        return RoomData.objects.latest_valid(self)

    @property
    def previous_room_data(self):
        from .room_data import RoomData

        return RoomData.objects.previous(self.latest_room_data)

    @property
    def versions(self):
        from .room_data import RoomData

        return RoomData.objects.versions(self)

    def get_entity_type(self):
        return EntityType.Room

    def upgrade(self):
        from .room_data import RoomData

        RoomData.objects.create_for_room(room=self)

    def destroy(self):
        versions = self.versions
        for version in versions:
            version.destroy()

        self.save()

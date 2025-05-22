from django.db import models
from django.utils import timezone
from enum import IntEnum

from .entity_type import EntityType


class RoomCategory(IntEnum):
    RoomCategoryNone = 0
    LivingRoom = 1
    DiningRoom = 2
    Kitchen = 3
    Bedroom = 4
    Loft = 5
    Closet = 6
    Corridor = 7
    Stairs = 8
    UtilityRoom = 9
    Garage = 10
    OutdoorArea = 11


class RoomManager(models.Manager):
    def create(self, *args, **kwargs):
        instance = super().create(*args, **kwargs)

        from .room_data import RoomData

        RoomData.objects.create_for_room(room=instance)

        return instance


class Room(models.Model):
    name = models.TextField(default='')
    category = models.IntegerField(default=RoomCategory.RoomCategoryNone)
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

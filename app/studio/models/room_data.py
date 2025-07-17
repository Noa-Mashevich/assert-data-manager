import hashlib
import json

from collections import OrderedDict
from django.db import (
    models,
    transaction,
)
from django.db.models import F
from django.utils import timezone

from server.utils import (
    get_object,
    is_migration,
    is_test,
)
from studio.file_utils import FileUtils

from .room import (
    Room,
    RoomFileTypes,
)
from .room_data_status import RoomDataStatus


class RoomDataManager(models.Manager):
    @transaction.atomic
    def create_versioned_room(self, room):
        room_data_versions = self.model.objects.filter(room=room)
        if len(room_data_versions) == 0:
            version = 1
        else:
            version = room.latest_room_data.version + 1
        room_data = self.model.objects.create(room=room, version=version)
        return room_data

    def create_for_room(self, room):
        from .file_ownership import FileOwnership

        room_data = self.model.objects.create_versioned_room(room=room)

        for file_type in RoomFileTypes:
            FileOwnership.objects.create_for_entity_data(file_type, room_data)

        return room_data

    def latest(self, room):
        room_data_versions = self.model.objects.filter(room=room).order_by('-version')

        if len(room_data_versions) == 0:
            raise ValueError(f'Room data not found for room {room.pk}')

        return room_data_versions[0]

    def latest_valid(self, room):
        room_data_versions = self.model.objects.filter(
            room=room, deleted_at__isnull=True
        ).order_by('-version')

        valid_room_data = [
            x for x in room_data_versions if x.status == RoomDataStatus.Complete
        ]

        if len(valid_room_data) == 0:
            return None

        return valid_room_data[0]

    def previous(self, room_data):
        room_data_versions = self.model.objects.filter(room=room_data.get_parent())

        previous_version = [
            x for x in room_data_versions if x.version == room_data.version - 1
        ]

        if len(previous_version) != 1:
            return None

        return previous_version[0]

    def versions(self, room):
        return self.model.objects.filter(room=room).order_by('-version')


class RoomData(models.Model):
    room = models.ForeignKey(Room, on_delete=models.RESTRICT)
    version = models.BigIntegerField()
    data = models.JSONField(default=dict)
    required_file_count = models.IntegerField(default=len(RoomFileTypes), db_index=True)
    current_file_count = models.IntegerField(default=0, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, db_index=True)

    objects = RoomDataManager()

    class Meta:
        # newest first
        ordering = ['-version']

        indexes = [
            models.Index(
                fields=['deleted_at', 'current_file_count', 'required_file_count']
            ),
        ]

    @property
    def status(self) -> int:
        from .file import File

        files = File.objects.filter(ownership__room_data=self)

        if not all([x.exists for x in files]):
            return RoomDataStatus.Incomplete

        return RoomDataStatus.Complete

    @property
    def files(self):
        from .file import File

        return File.objects.filter(ownership__room_data=self)

    @property
    def elements(self):
        from .room_element import RoomElement

        return RoomElement.objects.filter(room_data=self, deleted_at__isnull=True)

    @property
    def data_hash(self):
        hash_data = dict(OrderedDict(sorted(self.data.items())))
        content = json.dumps(hash_data).encode('utf-8')
        return hashlib.md5(content).hexdigest()

    def get_data_from_file(self):
        from .file import File
        from .file_type import FileType

        json_files = File.objects.filter(ownership__room_data=self, type=FileType.Json)

        if len(json_files) != 1:
            raise ValueError(
                f'Json file not found for room {self.pk} version = {self.version}'
            )

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
        return self.room

    def increment_file_count(self):
        RoomData.objects.filter(id=self.id).update(
            current_file_count=F('current_file_count') + 1
        )
        self.refresh_from_db()

    def track_changes(self):
        from .room_data_change import RoomDataChange
        from .room_element import RoomElement

        self.data = self.get_data_from_file()
        self.save(is_updating=True)

        previous_room_data = RoomData.objects.previous(self)

        RoomDataChange.objects.create_from_data_comparison(previous_room_data, self)

        RoomElement.objects.create_from_data(self)

    def destroy(self):
        self.deleted_at = timezone.now()
        self.save(is_updating=True)

    def save(self, is_updating=False, *args, **kwargs):
        # Insert a new record when not updating.
        if not is_updating:
            self.pk = None
        super().save(*args, **kwargs)

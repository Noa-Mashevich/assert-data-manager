from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from studio.models.room_element import RoomElement
from studio.serializers.file import FileSerializer


class RoomElementSerializer(ModelSerializer):
    room_id = serializers.SerializerMethodField()
    room_version = serializers.SerializerMethodField()
    element_id = serializers.SerializerMethodField()
    element_version = serializers.SerializerMethodField()
    files = FileSerializer(many=True, read_only=True)

    class Meta:
        model = RoomElement
        fields = [
            'id',
            'room_id',
            'room_version',
            'element_id',
            'element_version',
            'files',
            'created_at',
            'updated_at',
            'deleted_at',
        ]

    def get_room_id(self, obj) -> int:
        return obj.room_data.room.id

    def get_room_version(self, obj) -> int:
        return obj.room_data.version

    def get_element_id(self, obj) -> int:
        return obj.element_data.element.id

    def get_element_version(self, obj) -> int:
        return obj.element_data.version

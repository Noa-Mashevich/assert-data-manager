from rest_framework.serializers import ModelSerializer

from studio.models.room_data import RoomData
from studio.serializers.file import (
    FileReadSerializer,
    FileWriteSerializer,
)
from studio.serializers.room_element import RoomElementSerializer


class RoomDataWriteSerializer(ModelSerializer):
    files = FileWriteSerializer(many=True, read_only=True)
    elements = RoomElementSerializer(many=True, read_only=True)

    class Meta:
        model = RoomData
        fields = [
            'id',
            'version',
            'status',
            'files',
            'elements',
            'data',
            'data_hash',
            'created_at',
            'updated_at',
            'deleted_at',
        ]


class RoomDataReadSerializer(ModelSerializer):
    files = FileReadSerializer(many=True, read_only=True)
    elements = RoomElementSerializer(many=True, read_only=True)

    class Meta:
        model = RoomData
        fields = [
            'id',
            'version',
            'status',
            'files',
            'elements',
            'data',
            'data_hash',
            'created_at',
            'updated_at',
            'deleted_at',
        ]

from rest_framework.serializers import ModelSerializer

from studio.models.element_data import ElementData
from studio.serializers.file import (
    FileReadSerializer,
    FileWriteSerializer,
)


class ElementDataWriteSerializer(ModelSerializer):
    files = FileWriteSerializer(many=True, read_only=True)

    class Meta:
        model = ElementData
        fields = [
            'id',
            'version',
            'status',
            'files',
            'data',
            'data_hash',
            'created_at',
            'updated_at',
            'deleted_at',
        ]


class ElementDataReadSerializer(ModelSerializer):
    files = FileReadSerializer(many=True, read_only=True)

    class Meta:
        model = ElementData
        fields = [
            'id',
            'version',
            'status',
            'files',
            'data',
            'data_hash',
            'created_at',
            'updated_at',
            'deleted_at',
        ]

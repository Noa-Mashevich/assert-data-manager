from rest_framework.serializers import ModelSerializer

from studio.models.file import File


class FileWriteSerializer(ModelSerializer):
    class Meta:
        model = File
        fields = [
            'id',
            'type',
            'content_type',
            'status',
            'upload_url',
            'created_at',
        ]


class FileReadSerializer(ModelSerializer):
    class Meta:
        model = File
        fields = [
            'id',
            'type',
            'content_type',
            'status',
            'download_url',
            'created_at',
        ]


class FileSerializer(ModelSerializer):
    class Meta:
        model = File
        fields = [
            'id',
            'type',
            'content_type',
            'status',
            'download_url',
            'upload_url',
            'created_at',
        ]

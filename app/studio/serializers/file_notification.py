import os

from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import Field
from rest_framework.serializers import ModelSerializer

from studio.models.entity_type import EntityType
from studio.models.file_notification import FileNotification
from studio.models.file_status import FileStatus


class FileNotificationStatus(Field):
    write_only = True

    def to_internal_value(self, data):
        assert isinstance(data, str)

        if data.startswith('ObjectCreated:'):
            return FileStatus.Ready

        if data.startswith('ObjectRemoved:'):
            return FileStatus.Deleted

        raise ValidationError(f'Unknown S3 eventName: {data}')


class FileNotificationSerializer(ModelSerializer):
    write_only = True

    eventName = FileNotificationStatus(source='status')
    # these fields map directly to the message from s3
    key = serializers.CharField(source='s3_key')
    size = serializers.IntegerField(source='s3_size')
    eTag = serializers.CharField(source='s3_etag')

    def get_file_metadata(self):
        # For example: studio/elements/123/files/456.json
        key = self.validated_data['s3_key']

        entity_type = EntityType.from_s3_file_name(key)

        path = os.path.splitext(key)[0].split('/')
        assert len(path) >= 5

        entity_id = int(path[2])
        file_id = int(path[4])

        return int(entity_type), entity_id, file_id

    def create(self, validated_data):
        # additional fields for an instance of the model
        file_metadata = self.get_file_metadata()
        validated_data['file_id'] = file_metadata[2]
        return FileNotification.objects.create(**validated_data)

    class Meta:
        model = FileNotification
        fields = [
            'eventName',
            'key',
            'size',
            'eTag',
        ]

import json

from django.conf import settings
from django.db import models
from django.dispatch import receiver

from server.utils import is_migration

from .entity_type import EntityType
from .file_status import FileStatus


class FileNotificationManager(models.Manager):
    def __init__(self, *args, **kwargs):
        super(models.Manager, self).__init__(*args, **kwargs)
        self.queue_url = self._get_queue_url()

    def _get_queue_url(self):
        # do not run this in migrations
        if is_migration():
            return None

        return settings.QUEUE_URL

    def create_from_queue(self, json_message):
        from studio.serializers.file_notification import FileNotificationSerializer

        json_data = json.loads(json_message)
        notification_data = json_data['Records'][0]

        # s3 details
        file_data = notification_data['s3']['object']

        # s3 notifications coming here are unfiltered
        # skip if the s3 object isn't recognized
        try:
            EntityType.from_s3_file_name(file_data['key'])
        except Exception:
            return

        # skipping adding extra serializer
        file_data['eventName'] = notification_data['eventName']

        notification = FileNotificationSerializer(data=file_data)
        notification.is_valid(raise_exception=True)
        return notification.save()

    def file_status(self, file):
        notification = self.filter(s3_key=file.s3_key).first()
        if notification is None:
            return FileStatus.Created
        return notification.status


class FileNotification(models.Model):
    file_id = models.BigIntegerField()
    status = models.IntegerField(default=FileStatus.Created)
    s3_key = models.CharField(max_length=1024, db_index=True)
    s3_size = models.IntegerField()
    s3_etag = models.CharField(max_length=1024)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = FileNotificationManager()

    class Meta:
        # newest first
        ordering = ['-created_at']


# TODO temporary, remove, launch by api
@receiver(models.signals.post_save, sender=FileNotification)
def continue_after_save(sender, instance, created, *args, **kwargs):
    from .file import File

    if created:
        File.objects.on_notification(instance)

from django.db import models

from studio.models import Schema


class Validator(models.Model):
    data = models.JSONField()
    version = models.CharField(max_length=128)
    success = models.BooleanField()
    message = models.TextField()

    def validate(self):
        if 'version' not in self.data:
            raise Exception('Missing version in input data')

        self.version = self.data['version']

        schema = Schema.objects.create_from_version(self.version)
        success, message = schema.validate(self.data)

        self.success = success
        self.message = message

        if not success:
            raise Exception(message)

    @property
    def schema_version(self):
        return self.version

    @property
    def validation_message(self):
        return self.message

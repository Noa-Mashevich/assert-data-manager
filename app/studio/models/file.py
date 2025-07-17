import boto3
import datetime

from botocore.signers import CloudFrontSigner
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from django.conf import settings
from django.db import models
from django.http import Http404

from server.utils import (
    invoke_lambda,
    is_migration,
    is_test,
)

from .entity_type import EntityType
from .file_notification import FileNotification
from .file_status import FileStatus
from .file_type import FileType
from .stack import Stack


class FileManager(models.Manager):
    def __init__(self, *args, **kwargs):
        super(FileManager, self).__init__(*args, **kwargs)
        self.cloudfront_signer = self._get_cloudfront_signer()

    def create_for_type(self, file_type, s3_prefix):
        return self.model.objects.create(type=file_type, s3_prefix=s3_prefix)

    def _get_cloudfront_signer(self):
        # skip running this logic in migrations
        # TODO: should this also be skipped when unit-testing?
        if is_migration() or is_test():
            return

        public_key_id = Stack.objects.output(
            settings.AWS_STACK_STORAGE_CDN_REGION,
            settings.AWS_STACK_STORAGE_CDN,
            'StudioPublicKeyId',
        )
        ssm_parameter_name = Stack.objects.output(
            settings.AWS_STACK_STORAGE_CDN_REGION,
            settings.AWS_STACK_STORAGE_CDN,
            'StudioPrivateKeySSM',
        )
        ssm_client = boto3.client(
            'ssm', region_name=settings.AWS_STACK_STORAGE_CDN_REGION
        )
        private_key_parameter = ssm_client.get_parameter(
            Name=ssm_parameter_name, WithDecryption=True
        )
        private_key_value = private_key_parameter['Parameter']['Value']
        private_key = serialization.load_pem_private_key(
            bytes(private_key_value, encoding='utf-8'),
            password=None,
            backend=default_backend(),
        )
        return CloudFrontSigner(
            public_key_id,
            lambda message: private_key.sign(
                message,
                padding.PKCS1v15(),
                hashes.SHA1(),
            ),
        )

    def get_signed_url(self, s3_key):
        base_url = Stack.objects.output(
            settings.AWS_STACK_STORAGE_CDN_REGION,
            settings.AWS_STACK_STORAGE_CDN,
            'BaseURL',
        )
        url = base_url + s3_key
        url_expiration = 3600
        expires_at = datetime.datetime.now() + datetime.timedelta(seconds=url_expiration)
        return self.cloudfront_signer.generate_presigned_url(url, expires_at)

    def on_notification(self, file_notification):
        file = self.model.objects.filter(s3_key=file_notification.s3_key).first()

        file_ownership = file.ownership.get()

        if not file.exists:
            entity_name = file_ownership.get_entity_type().get_name()
            entity_id = file_ownership.get_entity_id()
            raise ValueError(
                f'File {file_notification.s3_key} not found with status {file_notification.status} on {entity_name} {entity_id}'
            )

        if file_ownership.get_entity_type() == EntityType.Element:
            file_ownership.element_data.increment_file_count()

            if file.type == FileType.Json:
                file_ownership.element_data.track_changes()

        if file_ownership.get_entity_type() == EntityType.Room:
            file_ownership.room_data.increment_file_count()

            if file.type == FileType.Json:
                file_ownership.room_data.track_changes()

        if file_ownership.get_entity_type() == EntityType.RoomElement:
            if file.type == FileType.Json:
                file_ownership.room_element.track_changes()


class File(models.Model):
    type = models.IntegerField()
    s3_prefix = models.CharField(max_length=1024, null=True, db_index=True)
    s3_key = models.CharField(max_length=1024, null=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = FileManager()

    class Meta:
        # newest first
        ordering = ['-created_at']

        indexes = [models.Index(fields=['type'])]

    @property
    def content_type(self) -> str:
        return FileType(self.type).get_content_type()

    @property
    def extension(self) -> str:
        return FileType(self.type).get_extension()

    @property
    def upload_url(self) -> str:
        if self.exists:
            return None

        if is_test():
            return 'placeholder_upload_url'

        # upload system expects path w/o app name prefix
        s3_path = self.get_s3_key.removeprefix('studio/')
        payload = {
            'app': 'studio',
            'event_type': 'simple',
            'path': s3_path,
            'content_type': self.content_type,
            'expires_in': 3600,
        }
        upload_lambda_arn = Stack.objects.output(
            settings.AWS_REGION, settings.AWS_STACK_UPLOAD, 'HandlerLambdaARN'
        )
        json_response = invoke_lambda(upload_lambda_arn, payload)
        signed_url = json_response.get('signed_url', None)

        if not signed_url:
            raise ValueError(f'Error getting a upload URL for {self.s3_key}')

        return signed_url

    @property
    def download_url(self) -> str:
        if not self.exists:
            return None

        if is_test():
            return 'placeholder_download_url'

        try:
            s3_key = self.get_s3_key
        except Exception:
            raise Http404

        return File.objects.get_signed_url(s3_key)

    @property
    def s3_url(self):
        return f's3://{settings.AWS_STACK_STORAGE}/{self.s3_key}'

    @property
    def exists(self):
        return self.status == FileStatus.Ready

    @property
    def get_s3_key(self):
        if not self.s3_key:
            raise ValueError(f'Missing S3 key on file {self.pk}')
        return self.s3_key

    def create_s3_key(self):
        return f'{self.s3_prefix}/files/{self.pk}.{self.extension}'

    @property
    def status(self) -> int:
        return FileNotification.objects.file_status(self)

    def save(self, *args, **kwargs):
        super(File, self).save(*args, **kwargs)
        self.s3_key = self.create_s3_key()
        File.objects.filter(pk=self.pk).update(s3_key=self.s3_key)

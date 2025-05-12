from django.test import TestCase

from studio.models.file import File
from studio.models.file_status import FileStatus
from studio.models.file_type import FileType


class TestFile(TestCase):
    def test_initialization(self):
        file = File.objects.create(type=FileType.Json, s3_prefix='studio/elements/1')

        self.assertEqual(file.status, FileStatus.Created)
        self.assertFalse(file.exists)
        self.assertEqual(file.s3_key, 'studio/elements/1/files/1.json')

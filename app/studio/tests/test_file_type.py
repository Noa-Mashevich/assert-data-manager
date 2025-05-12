from django.test import TestCase

from studio.models.file_type import FileType


class TestFileType(TestCase):
    def test_get_content_type(self):
        for t in FileType:
            if t == FileType.FileTypeNone:
                with self.assertRaises(ValueError):
                    t.get_content_type()
            else:
                content_type = t.get_content_type()
                self.assertGreater(len(content_type), 0)

    def test_get_extension(self):
        for t in FileType:
            if t == FileType.FileTypeNone:
                with self.assertRaises(ValueError):
                    t.get_extension()
            else:
                extension = t.get_extension()
                self.assertGreater(len(extension), 0)

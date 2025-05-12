from django.test import TestCase

from studio.models.entity_type import EntityType


class TestEntityType(TestCase):
    def test_get_name(self):
        for t in EntityType:
            if t == EntityType.EntityTypeNone:
                with self.assertRaises(ValueError):
                    t.get_name()
            else:
                name = t.get_name()
                self.assertGreater(len(name), 0)

    def test_get_s3_folder(self):
        for t in EntityType:
            if t == EntityType.EntityTypeNone:
                with self.assertRaises(ValueError):
                    t.get_s3_folder()
            else:
                s3_folder = t.get_s3_folder()
                self.assertGreater(len(s3_folder), 0)

    def test_get_s3_prefix(self):
        self.assertEqual(EntityType.Element.get_s3_prefix(12), 'studio/elements/12')

    def test_from_s3_file_name(self):
        entity_type = EntityType.from_s3_file_name('studio/elements/1/files/1.json')
        self.assertEqual(entity_type, EntityType.Element)

        entity_type = EntityType.from_s3_file_name('studio/roomelements/1/files/1.json')
        self.assertEqual(entity_type, EntityType.RoomElement)

        entity_type = EntityType.from_s3_file_name('studio/rooms/1/files/1.json')
        self.assertEqual(entity_type, EntityType.Room)

        with self.assertRaises(ValueError):
            EntityType.from_s3_file_name('blah.json')

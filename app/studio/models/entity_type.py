from enum import IntEnum


class EntityType(IntEnum):
    EntityTypeNone = 0
    Element = 1
    RoomElement = 2
    Room = 3

    def get_name(self):
        if self.value == EntityType.Element:
            return 'element'
        elif self.value == EntityType.RoomElement:
            return 'room-element'
        elif self.value == EntityType.Room:
            return 'room'
        raise ValueError(f'Entity type {self.value} is not valid')

    def get_s3_folder(self):
        if self.value == EntityType.Element:
            return 'studio/elements'
        elif self.value == EntityType.RoomElement:
            return 'studio/roomelements'
        elif self.value == EntityType.Room:
            return 'studio/rooms'
        raise ValueError(f'Entity type {self.value} is not valid')

    def get_s3_prefix(self, entity_id):
        s3_folder = self.get_s3_folder()
        return f'{s3_folder}/{entity_id}'

    @staticmethod
    def from_s3_file_name(s3_file_name):
        for t in EntityType:
            if t == EntityType.EntityTypeNone:
                continue
            if s3_file_name.startswith(t.get_s3_folder()):
                return t
        raise ValueError(f'S3 folder for {s3_file_name} not recognized')

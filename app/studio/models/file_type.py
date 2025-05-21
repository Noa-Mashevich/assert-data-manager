from enum import IntEnum


class FileType(IntEnum):
    FileTypeNone = 0
    Json = 1
    Dxf = 2
    Rfa = 3
    Jpg = 4
    Png = 5

    def get_content_type(self) -> str:
        if self.value == FileType.Json:
            return 'application/json'
        if self.value == FileType.Dxf:
            return 'application/dxf'
        if self.value == FileType.Rfa:
            return 'application/xml'
        if self.value == FileType.Jpg:
            return 'image/jpeg'
        if self.value == FileType.Png:
            return 'image/png'
        raise ValueError(f'File type {self.value} is not valid')

    def get_extension(self) -> str:
        if self.value == FileType.Json:
            return 'json'
        if self.value == FileType.Dxf:
            return 'dxf'
        if self.value == FileType.Rfa:
            return 'rfa'
        if self.value == FileType.Jpg:
            return 'jpg'
        if self.value == FileType.Png:
            return 'png'
        raise ValueError(f'File type {self.value} is not valid')

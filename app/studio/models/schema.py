import os

from django.db import models
from jsonschema import validate

from studio.file_utils import FileUtils


def get_schema_dir() -> str:
    current_dir = os.path.dirname(__file__)
    return FileUtils.join_path(current_dir, '..', '..', 'data', 'schema')


def get_schema_file_name(version: str) -> str:
    return FileUtils.join_path(get_schema_dir(), f'{version}.json')


class SchemaManager(models.Manager):
    def create_from_version(self, version: str):
        if version not in SchemaManager.get_supported_versions():
            raise ValueError(f'Schema version "{version}" is not supported')

        schema_file_name = get_schema_file_name(version)
        schema_data = FileUtils.read_dict(schema_file_name)
        schema = Schema(version=version, schema_data=schema_data)

        return schema

    @staticmethod
    def get_supported_versions() -> [str]:
        versions = []

        file_names = FileUtils.listdir(get_schema_dir())
        for file_name in file_names:
            base_file_name, ext = os.path.splitext(file_name)
            if ext == '.json':
                versions.append(base_file_name)

        return versions


class Schema(models.Model):
    version = models.CharField(max_length=128)
    schema_data = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    objects = SchemaManager()

    class Meta:
        managed = False

    def validate(self, data: dict) -> (bool, str):
        success = False
        error_message = ''

        try:
            validate(instance=data, schema=self.schema_data)
            success = True
        except Exception as e:
            error_message = (
                f'Failed validating data, version "{self.version}", reason: {e}'
            )

        return success, error_message

import json
import os

from django.db import models


def join_path(*paths) -> str:
    return clean_path(os.path.join(*paths))


def clean_path(path: str) -> str:
    return path.replace('\\', '/')


def read_dict(file_name: str) -> dict:
    with open(file_name, 'rt', encoding='utf-8-sig') as file:
        content = file.read()
        return json.loads(content)


def get_schema_dir() -> str:
    current_dir = os.path.dirname(__file__)
    return join_path(current_dir, '..', '..', 'data', 'schemas')


def get_schema_file_name(version: str) -> str:
    current_dir = os.path.dirname(__file__)
    schemas_dir = join_path(current_dir, '..', '..', 'data', 'schemas')

    return join_path(schemas_dir, f'{version}.json')


class SchemaManager(models.Manager):
    def create(self, version: str):
        if version not in SchemaManager.get_supported_versions():
            raise ValueError(f'Schema version "{version}" is not supported')

        schema_file_name = get_schema_file_name(version)
        schema_data = read_dict(schema_file_name)
        schema = Schema(schema_data=schema_data)

        return schema

    @staticmethod
    def get_supported_versions() -> [str]:
        versions = []
        for _, _, file_names in os.walk(get_schema_dir()):
            for file_name in file_names:
                base_file_name, ext = os.path.splitext(file_name)
                if ext == '.json':
                    versions.append(base_file_name)
        return versions


class Schema(models.Model):
    schema_data: dict
    objects = SchemaManager()

    def __init__(self, *args, schema_data, **kwargs):
        super().__init__(*args, **kwargs)
        self.schema_data = schema_data

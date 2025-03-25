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


class SchemaManager(models.Manager):
    def create(self, version: str):
        current_dir = os.path.dirname(__file__)
        schemas_dir = join_path(current_dir, '..', '..', 'data', 'schemas')

        schema_file_name = join_path(schemas_dir, f'{version}.json')
        if not os.path.isfile(schema_file_name):
            raise FileNotFoundError(f'Schema file does not exist for version "{version}"')

        schema_data = read_dict(schema_file_name)
        schema = Schema(schema_data=schema_data)

        return schema


class Schema(models.Model):
    schema_data: dict
    objects = SchemaManager()

    def __init__(self, *args, schema_data, **kwargs):
        super().__init__(*args, **kwargs)
        self.schema_data = schema_data

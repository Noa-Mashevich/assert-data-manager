import hashlib
import json

from collections import OrderedDict
from django.db import (
    models,
    transaction,
)
from django.utils import timezone

from server.utils import (
    get_object,
    is_migration,
    is_test,
)
from studio.file_utils import FileUtils

from .element import Element
from .element_data_status import ElementDataStatus


class ElementDataManager(models.Manager):
    @transaction.atomic
    def create_versioned_element(self, element):
        element_data_versions = self.model.objects.filter(element=element)
        if len(element_data_versions) == 0:
            version = 1
        else:
            version = element.latest_element_data.version + 1
        element_data = self.model.objects.create(element=element, version=version)
        return element_data

    def create_for_element(self, element):
        from .file_ownership import FileOwnership
        from .file_type import FileType

        element_data = self.model.objects.create_versioned_element(element=element)

        FileOwnership.objects.create_for_entity_data(FileType.Json, element_data)
        FileOwnership.objects.create_for_entity_data(FileType.Dxf, element_data)
        FileOwnership.objects.create_for_entity_data(FileType.Rfa, element_data)
        FileOwnership.objects.create_for_entity_data(FileType.Png, element_data)

        return element_data

    def latest(self, element):
        element_data_versions = self.model.objects.filter(element=element).order_by(
            '-version'
        )

        if len(element_data_versions) == 0:
            raise ValueError(f'Element data not found for element {element.pk}')

        return element_data_versions[0]

    def latest_valid(self, element):
        element_data_versions = self.model.objects.filter(
            element=element, deleted_at__isnull=True
        ).order_by('-version')

        valid_element_data = [
            x for x in element_data_versions if x.status == ElementDataStatus.Complete
        ]

        if len(valid_element_data) == 0:
            return None

        return valid_element_data[0]

    def previous(self, element_data):
        element_data_versions = self.model.objects.filter(
            element=element_data.get_parent()
        )

        previous_version = [
            x for x in element_data_versions if x.version == element_data.version - 1
        ]

        if len(previous_version) != 1:
            return None

        return previous_version[0]

    def versions(self, element):
        return self.model.objects.filter(element=element).order_by('-version')


class ElementData(models.Model):
    element = models.ForeignKey(Element, on_delete=models.RESTRICT)
    version = models.BigIntegerField()
    data = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True)

    objects = ElementDataManager()

    class Meta:
        # newest first
        ordering = ['-version']

    @property
    def status(self) -> int:
        from .file import File

        files = File.objects.filter(ownership__element_data=self)

        if not all([x.exists for x in files]):
            return ElementDataStatus.Incomplete

        return ElementDataStatus.Complete

    @property
    def files(self):
        from .file import File

        return File.objects.filter(ownership__element_data=self)

    @property
    def data_hash(self):
        hash_data = dict(OrderedDict(sorted(self.data.items())))
        content = json.dumps(hash_data).encode('utf-8')
        return hashlib.md5(content).hexdigest()

    def get_data_from_file(self):
        from .file import File
        from .file_type import FileType

        json_files = File.objects.filter(ownership__element_data=self, type=FileType.Json)

        if len(json_files) != 1:
            raise ValueError(
                f'Json file not found for element {self.pk} version = {self.version}'
            )

        json_file = json_files[0]

        if not json_file.exists:
            return {}

        # Note: only for unittesting.
        if is_migration() or is_test():
            return FileUtils.read_test_file_content(json_file.s3_key)

        json_file_s3 = get_object(json_file.s3_key)
        json_data = json.load(json_file_s3['Body'])

        return json_data

    def get_parent(self):
        return self.element

    def track_changes(self):
        from .element_data_change import ElementDataChange

        self.data = self.get_data_from_file()
        self.save(is_updating=True)

        previous_element_data = ElementData.objects.previous(self)

        ElementDataChange.objects.create_from_data_comparison(previous_element_data, self)

    def destroy(self):
        self.deleted_at = timezone.now()
        self.save(is_updating=True)

    def save(self, is_updating=False, *args, **kwargs):
        # Insert a new record when not updating.
        if not is_updating:
            self.pk = None
        super().save(*args, **kwargs)

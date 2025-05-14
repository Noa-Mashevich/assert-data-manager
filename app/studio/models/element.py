from django.db import models
from django.utils import timezone
from enum import IntEnum

from .entity_type import EntityType


class ElementCategory(IntEnum):
    ElementCategoryNone = 0
    Wall = 1
    Floor = 2
    Ceiling = 3
    StructuralFoundation = 4
    Roof = 5
    Door = 6
    Window = 7
    Fascia = 8
    GenericModel = 9
    StructuralColumn = 10
    ElectricalFixture = 11
    MechanicalEquipment = 12
    PlumbingFixture = 13
    LightingFixture = 14
    SpecialtyEquipment = 15
    Casework = 16
    Staircase = 17
    Railing = 18
    Furniture = 19


class ElementManager(models.Manager):
    def create(self, *args, **kwargs):
        instance = super().create(*args, **kwargs)

        from .element_data import ElementData

        ElementData.objects.create_for_element(element=instance)

        return instance


class Element(models.Model):
    name = models.TextField(default='')
    category = models.IntegerField(default=ElementCategory.ElementCategoryNone)

    objects = ElementManager()

    @property
    def latest_element_data(self):
        from .element_data import ElementData

        return ElementData.objects.latest(self)

    @property
    def latest_valid_element_data(self):
        from .element_data import ElementData

        return ElementData.objects.latest_valid(self)

    @property
    def previous_element_data(self):
        from .element_data import ElementData

        return ElementData.objects.previous(self.latest_element_data)

    @property
    def versions(self):
        from .element_data import ElementData

        return ElementData.objects.versions(self)

    def get_entity_type(self):
        return EntityType.Element

    def upgrade(self):
        from .element_data import ElementData

        ElementData.objects.create_for_element(element=self)

    def destroy(self):
        # TODO: figure out if all versions should be destroyed, or just
        #  one specific version.
        element_data = self.latest_element_data
        element_data.deleted_at = timezone.now()
        element_data.save()

        self.save()

from django.db import models
from enum import Enum

from .entity_type import EntityType


class ElementCategory(Enum):
    ElementCategoryNone = ''
    Wall = 'wall'
    Floor = 'floor'
    Ceiling = 'ceiling'
    StructuralFoundation = 'structural_foundation'
    Roof = 'roof'
    Door = 'door'
    Window = 'window'
    Fascia = 'fascia'
    GenericModel = 'generic_model'
    StructuralColumn = 'structural_column'
    ElectricalFixture = 'electrical_fixture'
    MechanicalEquipment = 'mechanical_equipment'
    PlumbingFixture = 'plumbing_fixture'
    LightingFixture = 'lighting_fixture'
    SpecialtyEquipment = 'special_equipment'
    Casework = 'casework'
    Staircase = 'staircase'
    Railing = 'railing'
    Furniture = 'furniture'


class ElementManager(models.Manager):
    def create(self, *args, **kwargs):
        instance = super().create(*args, **kwargs)

        from .element_data import ElementData

        ElementData.objects.create_for_element(element=instance)

        return instance


class Element(models.Model):
    name = models.TextField(default='')
    category = models.TextField(default=ElementCategory.ElementCategoryNone)

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
        versions = self.versions
        for version in versions:
            version.destroy()

        self.save()

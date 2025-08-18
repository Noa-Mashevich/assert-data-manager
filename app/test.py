from studio.models.element import Element
from studio.models.element_data import ElementData
from studio.models.element_data_change import ElementDataChange
import os
import django
from app.studio.models.element import Element

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings.veev-local")
django.setup()

print(Element.objects.count())

e = Element.objects.get(id=4)

# Seed v1 data → creates “added” changes
ed1 = ElementData.objects.get(element=e, version=1)
ed1.data = {"stretch_lines": False, "elements": ["window", "door"]}
ed1.save(is_updating=True)
ElementDataChange.objects.create_from_data_comparison(None, ed1)

# Create v2 with differences → creates patch/major/minor changes
ed2 = ElementData.objects.create(
    element=e,
    version=2,
    data={"stretch_lines": True, "elements": ["window", "door", "column"]},
)
prev = ed1
ElementDataChange.objects.create_from_data_comparison(prev, ed2)

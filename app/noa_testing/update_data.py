import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings.veev-local")
django.setup()

from studio.models.element import Element
from studio.models.element_data import ElementData
from studio.models.element_data_change import ElementDataChange

# Get element 8
e = Element.objects.get(id=8)

# Update version 3 data to something different
ed3 = ElementData.objects.get(element=e, version=3)
ed3.data = {
    "stretch_lines": True,
    "elements": ["window", "door", "column", "beam"],
    "meta": {"color": "purple", "height": 250, "width": 120},
    "new_feature": True,
}
ed3.save()

print("Updated version 3 data")
print("Now create version 4 to see the changes!")

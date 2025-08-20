#!/usr/bin/env python
import os
import sys
import django

# Add the app directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings.e2e-local')
django.setup()

from studio.models.element import Element
from studio.models.element_data import ElementData


def create_new_version():
    """Create a new version for element data"""

    # Get the element with ID 1
    try:
        element = Element.objects.get(id=1)
        print(f"Found element: {element.name}")
    except Element.DoesNotExist:
        print("Element with ID 1 not found!")
        return

    # Check current versions
    current_versions = ElementData.objects.filter(element=element).order_by('-version')
    print(f"Current versions: {[v.version for v in current_versions]}")

    # Create a new version using the proper method
    print("Creating new version...")
    element.upgrade()

    # Check the new version
    new_version = element.latest_element_data
    print(f"New version created: {new_version.version}")
    print(f"New version ID: {new_version.id}")
    print(f"New version data: {new_version.data}")

    # Show all versions now
    all_versions = ElementData.objects.filter(element=element).order_by('-version')
    print(f"All versions after upgrade: {[v.version for v in all_versions]}")

    print("New version creation completed!")


if __name__ == "__main__":
    create_new_version()

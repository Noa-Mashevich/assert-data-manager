#!/usr/bin/env python
"""
Simple test script that only imports necessary models to avoid AWS issues.
Run with: python simple_test.py
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings.veev-local')
django.setup()

# Only import the specific models we need (avoid AWS-dependent ones)
from django.db import models
from studio.models.element import Element
from studio.models.element_data import ElementData
from studio.models.element_data_change import ElementDataChange


def create_test_data():
    """Create test element versions and changes."""
    try:
        # Get element 10 (or create one if it doesn't exist)
        e, created = Element.objects.get_or_create(
            id=10, defaults={'name': 'Test Element', 'category': 'door'}
        )

        if created:
            print(f"Created new element: {e.name} (ID: {e.id})")
        else:
            print(f"Using existing element: {e.name} (ID: {e.id})")

        # Create version 1 with initial data
        ed1, created = ElementData.objects.get_or_create(
            element=e,
            version=1,
            defaults={
                'data': {
                    "stretch_lines": False,
                    "elements": ["window", "door"],
                    "meta": {"color": "red", "height": 200},
                }
            },
        )

        if created:
            print("Created version 1")
        else:
            print("Version 1 already exists")

        # Generate changes for version 1
        ElementDataChange.objects.create_from_data_comparison(None, ed1)
        print("Generated changes for version 1")

        # Create version 2 with different data
        ed2, created = ElementData.objects.get_or_create(
            element=e,
            version=2,
            defaults={
                'data': {
                    "stretch_lines": True,
                    "elements": ["window", "door", "column"],
                    "meta": {"color": "blue", "height": 210},
                }
            },
        )

        if created:
            print("Created version 2")
        else:
            print("Version 2 already exists")

        # Generate changes for version 2
        ElementDataChange.objects.create_from_data_comparison(ed1, ed2)
        print("Generated changes for version 2")

        print(f"\nSuccess! Element {e.id} now has 2 versions with change tracking.")
        print(f"Check the API:")
        print(f"  GET http://127.0.0.1:8000/studio/element/{e.id}/version/1/")
        print(f"  GET http://127.0.0.1:8000/studio/element/{e.id}/version/2/")
        print(f"  GET http://127.0.0.1:8000/studio/element/{e.id}/version/1/changes/")
        print(f"  GET http://127.0.0.1:8000/studio/element/{e.id}/version/2/changes/")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    create_test_data()

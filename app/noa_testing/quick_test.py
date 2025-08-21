#!/usr/bin/env python
"""
Quick test script - run this to create test data easily.
Usage: python quick_test.py
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings.veev-local')
django.setup()

from studio.models.element import Element
from studio.models.element_data import ElementData
from studio.models.element_data_change import ElementDataChange


def quick_test():
    """Quickly create test data for API testing."""

    # Create or get element
    e, created = Element.objects.get_or_create(
        id=99, defaults={'name': 'Quick Test Element', 'category': 'window'}
    )

    print(f"Using element: {e.name} (ID: {e.id})")

    # Create version 1
    ed1, created = ElementData.objects.get_or_create(
        element=e,
        version=1,
        defaults={
            'data': {
                "stretch_lines": False,
                "elements": ["window"],
                "meta": {"color": "red", "height": 100},
            }
        },
    )

    # Create version 2 with changes
    ed2, created = ElementData.objects.get_or_create(
        element=e,
        version=2,
        defaults={
            'data': {
                "stretch_lines": True,
                "elements": ["window", "door"],
                "meta": {"color": "blue", "height": 150},
            }
        },
    )

    # Generate changes
    ElementDataChange.objects.create_from_data_comparison(None, ed1)
    ElementDataChange.objects.create_from_data_comparison(ed1, ed2)

    print("✅ Test data created!")
    print(f"Test these URLs:")
    print(f"  GET http://127.0.0.1:8000/studio/element/{e.id}/version/1/changes/")
    print(f"  GET http://127.0.0.1:8000/studio/element/{e.id}/version/2/changes/")


if __name__ == "__main__":
    quick_test()

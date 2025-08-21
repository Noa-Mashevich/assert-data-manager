#!/usr/bin/env python
"""
Test upgrade process to identify duplicates.
Usage: python test_upgrade.py
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings.veev-local')
django.setup()

from studio.models.element import Element
from studio.models.element_data import ElementData
from studio.models.element_data_change import ElementDataChange

def test_upgrade():
    print("🧪 Testing upgrade process...")
    
    # Get element 1
    element = Element.objects.get(id=1)
    print(f"📋 Element: {element.name} (ID: {element.id})")
    
    # Check current state
    print(f"\n📊 BEFORE upgrade:")
    all_data = ElementData.objects.filter(element=element).order_by('version')
    for data in all_data:
        print(f"  - Version {data.version} (ID {data.id}): {data.data}")
    
    # Get current latest version
    current_latest = element.latest_element_data
    print(f"  - Current latest: Version {current_latest.version} (ID {current_latest.id})")
    
    # Perform upgrade
    print(f"\n🔄 Performing upgrade...")
    element.upgrade()
    
    # Check after upgrade
    print(f"\n📊 AFTER upgrade:")
    all_data = ElementData.objects.filter(element=element).order_by('version')
    for data in all_data:
        print(f"  - Version {data.version} (ID {data.id}): {data.data}")
    
    # Get new latest version
    new_latest = element.latest_element_data
    print(f"  - New latest: Version {new_latest.version} (ID {new_latest.id})")
    
    # Check for duplicates
    print(f"\n🔍 Checking for duplicates:")
    for version in range(1, new_latest.version + 1):
        version_records = ElementData.objects.filter(element=element, version=version)
        if version_records.count() > 1:
            print(f"  ⚠️ Version {version}: {version_records.count()} records!")
            for record in version_records:
                print(f"    - ID {record.id}: {record.data}")
        else:
            print(f"  ✅ Version {version}: {version_records.count()} record")

if __name__ == "__main__":
    test_upgrade()

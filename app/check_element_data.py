#!/usr/bin/env python
"""
Check Element Data Status
"""

import os
import sys
import django

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings.e2e-local')
django.setup()

from studio.models.element import Element
from studio.models.element_data import ElementData
from studio.models.data_status import DataStatus


def check_element_data(element_id):
    """Check element data status"""

    try:
        element = Element.objects.get(pk=element_id)
        print(f"🔍 Element ID {element_id}: {element.name} ({element.category})")
        print("=" * 50)

        # Check if element has any ElementData records
        element_data_records = ElementData.objects.filter(element=element)
        print(f"📊 Total ElementData records: {element_data_records.count()}")

        if element_data_records.count() == 0:
            print("❌ No ElementData records found!")
            print("💡 Solution: Use the upgrade_with_data endpoint to create ElementData")
            return

        # Check each ElementData record
        for i, element_data in enumerate(element_data_records.order_by('-version')):
            print(f"\n📋 Version {element_data.version}:")
            print(
                f"   - Status: {element_data.status} ({DataStatus(element_data.status).name})"
            )
            print(f"   - Current file count: {element_data.current_file_count}")
            print(f"   - Required file count: {element_data.required_file_count}")
            print(f"   - Data: {element_data.data}")
            print(f"   - Created: {element_data.created_at}")
            print(f"   - Deleted: {element_data.deleted_at}")

        # Check latest_valid_element_data
        print(f"\n🎯 Latest valid element data:")
        latest_valid = element.latest_valid_element_data
        if latest_valid:
            print(f"   ✅ Found: Version {latest_valid.version}")
            print(f"   - Status: {latest_valid.status}")
            print(f"   - Data: {latest_valid.data}")
        else:
            print("   ❌ No valid element data found!")
            print("   💡 This is why element_data is null in the API response")

            # Check why no valid data
            incomplete_records = [
                ed for ed in element_data_records if ed.status == DataStatus.Incomplete
            ]
            if incomplete_records:
                print(f"   📝 Found {len(incomplete_records)} incomplete records:")
                for ed in incomplete_records:
                    print(
                        f"      - Version {ed.version}: {ed.current_file_count}/{ed.required_file_count} files"
                    )

        # Check latest_element_data (any status)
        print(f"\n📈 Latest element data (any status):")
        try:
            latest = element.latest_element_data
            print(f"   ✅ Found: Version {latest.version}")
            print(f"   - Status: {latest.status}")
            print(f"   - Data: {latest.data}")
        except ValueError as e:
            print(f"   ❌ Error: {e}")

    except Element.DoesNotExist:
        print(f"❌ Element with ID {element_id} not found!")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    element_id = 4  # Change this to your element ID
    check_element_data(element_id)

#!/usr/bin/env python
"""
Debug Element Upgrade Process
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
from studio.models.element_data_change import ElementDataChange


def debug_upgrade_process(element_id):
    """Debug the upgrade process step by step"""

    try:
        print(f"🔍 Debugging upgrade process for Element ID {element_id}")
        print("=" * 60)

        # Step 1: Get the element
        element = Element.objects.get(pk=element_id)
        print(f"✅ Step 1: Found element - {element.name} ({element.category})")

        # Step 2: Check current ElementData records
        current_records = ElementData.objects.filter(element=element)
        print(f"📊 Step 2: Current ElementData records: {current_records.count()}")

        # Step 3: Test the upgrade method
        print("🔄 Step 3: Testing element.upgrade()...")
        try:
            element.upgrade()
            print("✅ element.upgrade() completed successfully")
        except Exception as e:
            print(f"❌ element.upgrade() failed: {e}")
            return

        # Step 4: Check if new ElementData was created
        new_records = ElementData.objects.filter(element=element)
        print(f"📊 Step 4: ElementData records after upgrade: {new_records.count()}")

        # Step 5: Get the latest element data
        print("🔍 Step 5: Getting latest_element_data...")
        try:
            latest_data = element.latest_element_data
            print(f"✅ Latest element data: Version {latest_data.version}")
            print(f"   - Status: {latest_data.status}")
            print(f"   - Data: {latest_data.data}")
        except Exception as e:
            print(f"❌ Failed to get latest_element_data: {e}")
            return

        # Step 6: Test setting data
        test_data = {
            "stretch_lines": True,
            "elements": ["door"],
            "meta": {"color": "blue", "height": 250, "width": 150},
            "new_feature": True,
        }

        print("📝 Step 6: Testing data assignment...")
        try:
            latest_data.data = test_data
            latest_data.save(is_updating=True)
            print("✅ Data assignment completed successfully")
        except Exception as e:
            print(f"❌ Data assignment failed: {e}")
            return

        # Step 7: Test change tracking
        print("🔄 Step 7: Testing change tracking...")
        try:
            previous_version = element.previous_element_data
            print(f"✅ Previous version: {previous_version}")

            ElementDataChange.objects.create_from_data_comparison(
                previous_version, latest_data
            )
            print("✅ Change tracking completed successfully")
        except Exception as e:
            print(f"❌ Change tracking failed: {e}")
            return

        # Step 8: Test serializer
        print("📋 Step 8: Testing serializer...")
        try:
            from studio.serializers.element import ElementUpgradeSerializer

            serializer = ElementUpgradeSerializer(instance=element)
            result = serializer.data
            print("✅ Serializer completed successfully")
            print(f"   - Result keys: {list(result.keys())}")
            if 'element_data' in result:
                print(f"   - Element data: {result['element_data']}")
        except Exception as e:
            print(f"❌ Serializer failed: {e}")
            return

        print("\n🎉 All steps completed successfully!")

    except Element.DoesNotExist:
        print(f"❌ Element with ID {element_id} not found!")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    element_id = 5  # Change this to your element ID
    debug_upgrade_process(element_id)

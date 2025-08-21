#!/usr/bin/env python
"""
Simple Element Upgrade Test
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


def simple_upgrade_test(element_id):
    """Simple test to create ElementData without complex logic"""

    try:
        print(f"🔍 Simple upgrade test for Element ID {element_id}")
        print("=" * 50)

        # Step 1: Get the element
        element = Element.objects.get(pk=element_id)
        print(f"✅ Found element: {element.name}")

        # Step 2: Create ElementData directly
        print("🔄 Creating ElementData directly...")
        element_data = ElementData.objects.create(
            element=element,
            version=1,
            data={
                "stretch_lines": True,
                "elements": ["door"],
                "meta": {"color": "blue", "height": 250, "width": 150},
                "new_feature": True,
            },
        )
        print(
            f"✅ Created ElementData: ID {element_data.id}, Version {element_data.version}"
        )

        # Step 3: Test getting latest_element_data
        print("🔍 Testing latest_element_data...")
        try:
            latest = element.latest_element_data
            print(f"✅ Latest element data: Version {latest.version}")
            print(f"   - Data: {latest.data}")
        except Exception as e:
            print(f"❌ Failed to get latest_element_data: {e}")

        # Step 4: Test serializer
        print("📋 Testing serializer...")
        try:
            from studio.serializers.element import ElementUpgradeSerializer

            serializer = ElementUpgradeSerializer(instance=element)
            result = serializer.data
            print("✅ Serializer worked!")
            print(f"   - Result: {result}")
        except Exception as e:
            print(f"❌ Serializer failed: {e}")
            import traceback

            traceback.print_exc()

        print("\n🎉 Simple test completed!")

    except Element.DoesNotExist:
        print(f"❌ Element with ID {element_id} not found!")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    element_id = 5  # Change this to your element ID
    simple_upgrade_test(element_id)

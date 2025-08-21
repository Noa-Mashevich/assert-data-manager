#!/usr/bin/env python
import os
import sys
import django
import requests
import json

# Add the app directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings.e2e-local')
django.setup()


def test_upgrade_with_data_endpoint():
    """Test the new upgrade_with_data endpoint"""

    # API endpoint URL (assuming Django server runs on localhost:8000)
    base_url = "http://localhost:8000"
    element_id = 1

    # Test data to send
    test_data = {
        "data": {
            "stretch_limit": 150,
            "material": "steel",
            "dimensions": {"width": 100, "height": 200, "depth": 50},
        },
        "additional_info": {
            "manufacturer": "ABC Corp",
            "model_number": "EL-2024-001",
            "installation_date": "2024-01-15",
            "warranty_expiry": "2026-01-15",
            "maintenance_notes": "Requires annual inspection",
        },
    }

    # Make the API call
    url = f"{base_url}/studio/element/{element_id}/upgrade_with_data/"

    try:
        print(f"Making POST request to: {url}")
        print(f"Request data: {json.dumps(test_data, indent=2)}")

        response = requests.post(
            url, json=test_data, headers={'Content-Type': 'application/json'}
        )

        print(f"Response status code: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print("Success! New version created:")
            print(json.dumps(result, indent=2))

            # Extract the new version info
            element_data = result.get('element_data', {})
            print(f"\nNew version details:")
            print(f"  Version: {element_data.get('version')}")
            print(f"  ID: {element_data.get('id')}")
            print(f"  Data: {element_data.get('data')}")

        else:
            print(f"Error: {response.text}")

    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the server.")
        print("Make sure Django server is running on localhost:8000")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    test_upgrade_with_data_endpoint()

#!/usr/bin/env python3
"""
Quick test script for Milestone 5 Departments API
"""

import requests
import json

def test_api():
    base_url = "http://localhost:5000"
    
    print("🧪 Testing Milestone 5: Departments API")
    print("=" * 50)
    
    # Test 1: Get all departments
    print("\n1. Testing GET /api/departments")
    try:
        response = requests.get(f"{base_url}/api/departments")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("✅ Success! Response:")
            print(json.dumps(data, indent=2))
        else:
            print(f"❌ Failed: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 2: Get specific department
    print("\n2. Testing GET /api/departments/1")
    try:
        response = requests.get(f"{base_url}/api/departments/1")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("✅ Success! Response:")
            print(json.dumps(data, indent=2))
        else:
            print(f"❌ Failed: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: Get products in department
    print("\n3. Testing GET /api/departments/1/products?limit=3")
    try:
        response = requests.get(f"{base_url}/api/departments/1/products?limit=3")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("✅ Success! Response structure:")
            print(f"  Department: {data.get('department', 'N/A')}")
            print(f"  Products count: {len(data.get('products', []))}")
            print(f"  Total count: {data.get('pagination', {}).get('total_count', 'N/A')}")
            print("\nSample product:")
            if data.get('products'):
                print(json.dumps(data['products'][0], indent=2))
        else:
            print(f"❌ Failed: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 4: Test error handling
    print("\n4. Testing error handling - Invalid department ID")
    try:
        response = requests.get(f"{base_url}/api/departments/999")
        print(f"Status: {response.status_code}")
        if response.status_code == 404:
            print("✅ Correctly returns 404 for invalid department")
        else:
            print(f"❌ Expected 404, got {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n🎉 Testing complete!")

if __name__ == "__main__":
    test_api() 
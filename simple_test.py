#!/usr/bin/env python3
"""
Simple test for Milestone 5 Departments API using built-in libraries
"""

import urllib.request
import json

def test_api():
    base_url = "http://localhost:5000"
    
    print("🧪 Testing Milestone 5: Departments API")
    print("=" * 50)
    
    # Test 1: Get all departments
    print("\n1. Testing GET /api/departments")
    try:
        with urllib.request.urlopen(f"{base_url}/api/departments") as response:
            data = json.loads(response.read().decode())
            print("✅ Success! Status: 200")
            print("Response:")
            print(json.dumps(data, indent=2))
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 2: Get specific department
    print("\n2. Testing GET /api/departments/1")
    try:
        with urllib.request.urlopen(f"{base_url}/api/departments/1") as response:
            data = json.loads(response.read().decode())
            print("✅ Success! Status: 200")
            print("Response:")
            print(json.dumps(data, indent=2))
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: Get products in department
    print("\n3. Testing GET /api/departments/1/products?limit=3")
    try:
        with urllib.request.urlopen(f"{base_url}/api/departments/1/products?limit=3") as response:
            data = json.loads(response.read().decode())
            print("✅ Success! Status: 200")
            print("Response structure:")
            print(f"  Department: {data.get('department', 'N/A')}")
            print(f"  Products count: {len(data.get('products', []))}")
            print(f"  Total count: {data.get('pagination', {}).get('total_count', 'N/A')}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 4: Test error handling
    print("\n4. Testing error handling - Invalid department ID")
    try:
        with urllib.request.urlopen(f"{base_url}/api/departments/999") as response:
            print("❌ Expected 404, but got success")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print("✅ Correctly returns 404 for invalid department")
        else:
            print(f"❌ Expected 404, got {e.code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n🎉 Testing complete!")

if __name__ == "__main__":
    test_api() 
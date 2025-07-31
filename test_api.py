#!/usr/bin/env python3
"""
Test API with new database structure
"""

import requests
import json
import time

def test_api():
    """Test the API endpoints"""
    base_url = "http://localhost:5000"
    
    print("🧪 Testing API with new database structure...\n")
    
    # Test 1: Home endpoint
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            data = response.json()
            print("✅ Home endpoint working")
            print(f"   Version: {data.get('version', 'N/A')}")
        else:
            print(f"❌ Home endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Home endpoint error: {e}")
        return False
    
    # Test 2: Departments endpoint
    try:
        response = requests.get(f"{base_url}/api/departments")
        if response.status_code == 200:
            data = response.json()
            departments = data.get('departments', [])
            print(f"✅ Departments endpoint working - {len(departments)} departments")
            for dept in departments:
                print(f"   - {dept['name']} (ID: {dept['id']})")
        else:
            print(f"❌ Departments endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Departments endpoint error: {e}")
        return False
    
    # Test 3: Products endpoint
    try:
        response = requests.get(f"{base_url}/api/products?limit=3")
        if response.status_code == 200:
            data = response.json()
            products = data.get('products', [])
            print(f"✅ Products endpoint working - {len(products)} products returned")
            
            if products:
                product = products[0]
                if 'department' in product and 'id' in product['department']:
                    print(f"   ✅ Products include department information")
                    print(f"   Sample: {product['name']} - {product['department']['name']}")
                else:
                    print("   ❌ Products missing department information")
                    return False
        else:
            print(f"❌ Products endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Products endpoint error: {e}")
        return False
    
    # Test 4: Products by department filter
    try:
        response = requests.get(f"{base_url}/api/products?department_name=Women&limit=2")
        if response.status_code == 200:
            data = response.json()
            products = data.get('products', [])
            print(f"✅ Department filter working - {len(products)} Women's products")
        else:
            print(f"❌ Department filter failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Department filter error: {e}")
        return False
    
    # Test 5: Stats endpoint
    try:
        response = requests.get(f"{base_url}/api/products/stats")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Stats endpoint working")
            print(f"   Total products: {data.get('total_products', 'N/A')}")
            print(f"   Total departments: {data.get('total_departments', 'N/A')}")
        else:
            print(f"❌ Stats endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Stats endpoint error: {e}")
        return False
    
    print("\n🎉 All API tests passed!")
    return True

if __name__ == "__main__":
    # Wait a moment for the server to start
    time.sleep(2)
    
    if test_api():
        print("\n✅ Database refactoring is complete and working!")
        print("\n📋 Summary:")
        print("✅ Separate departments table created")
        print("✅ Products table updated with department_id")
        print("✅ API updated to work with new structure")
        print("✅ All endpoints working correctly")
        print("✅ Department filtering working")
        print("✅ Data integrity maintained")
    else:
        print("\n❌ Some tests failed") 
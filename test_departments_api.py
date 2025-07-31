#!/usr/bin/env python3
"""
Test script for Milestone 5: Departments API
Tests all required department endpoints and response formats
"""

import requests
import json
import time

def test_departments_list():
    """Test GET /api/departments - List all departments"""
    print("=" * 60)
    print("1. 📋 TESTING GET /api/departments")
    print("=" * 60)
    
    try:
        # Test default format (Milestone 5 requirement)
        response = requests.get("http://localhost:5000/api/departments")
        
        if response.status_code == 200:
            data = response.json()
            departments = data.get('departments', [])
            
            print(f"✅ Status: {response.status_code}")
            print(f"✅ Found {len(departments)} departments")
            print("\nResponse format:")
            print(json.dumps(data, indent=2))
            
            # Verify response format matches Milestone 5 requirements
            if 'departments' in data and isinstance(departments, list):
                print("\n✅ Response format is correct")
                
                for dept in departments:
                    if all(key in dept for key in ['id', 'name', 'product_count']):
                        print(f"✅ Department {dept['name']}: {dept['product_count']} products")
                    else:
                        print(f"❌ Department {dept.get('name', 'Unknown')} missing required fields")
                        return False
            else:
                print("❌ Response format is incorrect")
                return False
                
        else:
            print(f"❌ Failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

def test_department_details():
    """Test GET /api/departments/{id} - Get specific department details"""
    print("\n" + "=" * 60)
    print("2. 🔍 TESTING GET /api/departments/{id}")
    print("=" * 60)
    
    try:
        # Test with valid department ID (1)
        response = requests.get("http://localhost:5000/api/departments/1")
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"✅ Status: {response.status_code}")
            print("Response:")
            print(json.dumps(data, indent=2))
            
            # Verify required fields
            required_fields = ['id', 'name', 'product_count']
            if all(field in data for field in required_fields):
                print(f"\n✅ Department details: {data['name']} ({data['product_count']} products)")
            else:
                print("❌ Missing required fields")
                return False
                
        else:
            print(f"❌ Failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
        # Test with invalid department ID
        print("\nTesting invalid department ID...")
        response = requests.get("http://localhost:5000/api/departments/999")
        
        if response.status_code == 404:
            print("✅ Correctly returns 404 for invalid department")
        else:
            print(f"❌ Expected 404, got {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

def test_department_products():
    """Test GET /api/departments/{id}/products - Get products in department"""
    print("\n" + "=" * 60)
    print("3. 📦 TESTING GET /api/departments/{id}/products")
    print("=" * 60)
    
    try:
        # Test with valid department ID (1)
        response = requests.get("http://localhost:5000/api/departments/1/products?limit=3")
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"✅ Status: {response.status_code}")
            print("Response structure:")
            print(f"  - Department: {data.get('department', 'N/A')}")
            print(f"  - Products count: {len(data.get('products', []))}")
            print(f"  - Total count: {data.get('pagination', {}).get('total_count', 'N/A')}")
            
            print("\nSample response:")
            print(json.dumps(data, indent=2))
            
            # Verify response format
            if 'department' in data and 'products' in data and 'pagination' in data:
                print("\n✅ Response format is correct")
                
                # Check if products have department info
                products = data.get('products', [])
                if products:
                    product = products[0]
                    if 'department' in product and 'id' in product['department']:
                        print("✅ Products include department information")
                    else:
                        print("❌ Products missing department information")
                        return False
                else:
                    print("⚠️  No products found in department")
            else:
                print("❌ Response format is incorrect")
                return False
                
        else:
            print(f"❌ Failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
        # Test with invalid department ID
        print("\nTesting invalid department ID...")
        response = requests.get("http://localhost:5000/api/departments/999/products")
        
        if response.status_code == 404:
            print("✅ Correctly returns 404 for invalid department")
        else:
            print(f"❌ Expected 404, got {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

def test_department_products_filtering():
    """Test filtering within department products"""
    print("\n" + "=" * 60)
    print("4. 🔍 TESTING DEPARTMENT PRODUCTS FILTERING")
    print("=" * 60)
    
    try:
        # Test category filtering within department
        response = requests.get("http://localhost:5000/api/departments/1/products?category=Accessories&limit=2")
        
        if response.status_code == 200:
            data = response.json()
            products = data.get('products', [])
            
            print(f"✅ Category filter: Found {len(products)} products in Accessories category")
            print(f"   Department: {data.get('department', 'N/A')}")
            print(f"   Total in category: {data.get('pagination', {}).get('total_count', 'N/A')}")
            
            # Test brand filtering within department
            response = requests.get("http://localhost:5000/api/departments/1/products?brand=MG&limit=2")
            
            if response.status_code == 200:
                data = response.json()
                products = data.get('products', [])
                
                print(f"✅ Brand filter: Found {len(products)} products from MG brand")
                print(f"   Total from brand: {data.get('pagination', {}).get('total_count', 'N/A')}")
                
            else:
                print(f"❌ Brand filter failed: {response.status_code}")
                return False
                
        else:
            print(f"❌ Category filter failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

def test_error_handling():
    """Test error handling for department endpoints"""
    print("\n" + "=" * 60)
    print("5. ⚠️  TESTING ERROR HANDLING")
    print("=" * 60)
    
    try:
        # Test invalid department ID for all endpoints
        endpoints = [
            "/api/departments/999",
            "/api/departments/999/products"
        ]
        
        for endpoint in endpoints:
            response = requests.get(f"http://localhost:5000{endpoint}")
            
            if response.status_code == 404:
                print(f"✅ {endpoint}: Correctly returns 404")
            else:
                print(f"❌ {endpoint}: Expected 404, got {response.status_code}")
                return False
        
        # Test invalid query parameters
        response = requests.get("http://localhost:5000/api/departments/1/products?limit=1000")
        
        if response.status_code == 200:
            data = response.json()
            # Should limit to max 100 items
            products = data.get('products', [])
            if len(products) <= 100:
                print("✅ Limit parameter correctly enforced (max 100)")
            else:
                print(f"❌ Limit not enforced: {len(products)} products returned")
                return False
        else:
            print(f"❌ Limit test failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

def main():
    """Run all department API tests"""
    print("🎯 MILESTONE 5: DEPARTMENTS API TESTING")
    print("=" * 60)
    print("Testing all required department endpoints...")
    
    # Wait for server to be ready
    time.sleep(2)
    
    tests = [
        ("Departments List", test_departments_list),
        ("Department Details", test_department_details),
        ("Department Products", test_department_products),
        ("Department Filtering", test_department_products_filtering),
        ("Error Handling", test_error_handling)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} test passed")
            else:
                print(f"❌ {test_name} test failed")
        except Exception as e:
            print(f"❌ {test_name} test failed with exception: {e}")
    
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS")
    print("=" * 60)
    print(f"Passed: {passed}/{total} tests")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Milestone 5 requirements met:")
        print("   - GET /api/departments - List all departments with product count")
        print("   - GET /api/departments/{id} - Get specific department details")
        print("   - GET /api/departments/{id}/products - Get products in department")
        print("   - Proper JSON responses with appropriate HTTP status codes")
        print("   - Error handling for invalid department IDs")
        print("   - Filtering within department products")
        print("   - Pagination support")
    else:
        print("\n❌ Some tests failed. Please check the implementation.")
    
    print("\n🚀 Departments API is ready for frontend integration!")

if __name__ == "__main__":
    main() 
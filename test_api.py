#!/usr/bin/env python3
"""
Test script for the Products REST API
Tests all endpoints and verifies responses
"""

import requests
import json
import time

# API base URL
BASE_URL = "http://localhost:5000"

def test_endpoint(endpoint, description):
    """Test an API endpoint and print results"""
    print(f"\n{'='*60}")
    print(f"Testing: {description}")
    print(f"Endpoint: {endpoint}")
    print(f"{'='*60}")
    
    try:
        response = requests.get(f"{BASE_URL}{endpoint}")
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            if isinstance(data, dict):
                if 'products' in data:
                    print(f"✅ Success! Found {len(data['products'])} products")
                    if 'pagination' in data:
                        pagination = data['pagination']
                        print(f"   Page: {pagination['page']}/{pagination['total_pages']}")
                        print(f"   Total: {pagination['total_count']} products")
                    
                    # Show first product as sample
                    if data['products']:
                        product = data['products'][0]
                        print(f"   Sample Product: {product['name'][:50]}...")
                        print(f"   Brand: {product['brand']}, Price: ${product['retail_price']}")
                
                elif 'categories' in data:
                    print(f"✅ Success! Found {len(data['categories'])} categories")
                    print(f"   Sample categories: {', '.join(data['categories'][:5])}")
                
                elif 'brands' in data:
                    print(f"✅ Success! Found {len(data['brands'])} brands")
                    print(f"   Sample brands: {', '.join(data['brands'][:5])}")
                
                elif 'total_products' in data:
                    print(f"✅ Success! Statistics retrieved")
                    print(f"   Total Products: {data['total_products']}")
                    print(f"   Total Categories: {data['total_categories']}")
                    print(f"   Total Brands: {data['total_brands']}")
                    print(f"   Average Price: ${data['price_stats']['average_price']}")
                
                else:
                    print(f"✅ Success! Response received")
                    print(f"   Response keys: {list(data.keys())}")
            
            else:
                print(f"✅ Success! Response received")
                print(f"   Response type: {type(data)}")
        
        else:
            print(f"❌ Error: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error message: {error_data.get('error', 'Unknown error')}")
            except:
                print(f"   Response text: {response.text[:100]}...")
        
        return response.status_code == 200
        
    except requests.exceptions.ConnectionError:
        print(f"❌ Connection Error: Could not connect to {BASE_URL}")
        print("   Make sure the Flask API is running (python app.py)")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_specific_product():
    """Test getting a specific product by ID"""
    print(f"\n{'='*60}")
    print("Testing: Get Specific Product by ID")
    print(f"{'='*60}")
    
    # First get a list of products to find an ID
    try:
        response = requests.get(f"{BASE_URL}/api/products?limit=1")
        if response.status_code == 200:
            data = response.json()
            if data['products']:
                product_id = data['products'][0]['id']
                
                # Test getting this specific product
                product_response = requests.get(f"{BASE_URL}/api/products/{product_id}")
                
                print(f"Testing product ID: {product_id}")
                print(f"Status Code: {product_response.status_code}")
                
                if product_response.status_code == 200:
                    product = product_response.json()
                    print(f"✅ Success! Product found")
                    print(f"   Name: {product['name']}")
                    print(f"   Brand: {product['brand']}")
                    print(f"   Price: ${product['retail_price']}")
                    print(f"   Profit Margin: ${product['profit_margin']} ({product['profit_margin_percentage']}%)")
                    return True
                else:
                    print(f"❌ Error: {product_response.status_code}")
                    return False
            else:
                print("❌ No products found to test with")
                return False
        else:
            print(f"❌ Error getting products list: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_error_cases():
    """Test error handling"""
    print(f"\n{'='*60}")
    print("Testing: Error Cases")
    print(f"{'='*60}")
    
    # Test non-existent product
    try:
        response = requests.get(f"{BASE_URL}/api/products/nonexistent123")
        print(f"Non-existent product test:")
        print(f"   Status Code: {response.status_code}")
        if response.status_code == 404:
            print("   ✅ Correctly returns 404 for non-existent product")
        else:
            print("   ❌ Expected 404 but got different status")
        
        # Test invalid endpoint
        response = requests.get(f"{BASE_URL}/api/invalid")
        print(f"Invalid endpoint test:")
        print(f"   Status Code: {response.status_code}")
        if response.status_code == 404:
            print("   ✅ Correctly returns 404 for invalid endpoint")
        else:
            print("   ❌ Expected 404 but got different status")
            
    except Exception as e:
        print(f"❌ Error testing error cases: {e}")

def main():
    """Run all API tests"""
    print("🚀 Products REST API Test Suite")
    print("Make sure the API is running: python app.py")
    print("\nStarting tests in 3 seconds...")
    time.sleep(3)
    
    tests = [
        ("/", "Home endpoint with API documentation"),
        ("/api/products", "List all products (first page)"),
        ("/api/products?page=2&limit=5", "List products with pagination"),
        ("/api/products?category=Jeans", "Filter products by category"),
        ("/api/products?brand=Allegra%20K", "Filter products by brand"),
        ("/api/products?department=Women", "Filter products by department"),
        ("/api/products/stats", "Get product statistics"),
        ("/api/categories", "Get all categories"),
        ("/api/brands", "Get all brands"),
    ]
    
    passed = 0
    total = len(tests)
    
    for endpoint, description in tests:
        if test_endpoint(endpoint, description):
            passed += 1
    
    # Test specific product
    if test_specific_product():
        passed += 1
    total += 1
    
    # Test error cases
    test_error_cases()
    
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Passed: {passed}/{total} tests")
    
    if passed == total:
        print("🎉 All tests passed! API is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the API implementation.")
    
    print(f"\nAPI is running at: {BASE_URL}")
    print("You can test manually in your browser or with tools like Postman!")

if __name__ == "__main__":
    main() 
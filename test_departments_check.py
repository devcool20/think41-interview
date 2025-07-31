#!/usr/bin/env python3
"""
Test the departments API to see what departments actually exist
"""

import requests
import json

def test_departments_api():
    """Test the departments API"""
    try:
        # Test the departments endpoint
        response = requests.get('http://localhost:5000/api/departments')
        
        if response.status_code == 200:
            data = response.json()
            departments = data.get('departments', [])
            
            print("🏪 DEPARTMENTS FROM API:")
            print("=" * 50)
            
            for dept in departments:
                print(f"📦 {dept['name']} (ID: {dept['id']}) - {dept['product_count']:,} products")
            
            print(f"\n📊 Total Departments: {len(departments)}")
            
            # Test a specific department
            if departments:
                first_dept = departments[0]
                print(f"\n🔍 Testing department: {first_dept['name']}")
                
                dept_response = requests.get(f'http://localhost:5000/api/departments/{first_dept["id"]}/products?limit=3')
                if dept_response.status_code == 200:
                    dept_data = dept_response.json()
                    print(f"   Department: {dept_data['department']}")
                    print(f"   Products found: {len(dept_data['products'])}")
                    
                    if dept_data['products']:
                        sample_product = dept_data['products'][0]
                        print(f"   Sample product: {sample_product['name']}")
                        print(f"   Product category: {sample_product['category']}")
                        print(f"   Product department: {sample_product['department']['name']}")
            
        else:
            print(f"❌ API Error: {response.status_code}")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API. Make sure the Flask server is running on port 5000.")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_departments_api() 
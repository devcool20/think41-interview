#!/usr/bin/env python3
"""
Test script for database migration and refactoring
Tests the new database structure with departments table
"""

import sqlite3
import json
import requests
import time
from migration_departments import DepartmentMigration

def test_migration():
    """Test the database migration process"""
    print("🧪 Testing Database Migration...")
    
    # Run migration
    migration = DepartmentMigration()
    success = migration.run_migration()
    
    if not success:
        print("❌ Migration failed!")
        return False
    
    print("✅ Migration completed successfully!")
    return True

def test_database_structure():
    """Test the new database structure"""
    print("\n🔍 Testing Database Structure...")
    
    try:
        conn = sqlite3.connect('products.db')
        cursor = conn.cursor()
        
        # Check if departments table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='departments'")
        if not cursor.fetchone():
            print("❌ Departments table not found!")
            return False
        
        # Check if products table has department_id column
        cursor.execute("PRAGMA table_info(products)")
        columns = [col[1] for col in cursor.fetchall()]
        if 'department_id' not in columns:
            print("❌ department_id column not found in products table!")
            return False
        
        if 'department' in columns:
            print("❌ Old department column still exists!")
            return False
        
        # Check foreign key constraint
        cursor.execute("PRAGMA foreign_key_list(products)")
        fk_constraints = cursor.fetchall()
        if not fk_constraints:
            print("❌ Foreign key constraint not found!")
            return False
        
        print("✅ Database structure is correct!")
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database structure test failed: {e}")
        return False

def test_data_integrity():
    """Test data integrity after migration"""
    print("\n📊 Testing Data Integrity...")
    
    try:
        conn = sqlite3.connect('products.db')
        cursor = conn.cursor()
        
        # Count records
        cursor.execute("SELECT COUNT(*) FROM products")
        product_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM departments")
        dept_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM products_backup")
        backup_count = cursor.fetchone()[0]
        
        print(f"📈 Products: {product_count}")
        print(f"📈 Departments: {dept_count}")
        print(f"📈 Backup: {backup_count}")
        
        # Check if all products have department_id
        cursor.execute("SELECT COUNT(*) FROM products WHERE department_id IS NULL")
        null_dept_count = cursor.fetchone()[0]
        
        if null_dept_count > 0:
            print(f"❌ {null_dept_count} products have NULL department_id!")
            return False
        
        # Check foreign key relationships
        cursor.execute("""
            SELECT COUNT(*) FROM products p
            JOIN departments d ON p.department_id = d.id
        """)
        linked_count = cursor.fetchone()[0]
        
        if linked_count != product_count:
            print(f"❌ Foreign key relationship mismatch! {linked_count} != {product_count}")
            return False
        
        print("✅ Data integrity verified!")
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Data integrity test failed: {e}")
        return False

def test_api_endpoints():
    """Test the updated API endpoints"""
    print("\n🌐 Testing API Endpoints...")
    
    try:
        # Start the API server
        import subprocess
        import threading
        
        # Start server in background
        server_process = subprocess.Popen(['python', 'app.py'], 
                                        stdout=subprocess.PIPE, 
                                        stderr=subprocess.PIPE)
        
        # Wait for server to start
        time.sleep(3)
        
        base_url = "http://localhost:5000"
        
        # Test home endpoint
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("✅ Home endpoint working")
        else:
            print(f"❌ Home endpoint failed: {response.status_code}")
            return False
        
        # Test departments endpoint
        response = requests.get(f"{base_url}/api/departments")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Departments endpoint working - {len(data['departments'])} departments")
        else:
            print(f"❌ Departments endpoint failed: {response.status_code}")
            return False
        
        # Test products endpoint with department filter
        response = requests.get(f"{base_url}/api/products?limit=5")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Products endpoint working - {len(data['products'])} products")
            
            # Check if products have department info
            if data['products']:
                product = data['products'][0]
                if 'department' in product and 'id' in product['department']:
                    print("✅ Products include department information")
                else:
                    print("❌ Products missing department information")
                    return False
        else:
            print(f"❌ Products endpoint failed: {response.status_code}")
            return False
        
        # Test stats endpoint
        response = requests.get(f"{base_url}/api/products/stats")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Stats endpoint working - {data['total_departments']} departments")
        else:
            print(f"❌ Stats endpoint failed: {response.status_code}")
            return False
        
        # Stop server
        server_process.terminate()
        server_process.wait()
        
        print("✅ All API endpoints working!")
        return True
        
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False

def test_sample_queries():
    """Test sample queries on the new structure"""
    print("\n🔍 Testing Sample Queries...")
    
    try:
        conn = sqlite3.connect('products.db')
        cursor = conn.cursor()
        
        # Test 1: Get products by department
        cursor.execute("""
            SELECT d.name, COUNT(*) as count
            FROM products p
            JOIN departments d ON p.department_id = d.id
            GROUP BY d.name
            ORDER BY count DESC
            LIMIT 3
        """)
        dept_counts = cursor.fetchall()
        print(f"✅ Products by department: {dept_counts}")
        
        # Test 2: Get average price by department
        cursor.execute("""
            SELECT d.name, AVG(p.retail_price) as avg_price
            FROM products p
            JOIN departments d ON p.department_id = d.id
            GROUP BY d.name
            ORDER BY avg_price DESC
            LIMIT 3
        """)
        avg_prices = cursor.fetchall()
        print(f"✅ Average price by department: {avg_prices}")
        
        # Test 3: Get products with highest profit margin
        cursor.execute("""
            SELECT p.name, d.name as department, 
                   (p.retail_price - p.cost) as profit_margin
            FROM products p
            JOIN departments d ON p.department_id = d.id
            ORDER BY (p.retail_price - p.cost) DESC
            LIMIT 3
        """)
        profit_margins = cursor.fetchall()
        print(f"✅ Highest profit margins: {profit_margins}")
        
        conn.close()
        print("✅ All sample queries working!")
        return True
        
    except Exception as e:
        print(f"❌ Sample queries test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting Database Refactoring Tests...\n")
    
    tests = [
        ("Migration", test_migration),
        ("Database Structure", test_database_structure),
        ("Data Integrity", test_data_integrity),
        ("Sample Queries", test_sample_queries),
        ("API Endpoints", test_api_endpoints)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_name} test failed!")
        except Exception as e:
            print(f"❌ {test_name} test failed with exception: {e}")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Database refactoring is successful!")
        print("\n📋 Summary of changes:")
        print("✅ Created separate departments table")
        print("✅ Added foreign key relationships")
        print("✅ Updated API to work with new structure")
        print("✅ Maintained data integrity")
        print("✅ Added new department-related endpoints")
    else:
        print("❌ Some tests failed. Please check the logs above.")

if __name__ == "__main__":
    main() 
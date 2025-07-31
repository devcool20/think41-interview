#!/usr/bin/env python3
"""
Check what departments actually exist in the database
"""

import sqlite3
import os

DATABASE_PATH = 'products.db'

def check_departments():
    """Check what departments exist in the database"""
    if not os.path.exists(DATABASE_PATH):
        print("❌ Database not found. Please run the database setup first.")
        return
    
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Check if departments table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='departments'")
        if not cursor.fetchone():
            print("❌ Departments table not found. Please run the database migration first.")
            return
        
        # Get all departments with their product counts
        cursor.execute("""
            SELECT d.id, d.name, COUNT(p.id) as product_count
            FROM departments d
            LEFT JOIN products p ON d.id = p.department_id
            GROUP BY d.id, d.name
            ORDER BY product_count DESC
        """)
        
        departments = cursor.fetchall()
        
        print("🏪 DEPARTMENTS IN THE DATABASE:")
        print("=" * 50)
        
        if not departments:
            print("❌ No departments found in the database.")
        else:
            for dept_id, dept_name, product_count in departments:
                print(f"📦 {dept_name} (ID: {dept_id}) - {product_count:,} products")
        
        print("\n" + "=" * 50)
        print(f"📊 Total Departments: {len(departments)}")
        
        # Also check some sample products to see the relationship
        print("\n🔍 SAMPLE PRODUCTS BY DEPARTMENT:")
        print("-" * 50)
        
        cursor.execute("""
            SELECT p.name, p.category, d.name as department_name
            FROM products p
            LEFT JOIN departments d ON p.department_id = d.id
            LIMIT 10
        """)
        
        sample_products = cursor.fetchall()
        for product_name, category, department_name in sample_products:
            print(f"📦 {product_name[:50]}...")
            print(f"   Category: {category}")
            print(f"   Department: {department_name}")
            print()
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error checking departments: {e}")

if __name__ == "__main__":
    check_departments() 
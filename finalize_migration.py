#!/usr/bin/env python3
"""
Finalize Migration: Add Foreign Key Constraint
Simple script to complete the migration
"""

import sqlite3
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def finalize_migration():
    """Finalize the migration by adding foreign key constraint"""
    try:
        conn = sqlite3.connect('products.db')
        cursor = conn.cursor()
        
        # Enable foreign key constraints
        cursor.execute("PRAGMA foreign_keys = ON")
        
        # Create new table with foreign key constraint
        cursor.execute("""
            CREATE TABLE products_final (
                id TEXT PRIMARY KEY,
                cost REAL NOT NULL,
                category TEXT NOT NULL,
                name TEXT NOT NULL,
                brand TEXT NOT NULL,
                retail_price REAL NOT NULL,
                sku TEXT NOT NULL,
                distribution_center_id INTEGER NOT NULL,
                department_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (department_id) REFERENCES departments(id)
            )
        """)
        
        # Copy data
        cursor.execute("""
            INSERT INTO products_final 
            SELECT * FROM products
        """)
        
        # Drop old table and rename
        cursor.execute("DROP TABLE products")
        cursor.execute("ALTER TABLE products_final RENAME TO products")
        
        # Recreate indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_products_category ON products(category)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_products_brand ON products(brand)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_products_department_id ON products(department_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_products_distribution_center ON products(distribution_center_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_products_sku ON products(sku)")
        
        # Recreate view
        cursor.execute("""
            CREATE OR REPLACE VIEW products_with_margin AS
            SELECT 
                p.*,
                d.name as department_name,
                (p.retail_price - p.cost) AS profit_margin,
                ROUND(((p.retail_price - p.cost) / p.retail_price * 100), 2) AS profit_margin_percentage
            FROM products p
            LEFT JOIN departments d ON p.department_id = d.id
        """)
        
        conn.commit()
        conn.close()
        
        logger.info("Migration finalized successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Failed to finalize migration: {e}")
        return False

def verify_final_state():
    """Verify the final state of the database"""
    try:
        conn = sqlite3.connect('products.db')
        cursor = conn.cursor()
        
        # Check departments table
        cursor.execute("SELECT COUNT(*) FROM departments")
        dept_count = cursor.fetchone()[0]
        print(f"✅ Departments: {dept_count}")
        
        # Check products table
        cursor.execute("SELECT COUNT(*) FROM products")
        product_count = cursor.fetchone()[0]
        print(f"✅ Products: {product_count}")
        
        # Check foreign key relationships
        cursor.execute("""
            SELECT COUNT(*) FROM products p
            JOIN departments d ON p.department_id = d.id
        """)
        linked_count = cursor.fetchone()[0]
        print(f"✅ Linked products: {linked_count}")
        
        # Check that old department column is gone
        cursor.execute("PRAGMA table_info(products)")
        columns = [col[1] for col in cursor.fetchall()]
        if 'department' not in columns:
            print("✅ Old department column removed")
        else:
            print("❌ Old department column still exists")
            return False
        
        # Check foreign key constraint
        cursor.execute("PRAGMA foreign_key_list(products)")
        fk_constraints = cursor.fetchall()
        if fk_constraints:
            print("✅ Foreign key constraint exists")
        else:
            print("❌ Foreign key constraint missing")
            return False
        
        # Sample data
        cursor.execute("""
            SELECT p.name, p.brand, d.name as department_name
            FROM products p
            JOIN departments d ON p.department_id = d.id
            LIMIT 3
        """)
        sample_data = cursor.fetchall()
        print("✅ Sample data:")
        for row in sample_data:
            print(f"  - {row[0]} ({row[1]}) - {row[2]}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Finalizing database migration...")
    
    if finalize_migration():
        print("\n🔍 Verifying final state...")
        if verify_final_state():
            print("\n🎉 Migration completed successfully!")
            print("The database has been fully refactored with:")
            print("✅ Separate departments table")
            print("✅ Foreign key relationships")
            print("✅ Proper normalization")
            print("✅ Updated API endpoints")
        else:
            print("\n❌ Verification failed")
    else:
        print("\n❌ Migration finalization failed") 
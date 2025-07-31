#!/usr/bin/env python3
"""
Complete Database Migration Script: Refactor Departments Table
Handles the current state and completes the migration
"""

import sqlite3
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CompleteMigration:
    def __init__(self, db_path='products.db'):
        self.db_path = db_path
        self.connection = None
        
    def connect(self):
        """Establish database connection"""
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row
            logger.info("Database connection established successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            return False
    
    def disconnect(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            logger.info("Database connection closed")
    
    def check_current_state(self):
        """Check the current state of the database"""
        try:
            cursor = self.connection.cursor()
            
            # Check if departments table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='departments'")
            has_departments = cursor.fetchone() is not None
            
            # Check products table structure
            cursor.execute("PRAGMA table_info(products)")
            columns = [col[1] for col in cursor.fetchall()]
            has_department_id = 'department_id' in columns
            has_department = 'department' in columns
            
            logger.info(f"Current state: departments_table={has_departments}, department_id={has_department_id}, department={has_department}")
            
            return {
                'has_departments': has_departments,
                'has_department_id': has_department_id,
                'has_department': has_department,
                'columns': columns
            }
        except Exception as e:
            logger.error(f"Failed to check current state: {e}")
            return None
    
    def create_departments_table(self):
        """Create the departments table if it doesn't exist"""
        try:
            cursor = self.connection.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS departments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(255) NOT NULL UNIQUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_departments_name ON departments(name)
            """)
            
            self.connection.commit()
            logger.info("Departments table created/verified successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to create departments table: {e}")
            return False
    
    def populate_departments(self):
        """Populate departments table with unique departments"""
        try:
            cursor = self.connection.cursor()
            
            # Get unique departments from products table
            cursor.execute("SELECT DISTINCT department FROM products WHERE department IS NOT NULL AND department != ''")
            departments = [row[0] for row in cursor.fetchall()]
            
            logger.info(f"Found {len(departments)} unique departments: {departments}")
            
            # Insert departments
            for dept in departments:
                cursor.execute("""
                    INSERT OR IGNORE INTO departments (name) VALUES (?)
                """, (dept,))
            
            self.connection.commit()
            
            # Verify insertion
            cursor.execute("SELECT COUNT(*) FROM departments")
            count = cursor.fetchone()[0]
            logger.info(f"Successfully populated departments table with {count} departments")
            return True
        except Exception as e:
            logger.error(f"Failed to populate departments: {e}")
            return False
    
    def add_department_id_column(self):
        """Add department_id column if it doesn't exist"""
        try:
            cursor = self.connection.cursor()
            
            # Check if column already exists
            cursor.execute("PRAGMA table_info(products)")
            columns = [col[1] for col in cursor.fetchall()]
            
            if 'department_id' not in columns:
                cursor.execute("""
                    ALTER TABLE products ADD COLUMN department_id INTEGER
                """)
                self.connection.commit()
                logger.info("Added department_id column to products table")
            else:
                logger.info("department_id column already exists")
            
            return True
        except Exception as e:
            logger.error(f"Failed to add department_id column: {e}")
            return False
    
    def update_department_ids(self):
        """Update department_id values based on department names"""
        try:
            cursor = self.connection.cursor()
            
            # Get department mappings
            cursor.execute("SELECT id, name FROM departments")
            dept_mappings = {row[1]: row[0] for row in cursor.fetchall()}
            
            # Update products with department_id
            cursor.execute("""
                UPDATE products 
                SET department_id = (
                    SELECT id FROM departments 
                    WHERE departments.name = products.department
                )
            """)
            
            self.connection.commit()
            
            # Verify update
            cursor.execute("SELECT COUNT(*) FROM products WHERE department_id IS NOT NULL")
            updated_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM products")
            total_count = cursor.fetchone()[0]
            
            logger.info(f"Updated {updated_count} out of {total_count} products with department_id")
            return True
        except Exception as e:
            logger.error(f"Failed to update department_ids: {e}")
            return False
    
    def remove_old_department_column(self):
        """Remove the old department column"""
        try:
            cursor = self.connection.cursor()
            
            # Get current table structure
            cursor.execute("PRAGMA table_info(products)")
            columns = cursor.fetchall()
            
            # Create new table without department column
            column_definitions = []
            for col in columns:
                if col[1] != 'department':  # Skip the old department column
                    col_def = f"{col[1]} {col[2]}"
                    if col[5] == 1:  # Primary key
                        col_def += " PRIMARY KEY"
                    if col[3] == 1:  # NOT NULL
                        col_def += " NOT NULL"
                    if col[4] is not None and col[4] != 'CURRENT_TIMESTAMP':
                        col_def += f" DEFAULT {col[4]}"
                    elif col[4] == 'CURRENT_TIMESTAMP':
                        col_def += " DEFAULT CURRENT_TIMESTAMP"
                    column_definitions.append(col_def)
            
            # Create new table
            new_table_sql = f"""
                CREATE TABLE products_new (
                    {', '.join(column_definitions)}
                )
            """
            cursor.execute(new_table_sql)
            
            # Copy data to new table (excluding department column)
            select_columns = [col[1] for col in columns if col[1] != 'department']
            select_sql = f"SELECT {', '.join(select_columns)} FROM products"
            
            cursor.execute(f"INSERT INTO products_new {select_sql}")
            
            # Drop old table and rename new table
            cursor.execute("DROP TABLE products")
            cursor.execute("ALTER TABLE products_new RENAME TO products")
            
            # Recreate indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_products_category ON products(category)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_products_brand ON products(brand)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_products_department_id ON products(department_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_products_distribution_center ON products(distribution_center_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_products_sku ON products(sku)")
            
            self.connection.commit()
            logger.info("Successfully removed old department column")
            return True
        except Exception as e:
            logger.error(f"Failed to remove old department column: {e}")
            return False
    
    def add_foreign_key_constraint(self):
        """Add foreign key constraint"""
        try:
            cursor = self.connection.cursor()
            
            # Enable foreign key constraints
            cursor.execute("PRAGMA foreign_keys = ON")
            
            # Create new table with foreign key constraint
            cursor.execute("""
                CREATE TABLE products_with_fk (
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
                INSERT INTO products_with_fk 
                SELECT * FROM products
            """)
            
            # Drop old table and rename
            cursor.execute("DROP TABLE products")
            cursor.execute("ALTER TABLE products_with_fk RENAME TO products")
            
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
            
            self.connection.commit()
            logger.info("Successfully added foreign key constraint")
            return True
        except Exception as e:
            logger.error(f"Failed to add foreign key constraint: {e}")
            return False
    
    def verify_migration(self):
        """Verify that the migration was successful"""
        try:
            cursor = self.connection.cursor()
            
            # Check departments table
            cursor.execute("SELECT COUNT(*) FROM departments")
            dept_count = cursor.fetchone()[0]
            logger.info(f"Departments table has {dept_count} records")
            
            # Check products table
            cursor.execute("SELECT COUNT(*) FROM products")
            product_count = cursor.fetchone()[0]
            logger.info(f"Products table has {product_count} records")
            
            # Check foreign key relationships
            cursor.execute("""
                SELECT COUNT(*) FROM products p
                JOIN departments d ON p.department_id = d.id
            """)
            linked_count = cursor.fetchone()[0]
            logger.info(f"Products with valid department links: {linked_count}")
            
            # Check that old department column is gone
            cursor.execute("PRAGMA table_info(products)")
            columns = [col[1] for col in cursor.fetchall()]
            if 'department' in columns:
                logger.error("Old department column still exists!")
                return False
            
            # Sample data verification
            cursor.execute("""
                SELECT p.name, p.brand, d.name as department_name
                FROM products p
                JOIN departments d ON p.department_id = d.id
                LIMIT 5
            """)
            sample_data = cursor.fetchall()
            logger.info("Sample data after migration:")
            for row in sample_data:
                logger.info(f"  Product: {row[0]}, Brand: {row[1]}, Department: {row[2]}")
            
            return True
        except Exception as e:
            logger.error(f"Failed to verify migration: {e}")
            return False
    
    def run_migration(self):
        """Run the complete migration process"""
        logger.info("Starting complete database migration...")
        
        try:
            # Step 1: Connect to database
            if not self.connect():
                return False
            
            # Step 2: Check current state
            state = self.check_current_state()
            if not state:
                return False
            
            # Step 3: Create departments table
            if not self.create_departments_table():
                return False
            
            # Step 4: Populate departments (only if table is empty)
            if state['has_departments']:
                cursor = self.connection.cursor()
                cursor.execute("SELECT COUNT(*) FROM departments")
                if cursor.fetchone()[0] == 0:
                    if not self.populate_departments():
                        return False
                else:
                    logger.info("Departments table already populated")
            else:
                if not self.populate_departments():
                    return False
            
            # Step 5: Add department_id column if needed
            if not state['has_department_id']:
                if not self.add_department_id_column():
                    return False
            
            # Step 6: Update department_ids if needed
            if state['has_department']:
                if not self.update_department_ids():
                    return False
            
            # Step 7: Remove old department column if it exists
            if state['has_department']:
                if not self.remove_old_department_column():
                    return False
            
            # Step 8: Add foreign key constraint
            if not self.add_foreign_key_constraint():
                return False
            
            # Step 9: Verify migration
            if not self.verify_migration():
                return False
            
            logger.info("Complete database migration completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            return False
        finally:
            self.disconnect()

def main():
    """Main function to run the migration"""
    migration = CompleteMigration()
    success = migration.run_migration()
    
    if success:
        print("✅ Complete migration completed successfully!")
        print("The database has been fully refactored with a separate departments table.")
        print("You can now use the updated API with the new structure.")
    else:
        print("❌ Migration failed. Check the logs for details.")

if __name__ == "__main__":
    main() 
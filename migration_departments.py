#!/usr/bin/env python3
"""
Database Migration Script: Refactor Departments Table
Milestone 4: Move departments into a separate table with proper foreign key relationships

This script will:
1. Create a new departments table
2. Extract unique department names from products data
3. Populate the departments table with these unique departments
4. Update the products table to reference departments via foreign key
5. Update the existing products API to include department information
"""

import sqlite3
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DepartmentMigration:
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
    
    def backup_products_table(self):
        """Create a backup of the products table before migration"""
        try:
            cursor = self.connection.cursor()
            
            # Create backup table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS products_backup AS 
                SELECT * FROM products
            """)
            
            self.connection.commit()
            logger.info("Products table backed up successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to backup products table: {e}")
            return False
    
    def create_departments_table(self):
        """Create the new departments table"""
        try:
            cursor = self.connection.cursor()
            
            # Create departments table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS departments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(255) NOT NULL UNIQUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create index for department name
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_departments_name ON departments(name)
            """)
            
            self.connection.commit()
            logger.info("Departments table created successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to create departments table: {e}")
            return False
    
    def extract_unique_departments(self):
        """Extract unique department names from products table"""
        try:
            cursor = self.connection.cursor()
            
            # Get unique departments
            cursor.execute("SELECT DISTINCT department FROM products WHERE department IS NOT NULL AND department != ''")
            departments = [row[0] for row in cursor.fetchall()]
            
            logger.info(f"Found {len(departments)} unique departments: {departments}")
            return departments
        except Exception as e:
            logger.error(f"Failed to extract unique departments: {e}")
            return []
    
    def populate_departments_table(self, departments):
        """Populate the departments table with unique departments"""
        try:
            cursor = self.connection.cursor()
            
            # Insert departments
            for department in departments:
                cursor.execute("""
                    INSERT OR IGNORE INTO departments (name) VALUES (?)
                """, (department,))
            
            self.connection.commit()
            
            # Verify insertion
            cursor.execute("SELECT COUNT(*) FROM departments")
            count = cursor.fetchone()[0]
            logger.info(f"Successfully populated departments table with {count} departments")
            return True
        except Exception as e:
            logger.error(f"Failed to populate departments table: {e}")
            return False
    
    def add_department_id_to_products(self):
        """Add department_id column to products table"""
        try:
            cursor = self.connection.cursor()
            
            # Add department_id column
            cursor.execute("""
                ALTER TABLE products ADD COLUMN department_id INTEGER
            """)
            
            self.connection.commit()
            logger.info("Added department_id column to products table")
            return True
        except Exception as e:
            logger.error(f"Failed to add department_id column: {e}")
            return False
    
    def update_products_with_department_ids(self):
        """Update products table to set department_id based on department name"""
        try:
            cursor = self.connection.cursor()
            
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
            logger.error(f"Failed to update products with department_id: {e}")
            return False
    
    def drop_old_department_column(self):
        """Remove the old department column from products table"""
        try:
            cursor = self.connection.cursor()
            
            # SQLite doesn't support DROP COLUMN directly, so we need to recreate the table
            # First, get the current table structure
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
                    if col[4] is not None and col[4] != 'CURRENT_TIMESTAMP':  # Default value
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
            
            # Copy data to new table
            cursor.execute("""
                INSERT INTO products_new 
                SELECT id, cost, category, name, brand, retail_price, sku, 
                       distribution_center_id, created_at, department_id
                FROM products
            """)
            
            # Drop old table and rename new table
            cursor.execute("DROP TABLE products")
            cursor.execute("ALTER TABLE products_new RENAME TO products")
            
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
            logger.info("Successfully removed old department column and updated table structure")
            return True
        except Exception as e:
            logger.error(f"Failed to drop old department column: {e}")
            return False
    
    def add_foreign_key_constraint(self):
        """Add foreign key constraint to ensure referential integrity"""
        try:
            cursor = self.connection.cursor()
            
            # Enable foreign key constraints
            cursor.execute("PRAGMA foreign_keys = ON")
            
            # Add foreign key constraint
            cursor.execute("""
                CREATE TABLE products_with_fk (
                    id VARCHAR(255) PRIMARY KEY,
                    cost DECIMAL(10, 4) NOT NULL,
                    category VARCHAR(255) NOT NULL,
                    name TEXT NOT NULL,
                    brand VARCHAR(255) NOT NULL,
                    retail_price DECIMAL(10, 4) NOT NULL,
                    sku VARCHAR(255) NOT NULL,
                    distribution_center_id INTEGER NOT NULL,
                    department_id INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
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
        logger.info("Starting department table migration...")
        
        try:
            # Step 1: Connect to database
            if not self.connect():
                return False
            
            # Step 2: Backup existing data
            if not self.backup_products_table():
                return False
            
            # Step 3: Create departments table
            if not self.create_departments_table():
                return False
            
            # Step 4: Extract unique departments
            departments = self.extract_unique_departments()
            if not departments:
                logger.error("No departments found to migrate")
                return False
            
            # Step 5: Populate departments table
            if not self.populate_departments_table(departments):
                return False
            
            # Step 6: Add department_id column to products
            if not self.add_department_id_to_products():
                return False
            
            # Step 7: Update products with department_ids
            if not self.update_products_with_department_ids():
                return False
            
            # Step 8: Drop old department column
            if not self.drop_old_department_column():
                return False
            
            # Step 9: Add foreign key constraint
            if not self.add_foreign_key_constraint():
                return False
            
            # Step 10: Verify migration
            if not self.verify_migration():
                return False
            
            logger.info("Department table migration completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            return False
        finally:
            self.disconnect()

def main():
    """Main function to run the migration"""
    migration = DepartmentMigration()
    success = migration.run_migration()
    
    if success:
        print("✅ Migration completed successfully!")
        print("The database has been refactored with a separate departments table.")
        print("You can now update your API to use the new structure.")
    else:
        print("❌ Migration failed. Check the logs for details.")
        print("You can restore from the backup table if needed.")

if __name__ == "__main__":
    main() 
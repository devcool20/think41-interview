#!/usr/bin/env python3
"""
SQLite version of the database manager for easier testing.
This version uses SQLite instead of PostgreSQL for simplicity.
"""

import pandas as pd
import sqlite3
import logging
import os
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SQLiteDatabaseManager:
    def __init__(self, db_path='products.db'):
        self.db_path = db_path
        self.connection = None
        
    def connect(self):
        """Establish SQLite database connection"""
        try:
            self.connection = sqlite3.connect(self.db_path)
            logger.info(f"SQLite database connection established: {self.db_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to SQLite database: {e}")
            return False
    
    def disconnect(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
        logger.info("SQLite database connection closed")
    
    def create_schema(self):
        """Create database schema for SQLite"""
        try:
            schema_sql = """
            CREATE TABLE IF NOT EXISTS products (
                id TEXT PRIMARY KEY,
                cost REAL NOT NULL,
                category TEXT NOT NULL,
                name TEXT NOT NULL,
                brand TEXT NOT NULL,
                retail_price REAL NOT NULL,
                department TEXT NOT NULL,
                sku TEXT NOT NULL,
                distribution_center_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);
            CREATE INDEX IF NOT EXISTS idx_products_brand ON products(brand);
            CREATE INDEX IF NOT EXISTS idx_products_department ON products(department);
            CREATE INDEX IF NOT EXISTS idx_products_distribution_center ON products(distribution_center_id);
            CREATE INDEX IF NOT EXISTS idx_products_sku ON products(sku);
            """
            
            self.connection.executescript(schema_sql)
            self.connection.commit()
            logger.info("SQLite database schema created successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to create schema: {e}")
            return False
    
    def load_csv_data(self, batch_size=1000):
        """Load CSV data into SQLite database in batches"""
        try:
            logger.info(f"Starting to load data from products.csv")
            
            # Read CSV in chunks to handle large files
            chunk_count = 0
            total_rows = 0
            
            for chunk in pd.read_csv('products.csv', chunksize=batch_size):
                # Clean and prepare data
                chunk = self._prepare_data(chunk)
                
                # Insert chunk into database
                chunk.to_sql('products', self.connection, if_exists='append', index=False, method='multi')
                
                chunk_count += 1
                total_rows += len(chunk)
                logger.info(f"Loaded chunk {chunk_count}: {len(chunk)} rows (Total: {total_rows})")
            
            logger.info(f"Data loading completed. Total rows loaded: {total_rows}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load CSV data: {e}")
            return False
    
    def _prepare_data(self, df):
        """Prepare and clean the dataframe before insertion"""
        # Ensure all required columns exist
        required_columns = ['id', 'cost', 'category', 'name', 'brand', 'retail_price', 'department', 'sku', 'distribution_center_id']
        
        for col in required_columns:
            if col not in df.columns:
                raise ValueError(f"Missing required column: {col}")
        
        # Clean data types
        df['id'] = df['id'].astype(str)
        df['cost'] = pd.to_numeric(df['cost'], errors='coerce')
        df['category'] = df['category'].astype(str)
        df['name'] = df['name'].astype(str)
        df['brand'] = df['brand'].astype(str)
        df['retail_price'] = pd.to_numeric(df['retail_price'], errors='coerce')
        df['department'] = df['department'].astype(str)
        df['sku'] = df['sku'].astype(str)
        df['distribution_center_id'] = pd.to_numeric(df['distribution_center_id'], errors='coerce')
        
        # Remove rows with null values in critical fields
        df = df.dropna(subset=['id', 'cost', 'retail_price'])
        
        return df
    
    def verify_data_loading(self):
        """Verify that data was loaded correctly"""
        try:
            cursor = self.connection.cursor()
            
            # Count total rows
            cursor.execute("SELECT COUNT(*) FROM products")
            total_count = cursor.fetchone()[0]
            logger.info(f"Total products in database: {total_count}")
            
            # Check for data quality
            cursor.execute("SELECT COUNT(*) FROM products WHERE cost <= 0 OR retail_price <= 0")
            invalid_prices = cursor.fetchone()[0]
            logger.info(f"Products with invalid prices: {invalid_prices}")
            
            # Sample data verification
            cursor.execute("SELECT * FROM products LIMIT 5")
            sample_data = cursor.fetchall()
            logger.info("Sample data from database:")
            for row in sample_data:
                logger.info(f"  ID: {row[0]}, Name: {row[3]}, Brand: {row[4]}, Price: {row[5]}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to verify data: {e}")
            return False
    
    def run_verification_queries(self):
        """Run various verification queries to analyze the data"""
        queries = {
            "Total Products": "SELECT COUNT(*) FROM products",
            "Products by Category": "SELECT category, COUNT(*) as count FROM products GROUP BY category ORDER BY count DESC LIMIT 10",
            "Products by Brand": "SELECT brand, COUNT(*) as count FROM products GROUP BY brand ORDER BY count DESC LIMIT 10",
            "Average Price by Category": "SELECT category, AVG(retail_price) as avg_price FROM products GROUP BY category ORDER BY avg_price DESC LIMIT 10",
            "Products with Highest Profit Margin": "SELECT name, brand, retail_price, cost, (retail_price - cost) as profit_margin FROM products ORDER BY (retail_price - cost) DESC LIMIT 10"
        }
        
        results = {}
        cursor = self.connection.cursor()
        
        for query_name, query in queries.items():
            try:
                cursor.execute(query)
                if query_name in ["Total Products"]:
                    results[query_name] = cursor.fetchone()[0]
                else:
                    results[query_name] = cursor.fetchall()
                logger.info(f"Query '{query_name}' executed successfully")
            except Exception as e:
                logger.error(f"Failed to execute query '{query_name}': {e}")
                results[query_name] = None
        
        return results

def main():
    """Main function to run the SQLite version"""
    db_manager = SQLiteDatabaseManager()
    
    try:
        logger.info("Starting SQLite CSV to Database loading process")
        
        # Step 1: Connect to database
        logger.info("Step 1: Connecting to SQLite database...")
        if not db_manager.connect():
            logger.error("Failed to connect to database. Exiting.")
            return False
        
        # Step 2: Create schema
        logger.info("Step 2: Creating database schema...")
        if not db_manager.create_schema():
            logger.error("Failed to create schema. Exiting.")
            return False
        
        # Step 3: Load CSV data
        logger.info("Step 3: Loading CSV data into database...")
        if not db_manager.load_csv_data(batch_size=1000):
            logger.error("Failed to load CSV data. Exiting.")
            return False
        
        # Step 4: Verify data loading
        logger.info("Step 4: Verifying data loading...")
        if not db_manager.verify_data_loading():
            logger.error("Data verification failed.")
            return False
        
        # Step 5: Run verification queries
        logger.info("Step 5: Running verification queries...")
        results = db_manager.run_verification_queries()
        
        # Display results
        print("\n" + "="*50)
        print("SQLITE DATA LOADING VERIFICATION RESULTS")
        print("="*50)
        
        for query_name, result in results.items():
            print(f"\n{query_name}:")
            if isinstance(result, int):
                print(f"  {result}")
            elif isinstance(result, list):
                for row in result[:5]:  # Show first 5 results
                    print(f"  {row}")
                if len(result) > 5:
                    print(f"  ... and {len(result) - 5} more results")
            else:
                print(f"  {result}")
        
        print("\n" + "="*50)
        print("SQLITE PROCESS COMPLETED SUCCESSFULLY!")
        print(f"Database file: {db_manager.db_path}")
        print("="*50)
        
        return True
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return False
    
    finally:
        # Always disconnect from database
        db_manager.disconnect()

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1) 
import pandas as pd
import psycopg2
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
import logging
from config import get_database_url, CSV_FILE_PATH

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        self.engine = None
        self.connection = None
        
    def connect(self):
        """Establish database connection"""
        try:
            database_url = get_database_url()
            self.engine = create_engine(database_url)
            self.connection = self.engine.connect()
            logger.info("Database connection established successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            return False
    
    def disconnect(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
        if self.engine:
            self.engine.dispose()
        logger.info("Database connection closed")
    
    def create_schema(self):
        """Create database schema from SQL file"""
        try:
            with open('database_schema.sql', 'r') as file:
                schema_sql = file.read()
            
            # Split by semicolon and execute each statement
            statements = schema_sql.split(';')
            for statement in statements:
                statement = statement.strip()
                if statement and not statement.startswith('--'):
                    self.connection.execute(text(statement))
            
            self.connection.commit()
            logger.info("Database schema created successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to create schema: {e}")
            return False
    
    def load_csv_data(self, batch_size=1000):
        """Load CSV data into database in batches"""
        try:
            logger.info(f"Starting to load data from {CSV_FILE_PATH}")
            
            # Read CSV in chunks to handle large files
            chunk_count = 0
            total_rows = 0
            
            for chunk in pd.read_csv(CSV_FILE_PATH, chunksize=batch_size):
                # Clean and prepare data
                chunk = self._prepare_data(chunk)
                
                # Insert chunk into database
                chunk.to_sql('products', self.engine, if_exists='append', index=False, method='multi')
                
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
            # Count total rows
            result = self.connection.execute(text("SELECT COUNT(*) FROM products"))
            total_count = result.fetchone()[0]
            logger.info(f"Total products in database: {total_count}")
            
            # Check for data quality
            result = self.connection.execute(text("SELECT COUNT(*) FROM products WHERE cost <= 0 OR retail_price <= 0"))
            invalid_prices = result.fetchone()[0]
            logger.info(f"Products with invalid prices: {invalid_prices}")
            
            # Sample data verification
            result = self.connection.execute(text("SELECT * FROM products LIMIT 5"))
            sample_data = result.fetchall()
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
        for query_name, query in queries.items():
            try:
                result = self.connection.execute(text(query))
                if query_name in ["Total Products"]:
                    results[query_name] = result.fetchone()[0]
                else:
                    results[query_name] = result.fetchall()
                logger.info(f"Query '{query_name}' executed successfully")
            except Exception as e:
                logger.error(f"Failed to execute query '{query_name}': {e}")
                results[query_name] = None
        
        return results 
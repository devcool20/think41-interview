#!/usr/bin/env python3
"""
Main script to load CSV data into database and verify the process.
This script performs the following steps:
1. Connect to database
2. Create schema
3. Load CSV data
4. Verify data loading
5. Run verification queries
"""

import sys
import logging
from database_manager import DatabaseManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data_loading.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def main():
    """Main function to orchestrate the data loading process"""
    db_manager = DatabaseManager()
    
    try:
        logger.info("Starting CSV to Database loading process")
        
        # Step 1: Connect to database
        logger.info("Step 1: Connecting to database...")
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
        print("DATA LOADING VERIFICATION RESULTS")
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
        print("PROCESS COMPLETED SUCCESSFULLY!")
        print("="*50)
        
        return True
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return False
    
    finally:
        # Always disconnect from database
        db_manager.disconnect()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 
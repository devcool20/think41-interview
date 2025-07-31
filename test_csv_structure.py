#!/usr/bin/env python3
"""
Test script to analyze CSV structure and validate data without database connection.
This helps verify the CSV data before attempting database operations.
"""

import pandas as pd
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def analyze_csv_structure():
    """Analyze the CSV file structure and data quality"""
    try:
        logger.info("Starting CSV structure analysis...")
        
        # Read first few rows to understand structure
        logger.info("Reading CSV header and first few rows...")
        df_sample = pd.read_csv('products.csv', nrows=10)
        
        print("\n" + "="*60)
        print("CSV STRUCTURE ANALYSIS")
        print("="*60)
        
        # Display basic information
        print(f"\nCSV File: products.csv")
        print(f"Total rows: 29,121 (from previous analysis)")
        print(f"Columns: {len(df_sample.columns)}")
        
        # Display column information
        print(f"\nColumns:")
        for i, col in enumerate(df_sample.columns, 1):
            print(f"  {i}. {col}")
        
        # Display data types
        print(f"\nData Types:")
        for col, dtype in df_sample.dtypes.items():
            print(f"  {col}: {dtype}")
        
        # Display sample data
        print(f"\nSample Data (first 5 rows):")
        print(df_sample.head().to_string(index=False))
        
        # Data quality analysis
        logger.info("Performing data quality analysis...")
        
        # Read in chunks for memory efficiency
        total_rows = 0
        null_counts = {}
        unique_counts = {}
        
        for chunk in pd.read_csv('products.csv', chunksize=1000):
            total_rows += len(chunk)
            
            # Count nulls
            for col in chunk.columns:
                if col not in null_counts:
                    null_counts[col] = 0
                null_counts[col] += chunk[col].isnull().sum()
            
            # Count unique values (for categorical columns)
            for col in ['category', 'brand', 'department']:
                if col not in unique_counts:
                    unique_counts[col] = set()
                unique_counts[col].update(chunk[col].dropna().unique())
        
        print(f"\nData Quality Analysis:")
        print(f"  Total rows processed: {total_rows:,}")
        
        print(f"\nNull value counts:")
        for col, null_count in null_counts.items():
            percentage = (null_count / total_rows) * 100
            print(f"  {col}: {null_count:,} ({percentage:.2f}%)")
        
        print(f"\nUnique value counts:")
        for col, unique_vals in unique_counts.items():
            print(f"  {col}: {len(unique_vals):,} unique values")
        
        # Numeric data analysis
        logger.info("Analyzing numeric data...")
        numeric_df = pd.read_csv('products.csv', usecols=['cost', 'retail_price', 'distribution_center_id'])
        
        print(f"\nNumeric Data Statistics:")
        print(numeric_df.describe().round(2))
        
        # Check for data issues
        print(f"\nData Quality Issues:")
        
        # Check for negative prices
        negative_cost = (numeric_df['cost'] < 0).sum()
        negative_price = (numeric_df['retail_price'] < 0).sum()
        
        if negative_cost > 0:
            print(f"  ⚠️  {negative_cost:,} products with negative cost")
        else:
            print(f"  ✅ No negative cost values")
            
        if negative_price > 0:
            print(f"  ⚠️  {negative_price:,} products with negative retail price")
        else:
            print(f"  ✅ No negative retail price values")
        
        # Check for zero prices
        zero_cost = (numeric_df['cost'] == 0).sum()
        zero_price = (numeric_df['retail_price'] == 0).sum()
        
        if zero_cost > 0:
            print(f"  ⚠️  {zero_cost:,} products with zero cost")
        else:
            print(f"  ✅ No zero cost values")
            
        if zero_price > 0:
            print(f"  ⚠️  {zero_price:,} products with zero retail price")
        else:
            print(f"  ✅ No zero retail price values")
        
        # Check for cost > retail_price
        cost_greater = (numeric_df['cost'] > numeric_df['retail_price']).sum()
        if cost_greater > 0:
            print(f"  ⚠️  {cost_greater:,} products where cost > retail price")
        else:
            print(f"  ✅ All products have cost <= retail price")
        
        print(f"\n" + "="*60)
        print("ANALYSIS COMPLETED SUCCESSFULLY!")
        print("="*60)
        
        return True
        
    except Exception as e:
        logger.error(f"Error during CSV analysis: {e}")
        return False

if __name__ == "__main__":
    success = analyze_csv_structure()
    sys.exit(0 if success else 1) 
#!/usr/bin/env python3
"""
Simple script to show sample data from the database for demo purposes
"""

import sqlite3

def show_sample_data():
    """Display sample data from the products table"""
    try:
        # Connect to database
        conn = sqlite3.connect('products.db')
        cursor = conn.cursor()
        
        print("=" * 80)
        print("SAMPLE DATA FROM PRODUCTS TABLE")
        print("=" * 80)
        
        # Show total count
        cursor.execute("SELECT COUNT(*) FROM products")
        total_count = cursor.fetchone()[0]
        print(f"Total Products in Database: {total_count:,}")
        print()
        
        # Show sample records
        cursor.execute("""
            SELECT id, name, brand, retail_price, cost, category, department 
            FROM products 
            LIMIT 10
        """)
        
        rows = cursor.fetchall()
        print("Sample Products:")
        print("-" * 80)
        
        for i, row in enumerate(rows, 1):
            id_val, name, brand, retail_price, cost, category, department = row
            profit_margin = retail_price - cost
            margin_percentage = (profit_margin / retail_price) * 100 if retail_price > 0 else 0
            
            print(f"{i}. ID: {id_val}")
            print(f"   Name: {name}")
            print(f"   Brand: {brand}")
            print(f"   Category: {category}")
            print(f"   Department: {department}")
            print(f"   Cost: ${cost:.2f}")
            print(f"   Retail Price: ${retail_price:.2f}")
            print(f"   Profit Margin: ${profit_margin:.2f} ({margin_percentage:.1f}%)")
            print()
        
        # Show some statistics
        print("=" * 80)
        print("DATABASE STATISTICS")
        print("=" * 80)
        
        # Categories
        cursor.execute("""
            SELECT category, COUNT(*) as count 
            FROM products 
            GROUP BY category 
            ORDER BY count DESC 
            LIMIT 5
        """)
        print("Top 5 Categories:")
        for row in cursor.fetchall():
            print(f"  {row[0]}: {row[1]:,} products")
        
        print()
        
        # Brands
        cursor.execute("""
            SELECT brand, COUNT(*) as count 
            FROM products 
            GROUP BY brand 
            ORDER BY count DESC 
            LIMIT 5
        """)
        print("Top 5 Brands:")
        for row in cursor.fetchall():
            print(f"  {row[0]}: {row[1]:,} products")
        
        print()
        
        # Price ranges
        cursor.execute("""
            SELECT 
                MIN(retail_price) as min_price,
                MAX(retail_price) as max_price,
                AVG(retail_price) as avg_price
            FROM products
        """)
        price_stats = cursor.fetchone()
        print("Price Statistics:")
        print(f"  Min Price: ${price_stats[0]:.2f}")
        print(f"  Max Price: ${price_stats[1]:.2f}")
        print(f"  Average Price: ${price_stats[2]:.2f}")
        
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    show_sample_data() 
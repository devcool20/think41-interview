#!/usr/bin/env python3
"""
Examine the CSV file to understand what departments should be
"""

def examine_csv():
    """Examine the CSV file structure and department values"""
    try:
        # Read first few lines of CSV to understand structure
        with open('products.csv', 'r', encoding='utf-8') as f:
            # Read header
            header = f.readline().strip()
            print("📋 CSV HEADER:")
            print(header)
            print()
            
            # Read first few data rows
            print("📊 FIRST 5 ROWS:")
            for i in range(5):
                line = f.readline().strip()
                if line:
                    print(f"Row {i+1}: {line[:200]}...")
                    print()
            
            # Now let's count unique department values
            f.seek(0)  # Go back to start
            f.readline()  # Skip header
            
            departments = set()
            for i, line in enumerate(f):
                if i >= 1000:  # Only check first 1000 rows for speed
                    break
                parts = line.split(',')
                if len(parts) >= 8:  # Assuming department is in a specific column
                    # Try different positions for department
                    for pos in [7, 8, 9]:  # Common positions for department
                        if pos < len(parts):
                            dept = parts[pos].strip().strip('"')
                            if dept and dept != 'department':  # Skip header if present
                                departments.add(dept)
            
            print("🏪 UNIQUE DEPARTMENT VALUES (from first 1000 rows):")
            print("=" * 50)
            for dept in sorted(departments):
                print(f"📦 {dept}")
            
            print(f"\n📊 Total unique departments found: {len(departments)}")
            
    except Exception as e:
        print(f"❌ Error examining CSV: {e}")

if __name__ == "__main__":
    examine_csv() 
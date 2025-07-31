# CSV to Database Data Loading Project

This project provides a complete solution for loading CSV data into a PostgreSQL database with verification and analysis capabilities.

## Project Structure

```
think41-interview/
├── products.csv                    # Source CSV data (29,121 rows)
├── database_schema.sql            # Database schema definition
├── config.py                      # Database configuration
├── database_manager.py            # Database operations manager
├── main.py                        # Main execution script
├── requirements.txt               # Python dependencies
├── env_example.txt               # Environment variables template
└── README.md                     # This file
```

## CSV Data Analysis

The `products.csv` file contains 29,121 product records with the following structure:

| Column | Type | Description |
|--------|------|-------------|
| id | VARCHAR(255) | Product ID (Primary Key) |
| cost | DECIMAL(10,4) | Product cost |
| category | VARCHAR(255) | Product category |
| name | TEXT | Product name |
| brand | VARCHAR(255) | Brand name |
| retail_price | DECIMAL(10,4) | Retail price |
| department | VARCHAR(255) | Department |
| sku | VARCHAR(255) | Stock keeping unit |
| distribution_center_id | INTEGER | Distribution center ID |

## Database Schema Design

The database schema includes:

1. **Products Table**: Main table with all product data
2. **Indexes**: Performance optimization for common queries
3. **Views**: Pre-calculated profit margin analysis
4. **Data Validation**: Constraints and data type enforcement

### Key Features:
- Primary key on `id` field
- Appropriate data types for each column
- Indexes on frequently queried columns
- Automatic timestamp fields for audit trail
- Profit margin calculation view

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Database Setup

1. Install PostgreSQL if not already installed
2. Create a new database:
   ```sql
   CREATE DATABASE products_db;
   ```

### 3. Environment Configuration

1. Copy `env_example.txt` to `.env`:
   ```bash
   cp env_example.txt .env
   ```

2. Update `.env` with your database credentials:
   ```
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=products_db
   DB_USER=your_username
   DB_PASSWORD=your_password
   ```

### 4. Run the Data Loading Process

```bash
python main.py
```

## What the Script Does

The `main.py` script performs the following steps:

1. **Database Connection**: Establishes connection to PostgreSQL
2. **Schema Creation**: Creates tables, indexes, and views
3. **Data Loading**: Loads CSV data in batches (1000 rows at a time)
4. **Data Verification**: Validates loaded data integrity
5. **Analysis Queries**: Runs verification queries to analyze the data

## Verification Queries

The system automatically runs these verification queries:

1. **Total Products Count**: Verify all records were loaded
2. **Products by Category**: Distribution analysis
3. **Products by Brand**: Brand analysis
4. **Average Price by Category**: Pricing analysis
5. **Highest Profit Margin Products**: Profitability analysis

## Output

The script provides:
- Real-time progress logging
- Detailed verification results
- Data quality metrics
- Sample data display
- Log file (`data_loading.log`) for troubleshooting

## Performance Features

- **Batch Processing**: Loads data in configurable chunks
- **Memory Efficient**: Processes large CSV files without loading entire file into memory
- **Data Validation**: Ensures data integrity during loading
- **Indexed Queries**: Optimized database performance
- **Error Handling**: Comprehensive error handling and logging

## Troubleshooting

### Common Issues:

1. **Database Connection Failed**:
   - Verify PostgreSQL is running
   - Check database credentials in `.env`
   - Ensure database exists

2. **Permission Errors**:
   - Verify database user has CREATE and INSERT permissions
   - Check file permissions for CSV access

3. **Memory Issues**:
   - Reduce batch size in `main.py` (default: 1000)
   - Ensure sufficient system memory

### Logs:
- Check `data_loading.log` for detailed error information
- Console output shows real-time progress

## Data Analysis Examples

After successful loading, you can run additional queries:

```sql
-- Products with highest profit margin
SELECT name, brand, retail_price, cost, 
       (retail_price - cost) as profit_margin,
       ROUND(((retail_price - cost) / retail_price * 100), 2) as margin_percentage
FROM products 
ORDER BY profit_margin DESC 
LIMIT 10;

-- Category performance analysis
SELECT category, 
       COUNT(*) as product_count,
       AVG(retail_price) as avg_price,
       AVG(retail_price - cost) as avg_profit
FROM products 
GROUP BY category 
ORDER BY avg_profit DESC;
```

## Requirements

- Python 3.7+
- PostgreSQL 10+
- 2GB+ available memory (for large CSV processing)
- Required Python packages (see `requirements.txt`) 
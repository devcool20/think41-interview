# Database Refactoring: Departments Table Migration

## Overview

This document describes the database refactoring process to move departments into a separate table with proper foreign key relationships, as part of Milestone 4.

## What Was Changed

### Before (Original Structure)
- Single `products` table with `department` as a VARCHAR field
- No normalization of department data
- Potential data redundancy and inconsistency

### After (Refactored Structure)
- Separate `departments` table with proper normalization
- `products` table with `department_id` foreign key
- Referential integrity enforced through foreign key constraints
- Better data consistency and reduced redundancy

## Database Schema Changes

### New Departments Table
```sql
CREATE TABLE departments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Updated Products Table
```sql
CREATE TABLE products (
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
);
```

## Migration Process

The migration was performed using the `migration_departments.py` script, which:

1. **Backup**: Creates a backup of the original products table
2. **Extract**: Extracts unique department names from existing data
3. **Create**: Creates the new departments table
4. **Populate**: Inserts unique departments into the new table
5. **Update**: Adds department_id column to products table
6. **Migrate**: Updates products with correct department_id values
7. **Cleanup**: Removes the old department column
8. **Enforce**: Adds foreign key constraints
9. **Verify**: Validates the migration was successful

## API Changes

### New Endpoints
- `GET /api/departments` - Get all departments
- `GET /api/departments/{id}` - Get specific department by ID

### Updated Endpoints
- `GET /api/products` - Now includes department information and supports department filtering
- `GET /api/products/stats` - Now includes department statistics

### Response Format Changes
Products now return department information as an object:
```json
{
  "id": "product_id",
  "name": "Product Name",
  "department": {
    "id": 1,
    "name": "Women"
  },
  // ... other fields
}
```

### New Query Parameters
- `department_id` - Filter products by department ID
- `department_name` - Filter products by department name
- `include_count` - Include product count in departments response

## Benefits of the Refactoring

### Data Integrity
- Foreign key constraints prevent orphaned records
- Unique constraint on department names prevents duplicates
- Referential integrity ensures data consistency

### Performance
- Reduced storage through normalization
- Better indexing on department_id
- More efficient queries with proper JOINs

### Maintainability
- Easier to manage department information centrally
- Simpler to add department-related features
- Better separation of concerns

### Scalability
- Support for additional department attributes
- Easier to implement department-based features
- Better foundation for future enhancements

## Testing

The refactoring includes comprehensive testing:

1. **Migration Testing**: Verifies the migration process works correctly
2. **Structure Testing**: Ensures the new database structure is correct
3. **Data Integrity Testing**: Validates that all data was preserved
4. **API Testing**: Confirms all endpoints work with the new structure
5. **Query Testing**: Tests sample queries on the new structure

Run tests with:
```bash
python test_migration.py
```

## Rollback Plan

If needed, the original data can be restored from the `products_backup` table:

```sql
-- Restore original structure (if needed)
DROP TABLE products;
CREATE TABLE products AS SELECT * FROM products_backup;
```

## Files Modified

### Core Files
- `database_schema.sql` - Updated schema definition
- `app.py` - Updated API to work with new structure
- `database_manager.py` - Updated to handle new structure

### New Files
- `migration_departments.py` - Migration script
- `test_migration.py` - Test suite for migration
- `MIGRATION_README.md` - This documentation

## Usage Examples

### Get All Departments
```bash
curl http://localhost:5000/api/departments
```

### Get Products by Department
```bash
curl "http://localhost:5000/api/products?department_name=Women&limit=10"
```

### Get Department with Product Count
```bash
curl "http://localhost:5000/api/departments?include_count=true"
```

### Get Products with Department Info
```bash
curl http://localhost:5000/api/products/13842
```

## Sample Queries

### Products by Department
```sql
SELECT d.name, COUNT(*) as count
FROM products p
JOIN departments d ON p.department_id = d.id
GROUP BY d.name
ORDER BY count DESC;
```

### Average Price by Department
```sql
SELECT d.name, AVG(p.retail_price) as avg_price
FROM products p
JOIN departments d ON p.department_id = d.id
GROUP BY d.name
ORDER BY avg_price DESC;
```

### Products with Highest Profit Margin
```sql
SELECT p.name, d.name as department, 
       (p.retail_price - p.cost) as profit_margin
FROM products p
JOIN departments d ON p.department_id = d.id
ORDER BY (p.retail_price - p.cost) DESC;
```

## Future Enhancements

With the new structure, it's now easier to add:

1. **Department Management**: CRUD operations for departments
2. **Department Analytics**: Advanced reporting by department
3. **Department Hierarchies**: Parent-child department relationships
4. **Department Metadata**: Additional department attributes
5. **Department-based Permissions**: Access control by department

## Conclusion

The database refactoring successfully normalizes the department data while maintaining backward compatibility through the API. The new structure provides better data integrity, performance, and maintainability while setting the foundation for future enhancements. 
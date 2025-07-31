-- Database Schema for Products and Departments Tables
-- Milestone 4: Refactored to use separate departments table with foreign key relationships

-- Create departments table
CREATE TABLE IF NOT EXISTS departments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create products table with department foreign key
CREATE TABLE IF NOT EXISTS products (
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

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_departments_name ON departments(name);
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);
CREATE INDEX IF NOT EXISTS idx_products_brand ON products(brand);
CREATE INDEX IF NOT EXISTS idx_products_department_id ON products(department_id);
CREATE INDEX IF NOT EXISTS idx_products_distribution_center ON products(distribution_center_id);
CREATE INDEX IF NOT EXISTS idx_products_sku ON products(sku);

-- Create a view for products with calculated profit margin and department name
CREATE OR REPLACE VIEW products_with_margin AS
SELECT 
    p.*,
    d.name as department_name,
    (p.retail_price - p.cost) AS profit_margin,
    ROUND(((p.retail_price - p.cost) / p.retail_price * 100), 2) AS profit_margin_percentage
FROM products p
LEFT JOIN departments d ON p.department_id = d.id;

-- Sample queries for verification
-- 1. Count total products
-- SELECT COUNT(*) FROM products;

-- 2. Products by category
-- SELECT category, COUNT(*) as product_count FROM products GROUP BY category ORDER BY product_count DESC;

-- 3. Products by brand
-- SELECT brand, COUNT(*) as product_count FROM products GROUP BY brand ORDER BY product_count DESC;

-- 4. Products by department
-- SELECT d.name as department, COUNT(*) as product_count 
-- FROM products p 
-- JOIN departments d ON p.department_id = d.id 
-- GROUP BY d.name ORDER BY product_count DESC;

-- 5. Average profit margin by department
-- SELECT d.name as department, AVG(profit_margin_percentage) as avg_margin 
-- FROM products_with_margin pwm
-- GROUP BY d.name ORDER BY avg_margin DESC;

-- 6. Products with highest profit margin
-- SELECT name, brand, department_name, retail_price, cost, profit_margin_percentage 
-- FROM products_with_margin 
-- ORDER BY profit_margin_percentage DESC LIMIT 10; 
-- Database Schema for Products Table
-- Based on analysis of products.csv structure

CREATE TABLE IF NOT EXISTS products (
    id VARCHAR(255) PRIMARY KEY,
    cost DECIMAL(10, 4) NOT NULL,
    category VARCHAR(255) NOT NULL,
    name TEXT NOT NULL,
    brand VARCHAR(255) NOT NULL,
    retail_price DECIMAL(10, 4) NOT NULL,
    department VARCHAR(255) NOT NULL,
    sku VARCHAR(255) NOT NULL,
    distribution_center_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);
CREATE INDEX IF NOT EXISTS idx_products_brand ON products(brand);
CREATE INDEX IF NOT EXISTS idx_products_department ON products(department);
CREATE INDEX IF NOT EXISTS idx_products_distribution_center ON products(distribution_center_id);
CREATE INDEX IF NOT EXISTS idx_products_sku ON products(sku);

-- Create a view for products with calculated profit margin
CREATE OR REPLACE VIEW products_with_margin AS
SELECT 
    *,
    (retail_price - cost) AS profit_margin,
    ROUND(((retail_price - cost) / retail_price * 100), 2) AS profit_margin_percentage
FROM products;

-- Sample queries for verification
-- 1. Count total products
-- SELECT COUNT(*) FROM products;

-- 2. Products by category
-- SELECT category, COUNT(*) as product_count FROM products GROUP BY category ORDER BY product_count DESC;

-- 3. Products by brand
-- SELECT brand, COUNT(*) as product_count FROM products GROUP BY brand ORDER BY product_count DESC;

-- 4. Average profit margin by category
-- SELECT category, AVG(profit_margin_percentage) as avg_margin FROM products_with_margin GROUP BY category ORDER BY avg_margin DESC;

-- 5. Products with highest profit margin
-- SELECT name, brand, retail_price, cost, profit_margin_percentage FROM products_with_margin ORDER BY profit_margin_percentage DESC LIMIT 10; 
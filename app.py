#!/usr/bin/env python3
"""
Flask REST API for Products Database
Milestone 4: Updated to work with refactored database structure

Endpoints:
- GET /api/products - List all products (with pagination)
- GET /api/products/{id} - Get specific product by ID
- GET /api/departments - Get all departments
- GET /api/products/stats - Get product statistics
- Error handling for product not found, invalid ID, etc.
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend integration

# Database configuration
DATABASE_PATH = 'products.db'

def get_db_connection():
    """Create and return a database connection"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        return conn
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        return None

def format_product(row):
    """Format a database row into a product dictionary"""
    return {
        'id': row['id'],
        'name': row['name'],
        'brand': row['brand'],
        'category': row['category'],
        'department': {
            'id': row['department_id'],
            'name': row['department_name']
        },
        'cost': float(row['cost']),
        'retail_price': float(row['retail_price']),
        'sku': row['sku'],
        'distribution_center_id': int(row['distribution_center_id']),
        'profit_margin': float(row['retail_price']) - float(row['cost']),
        'profit_margin_percentage': round(((float(row['retail_price']) - float(row['cost'])) / float(row['retail_price']) * 100), 2)
    }

@app.route('/api/products', methods=['GET'])
def get_products():
    """
    GET /api/products - List all products with pagination
    
    Query parameters:
    - page: Page number (default: 1)
    - limit: Items per page (default: 10, max: 100)
    - category: Filter by category
    - brand: Filter by brand
    - department_id: Filter by department ID
    - department_name: Filter by department name
    """
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        limit = min(request.args.get('limit', 10, type=int), 100)  # Max 100 items per page
        category = request.args.get('category')
        brand = request.args.get('brand')
        department_id = request.args.get('department_id', type=int)
        department_name = request.args.get('department_name')
        
        # Calculate offset
        offset = (page - 1) * limit
        
        # Build query with JOIN to get department information
        query = """
            SELECT p.*, d.name as department_name 
            FROM products p 
            LEFT JOIN departments d ON p.department_id = d.id 
            WHERE 1=1
        """
        params = []
        
        if category:
            query += " AND p.category = ?"
            params.append(category)
        
        if brand:
            query += " AND p.brand = ?"
            params.append(brand)
            
        if department_id:
            query += " AND p.department_id = ?"
            params.append(department_id)
            
        if department_name:
            query += " AND d.name = ?"
            params.append(department_name)
        
        # Get total count
        count_query = query.replace("SELECT p.*, d.name as department_name", "SELECT COUNT(*)")
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500
            
        cursor = conn.cursor()
        cursor.execute(count_query, params)
        total_count = cursor.fetchone()[0]
        
        # Get paginated results
        query += " ORDER BY p.id LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        # Format products
        products = [format_product(row) for row in rows]
        
        # Calculate pagination info
        total_pages = (total_count + limit - 1) // limit
        has_next = page < total_pages
        has_prev = page > 1
        
        response = {
            'products': products,
            'pagination': {
                'page': page,
                'limit': limit,
                'total_count': total_count,
                'total_pages': total_pages,
                'has_next': has_next,
                'has_prev': has_prev
            },
            'filters': {
                'category': category,
                'brand': brand,
                'department_id': department_id,
                'department_name': department_name
            }
        }
        
        conn.close()
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Error in get_products: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/products/<product_id>', methods=['GET'])
def get_product(product_id):
    """
    GET /api/products/{id} - Get a specific product by ID
    """
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500
            
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.*, d.name as department_name 
            FROM products p 
            LEFT JOIN departments d ON p.department_id = d.id 
            WHERE p.id = ?
        """, (product_id,))
        row = cursor.fetchone()
        
        if row is None:
            conn.close()
            return jsonify({'error': 'Product not found'}), 404
        
        product = format_product(row)
        conn.close()
        
        return jsonify(product), 200
        
    except Exception as e:
        logger.error(f"Error in get_product: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/departments', methods=['GET'])
def get_departments():
    """
    GET /api/departments - Get all departments with product count
    
    Query parameters:
    - include_details: Include created_at and updated_at (default: false)
    """
    try:
        include_details = request.args.get('include_details', 'false').lower() == 'true'
        
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500
            
        cursor = conn.cursor()
        
        if include_details:
            # Include full details with timestamps
            cursor.execute("""
                SELECT d.id, d.name, d.created_at, d.updated_at, COUNT(p.id) as product_count
                FROM departments d
                LEFT JOIN products p ON d.id = p.department_id
                GROUP BY d.id, d.name, d.created_at, d.updated_at
                ORDER BY d.name
            """)
            departments = []
            for row in cursor.fetchall():
                departments.append({
                    'id': row[0],
                    'name': row[1],
                    'created_at': row[2],
                    'updated_at': row[3],
                    'product_count': row[4]
                })
        else:
            # Default format matching Milestone 5 requirements
            cursor.execute("""
                SELECT d.id, d.name, COUNT(p.id) as product_count
                FROM departments d
                LEFT JOIN products p ON d.id = p.department_id
                GROUP BY d.id, d.name
                ORDER BY d.name
            """)
            departments = []
            for row in cursor.fetchall():
                departments.append({
                    'id': row[0],
                    'name': row[1],
                    'product_count': row[2]
                })
        
        conn.close()
        return jsonify({'departments': departments}), 200
        
    except Exception as e:
        logger.error(f"Error in get_departments: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/departments/<int:department_id>', methods=['GET'])
def get_department(department_id):
    """
    GET /api/departments/{id} - Get a specific department by ID
    """
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500
            
        cursor = conn.cursor()
        cursor.execute("""
            SELECT d.id, d.name, d.created_at, d.updated_at, COUNT(p.id) as product_count
            FROM departments d
            LEFT JOIN products p ON d.id = p.department_id
            WHERE d.id = ?
            GROUP BY d.id, d.name, d.created_at, d.updated_at
        """, (department_id,))
        row = cursor.fetchone()
        
        if row is None:
            conn.close()
            return jsonify({'error': 'Department not found'}), 404
        
        department = {
            'id': row[0],
            'name': row[1],
            'created_at': row[2],
            'updated_at': row[3],
            'product_count': row[4]
        }
        
        conn.close()
        return jsonify(department), 200
        
    except Exception as e:
        logger.error(f"Error in get_department: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/departments/<int:department_id>/products', methods=['GET'])
def get_department_products(department_id):
    """
    GET /api/departments/{id}/products - Get all products in a department
    
    Query parameters:
    - page: Page number (default: 1)
    - limit: Items per page (default: 10, max: 100)
    - category: Filter by category within department
    - brand: Filter by brand within department
    """
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        limit = min(request.args.get('limit', 10, type=int), 100)  # Max 100 items per page
        category = request.args.get('category')
        brand = request.args.get('brand')
        
        # Calculate offset
        offset = (page - 1) * limit
        
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500
            
        cursor = conn.cursor()
        
        # First, verify the department exists
        cursor.execute("SELECT id, name FROM departments WHERE id = ?", (department_id,))
        dept_row = cursor.fetchone()
        
        if dept_row is None:
            conn.close()
            return jsonify({'error': 'Department not found'}), 404
        
        department_name = dept_row[1]
        
        # Build query for products in this department
        query = """
            SELECT p.*, d.name as department_name 
            FROM products p 
            LEFT JOIN departments d ON p.department_id = d.id 
            WHERE p.department_id = ?
        """
        params = [department_id]
        
        if category:
            query += " AND p.category = ?"
            params.append(category)
        
        if brand:
            query += " AND p.brand = ?"
            params.append(brand)
        
        # Get total count
        count_query = query.replace("SELECT p.*, d.name as department_name", "SELECT COUNT(*)")
        cursor.execute(count_query, params)
        total_count = cursor.fetchone()[0]
        
        if total_count == 0:
            conn.close()
            return jsonify({
                'department': department_name,
                'products': [],
                'pagination': {
                    'page': page,
                    'limit': limit,
                    'total_count': 0,
                    'total_pages': 0,
                    'has_next': False,
                    'has_prev': False
                },
                'filters': {
                    'category': category,
                    'brand': brand
                }
            }), 200
        
        # Get paginated results
        query += " ORDER BY p.id LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        # Format products
        products = [format_product(row) for row in rows]
        
        # Calculate pagination info
        total_pages = (total_count + limit - 1) // limit
        has_next = page < total_pages
        has_prev = page > 1
        
        response = {
            'department': department_name,
            'products': products,
            'pagination': {
                'page': page,
                'limit': limit,
                'total_count': total_count,
                'total_pages': total_pages,
                'has_next': has_next,
                'has_prev': has_prev
            },
            'filters': {
                'category': category,
                'brand': brand
            }
        }
        
        conn.close()
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Error in get_department_products: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/products/stats', methods=['GET'])
def get_product_stats():
    """
    GET /api/products/stats - Get product statistics
    """
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500
            
        cursor = conn.cursor()
        
        # Get basic stats
        cursor.execute("SELECT COUNT(*) FROM products")
        total_products = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT category) FROM products")
        total_categories = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT brand) FROM products")
        total_brands = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT department_id) FROM products")
        total_departments = cursor.fetchone()[0]
        
        cursor.execute("SELECT AVG(retail_price) FROM products")
        avg_price = cursor.fetchone()[0]
        
        cursor.execute("SELECT MIN(retail_price), MAX(retail_price) FROM products")
        min_price, max_price = cursor.fetchone()
        
        # Get top categories
        cursor.execute("""
            SELECT category, COUNT(*) as count 
            FROM products 
            GROUP BY category 
            ORDER BY count DESC 
            LIMIT 5
        """)
        top_categories = [{'category': row[0], 'count': row[1]} for row in cursor.fetchall()]
        
        # Get top brands
        cursor.execute("""
            SELECT brand, COUNT(*) as count 
            FROM products 
            GROUP BY brand 
            ORDER BY count DESC 
            LIMIT 5
        """)
        top_brands = [{'brand': row[0], 'count': row[1]} for row in cursor.fetchall()]
        
        # Get top departments
        cursor.execute("""
            SELECT d.name, COUNT(*) as count 
            FROM products p
            JOIN departments d ON p.department_id = d.id
            GROUP BY d.id, d.name 
            ORDER BY count DESC 
            LIMIT 5
        """)
        top_departments = [{'department': row[0], 'count': row[1]} for row in cursor.fetchall()]
        
        conn.close()
        
        stats = {
            'total_products': total_products,
            'total_categories': total_categories,
            'total_brands': total_brands,
            'total_departments': total_departments,
            'price_stats': {
                'average_price': round(float(avg_price), 2),
                'min_price': round(float(min_price), 2),
                'max_price': round(float(max_price), 2)
            },
            'top_categories': top_categories,
            'top_brands': top_brands,
            'top_departments': top_departments
        }
        
        return jsonify(stats), 200
        
    except Exception as e:
        logger.error(f"Error in get_product_stats: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/categories', methods=['GET'])
def get_categories():
    """
    GET /api/categories - Get all product categories
    """
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500
            
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT category FROM products ORDER BY category")
        categories = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        return jsonify({'categories': categories}), 200
        
    except Exception as e:
        logger.error(f"Error in get_categories: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/brands', methods=['GET'])
def get_brands():
    """
    GET /api/brands - Get all product brands
    """
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500
            
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT brand FROM products ORDER BY brand")
        brands = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        return jsonify({'brands': brands}), 200
        
    except Exception as e:
        logger.error(f"Error in get_brands: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({'error': 'Internal server error'}), 500

@app.route('/')
def home():
    """Home endpoint with API documentation"""
    return jsonify({
        'message': 'Products REST API (Refactored with Departments)',
        'version': '2.0.0',
        'endpoints': {
            'GET /api/products': 'List all products (with pagination and filters)',
            'GET /api/products/{id}': 'Get specific product by ID',
            'GET /api/products/stats': 'Get product statistics',
            'GET /api/departments': 'Get all departments with product count',
            'GET /api/departments/{id}': 'Get specific department details',
            'GET /api/departments/{id}/products': 'Get all products in a department',
            'GET /api/categories': 'Get all product categories',
            'GET /api/brands': 'Get all product brands'
        },
        'query_parameters': {
            'page': 'Page number (default: 1)',
            'limit': 'Items per page (default: 10, max: 100)',
            'category': 'Filter by category',
            'brand': 'Filter by brand',
            'department_id': 'Filter by department ID',
            'department_name': 'Filter by department name',
            'include_details': 'Include timestamps in departments response (true/false)'
        },
        'database_structure': {
            'products': 'Contains product information with department_id foreign key',
            'departments': 'Contains department information with proper normalization'
        }
    }), 200

if __name__ == '__main__':
    logger.info("Starting Products REST API (Refactored)...")
    logger.info("Available endpoints:")
    logger.info("  GET /api/products - List all products")
    logger.info("  GET /api/products/{id} - Get specific product")
    logger.info("  GET /api/products/stats - Get statistics")
    logger.info("  GET /api/departments - Get all departments with product count")
    logger.info("  GET /api/departments/{id} - Get specific department details")
    logger.info("  GET /api/departments/{id}/products - Get products in department")
    logger.info("  GET /api/categories - Get all categories")
    logger.info("  GET /api/brands - Get all brands")
    
    app.run(debug=True, host='0.0.0.0', port=5000) 
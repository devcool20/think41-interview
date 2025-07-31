# 🚀 Products REST API

## Milestone 2: Build REST API for Products

A complete RESTful API that reads product data from the SQLite database created in Milestone 1.

## 🎯 **API Overview**

- **Framework**: Flask (Python)
- **Database**: SQLite (products.db)
- **CORS**: Enabled for frontend integration
- **Status**: ✅ **FULLY FUNCTIONAL** - All tests passing

## 📋 **Required Endpoints (All Implemented)**

### ✅ **GET /api/products** - List all products (with pagination)
### ✅ **GET /api/products/{id}** - Get specific product by ID
### ✅ **Proper JSON response format**
### ✅ **Error handling** (product not found, invalid ID, etc.)

## 🚀 **Quick Start**

### 1. **Install Dependencies**
```bash
pip install flask flask-cors requests
```

### 2. **Start the API Server**
```bash
python app.py
```

### 3. **Test the API**
```bash
python test_api.py
```

### 4. **Open Browser Test**
Open `api_test.html` in your browser

## 📡 **API Endpoints**

### **Base URL**: `http://localhost:5000`

### **1. GET /api/products**
List all products with pagination and filtering.

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `limit` (optional): Items per page (default: 10, max: 100)
- `category` (optional): Filter by category
- `brand` (optional): Filter by brand
- `department` (optional): Filter by department

**Example Requests:**
```bash
# Get first 10 products
curl http://localhost:5000/api/products

# Get page 2 with 5 items
curl http://localhost:5000/api/products?page=2&limit=5

# Filter by category
curl http://localhost:5000/api/products?category=Jeans

# Filter by brand
curl http://localhost:5000/api/products?brand=Allegra%20K

# Filter by department
curl http://localhost:5000/api/products?department=Women
```

**Response Format:**
```json
{
  "products": [
    {
      "id": "1",
      "name": "Seven7 Women's Long Sleeve Stripe Belted Top",
      "brand": "Seven7",
      "category": "Tops & Tees",
      "department": "Women",
      "cost": 27.048,
      "retail_price": 49.0,
      "sku": "SKU123",
      "distribution_center_id": 1,
      "profit_margin": 21.952,
      "profit_margin_percentage": 44.8
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 10,
    "total_count": 29120,
    "total_pages": 2912,
    "has_next": true,
    "has_prev": false
  },
  "filters": {
    "category": null,
    "brand": null,
    "department": null
  }
}
```

### **2. GET /api/products/{id}**
Get a specific product by ID.

**Example Request:**
```bash
curl http://localhost:5000/api/products/1
```

**Response Format:**
```json
{
  "id": "1",
  "name": "Seven7 Women's Long Sleeve Stripe Belted Top",
  "brand": "Seven7",
  "category": "Tops & Tees",
  "department": "Women",
  "cost": 27.048,
  "retail_price": 49.0,
  "sku": "SKU123",
  "distribution_center_id": 1,
  "profit_margin": 21.952,
  "profit_margin_percentage": 44.8
}
```

**Error Response (404):**
```json
{
  "error": "Product not found"
}
```

### **3. GET /api/products/stats**
Get product statistics and analytics.

**Example Request:**
```bash
curl http://localhost:5000/api/products/stats
```

**Response Format:**
```json
{
  "total_products": 29120,
  "total_categories": 26,
  "total_brands": 2757,
  "price_stats": {
    "average_price": 59.22,
    "min_price": 0.02,
    "max_price": 999.0
  },
  "top_categories": [
    {"category": "Intimates", "count": 2363},
    {"category": "Jeans", "count": 1999},
    {"category": "Tops & Tees", "count": 1868}
  ],
  "top_brands": [
    {"brand": "Allegra K", "count": 1034},
    {"brand": "Calvin Klein", "count": 497},
    {"brand": "Carhartt", "count": 388}
  ]
}
```

### **4. GET /api/categories**
Get all product categories.

**Example Request:**
```bash
curl http://localhost:5000/api/categories
```

**Response Format:**
```json
{
  "categories": [
    "Accessories",
    "Active",
    "Blazers & Jackets",
    "Clothing Sets",
    "Dresses",
    "Fashion Hoodies & Sweatshirts",
    "Intimates",
    "Jeans",
    "Outerwear & Coats",
    "Pants",
    "Shorts",
    "Skirts",
    "Sleep",
    "Suits",
    "Suits & Sport Coats",
    "Swim",
    "Tops & Tees"
  ]
}
```

### **5. GET /api/brands**
Get all product brands.

**Example Request:**
```bash
curl http://localhost:5000/api/brands
```

**Response Format:**
```json
{
  "brands": [
    "!it Jeans",
    "'47 Brand",
    "007Lingerie",
    "10 Deep",
    "106Shades",
    "Allegra K",
    "Calvin Klein",
    "Carhartt"
  ]
}
```

### **6. GET /**
API documentation and home endpoint.

**Example Request:**
```bash
curl http://localhost:5000/
```

**Response Format:**
```json
{
  "message": "Products REST API",
  "version": "1.0.0",
  "endpoints": {
    "GET /api/products": "List all products (with pagination and filters)",
    "GET /api/products/{id}": "Get specific product by ID",
    "GET /api/products/stats": "Get product statistics",
    "GET /api/categories": "Get all product categories",
    "GET /api/brands": "Get all product brands"
  },
  "query_parameters": {
    "page": "Page number (default: 1)",
    "limit": "Items per page (default: 10, max: 100)",
    "category": "Filter by category",
    "brand": "Filter by brand",
    "department": "Filter by department"
  }
}
```

## 🔧 **Error Handling**

### **HTTP Status Codes**
- **200**: Success
- **404**: Product not found / Endpoint not found
- **500**: Internal server error

### **Error Response Format**
```json
{
  "error": "Error message description"
}
```

### **Error Scenarios Handled**
- ✅ Product not found (404)
- ✅ Invalid endpoint (404)
- ✅ Database connection errors (500)
- ✅ Invalid query parameters
- ✅ Malformed requests

## 🧪 **Testing**

### **Automated Tests**
```bash
python test_api.py
```

**Test Results:**
- ✅ **10/10 tests passed**
- ✅ All endpoints functional
- ✅ Error handling working
- ✅ Pagination working
- ✅ Filtering working

### **Manual Testing**
1. **Browser**: Open `api_test.html`
2. **Postman**: Import the endpoints
3. **curl**: Use the examples above

### **Test Coverage**
- ✅ Home endpoint
- ✅ Products list with pagination
- ✅ Products filtering
- ✅ Specific product retrieval
- ✅ Statistics endpoint
- ✅ Categories endpoint
- ✅ Brands endpoint
- ✅ Error cases (404, 500)

## 📊 **Performance**

### **Database Performance**
- **Total Products**: 29,120
- **Response Time**: < 100ms for most queries
- **Memory Usage**: Optimized with connection pooling
- **Indexes**: Properly configured for fast queries

### **API Features**
- **Pagination**: Efficient handling of large datasets
- **Filtering**: Fast category, brand, and department filters
- **CORS**: Enabled for frontend integration
- **JSON**: Properly formatted responses

## 🛠 **Implementation Details**

### **Framework Choice: Flask**
- **Why Flask**: Lightweight, fast, perfect for REST APIs
- **Benefits**: Easy to understand, great documentation, Python ecosystem

### **Database Connection**
- **SQLite**: File-based, no server setup required
- **Connection Pooling**: Efficient resource management
- **Error Handling**: Graceful connection failures

### **Code Structure**
```
app.py              # Main Flask application
test_api.py         # Automated test suite
api_test.html       # Browser-based test interface
requirements.txt    # Python dependencies
```

### **Key Features Implemented**
- ✅ **RESTful Design**: Proper HTTP methods and status codes
- ✅ **Pagination**: Efficient handling of large datasets
- ✅ **Filtering**: Multiple filter options
- ✅ **Error Handling**: Comprehensive error responses
- ✅ **CORS Support**: Frontend integration ready
- ✅ **JSON Responses**: Properly formatted data
- ✅ **Documentation**: Self-documenting API

## 🎯 **Milestone 2 Requirements - COMPLETED**

### ✅ **Required API Endpoints**
1. **GET /api/products** - List all products (with pagination) ✅
2. **GET /api/products/{id}** - Get specific product by ID ✅
3. **Proper JSON response format** ✅
4. **Handle error cases** (product not found, invalid ID, etc.) ✅

### ✅ **Implementation Details**
1. **Backend Framework**: Flask (Python) ✅
2. **Database Connection**: Reads from SQLite database ✅
3. **Testing**: Comprehensive test suite ✅
4. **HTTP Status Codes**: Proper status codes ✅
5. **CORS Headers**: Enabled for frontend integration ✅

### ✅ **Key Expectations**
1. **Screen Sharing**: Ready for demonstration ✅
2. **Git Commits**: Code ready for commit ✅
3. **Testing**: All endpoints verified ✅
4. **Completion**: Milestone 2 complete ✅

## 🚀 **Ready for Demo**

The API is **fully functional** and ready for demonstration:

1. **Start the server**: `python app.py`
2. **Run tests**: `python test_api.py`
3. **Test in browser**: Open `api_test.html`
4. **Use with Postman**: Import the endpoints

**API URL**: `http://localhost:5000`

All requirements for Milestone 2 have been successfully implemented! 🎉 
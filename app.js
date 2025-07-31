// Products Catalog Frontend Application
// Milestone 3: Build Frontend UI for Products

class ProductsApp {
    constructor() {
        this.apiBase = 'http://localhost:5000/api';
        this.currentPage = 1;
        this.currentLimit = 12;
        this.currentFilters = {};
        this.currentView = 'home';
        
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadInitialData();
    }

    bindEvents() {
        // Navigation
        document.getElementById('home-btn').addEventListener('click', () => this.showView('home'));
        document.getElementById('stats-btn').addEventListener('click', () => this.showView('stats'));
        document.getElementById('back-btn').addEventListener('click', () => this.showView('home'));

        // Search and filters
        document.getElementById('search-input').addEventListener('input', this.debounce(() => this.handleSearch(), 300));
        document.getElementById('category-filter').addEventListener('change', () => this.handleFilterChange());
        document.getElementById('brand-filter').addEventListener('change', () => this.handleFilterChange());
        document.getElementById('department-filter').addEventListener('change', () => this.handleFilterChange());

        // Pagination
        document.getElementById('prev-btn').addEventListener('click', () => this.previousPage());
        document.getElementById('next-btn').addEventListener('click', () => this.nextPage());
    }

    async loadInitialData() {
        try {
            this.showLoading();
            
            // Load categories and brands for filters
            await Promise.all([
                this.loadCategories(),
                this.loadBrands(),
                this.loadProducts()
            ]);
            
            this.hideLoading();
        } catch (error) {
            this.showError('Failed to load initial data. Please check if the API is running.');
            console.error('Initial data loading error:', error);
        }
    }

    async loadProducts() {
        try {
            const params = new URLSearchParams({
                page: this.currentPage,
                limit: this.currentLimit,
                ...this.currentFilters
            });

            const response = await fetch(`${this.apiBase}/products?${params}`);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            this.renderProducts(data);
            this.updatePagination(data.pagination);
            
        } catch (error) {
            this.showError('Failed to load products. Please try again.');
            console.error('Products loading error:', error);
        }
    }

    async loadCategories() {
        try {
            const response = await fetch(`${this.apiBase}/categories`);
            const data = await response.json();
            this.populateFilter('category-filter', data.categories);
        } catch (error) {
            console.error('Categories loading error:', error);
        }
    }

    async loadBrands() {
        try {
            const response = await fetch(`${this.apiBase}/brands`);
            const data = await response.json();
            this.populateFilter('brand-filter', data.brands);
        } catch (error) {
            console.error('Brands loading error:', error);
        }
    }

    async loadProductDetail(productId) {
        try {
            this.showLoading();
            
            const response = await fetch(`${this.apiBase}/products/${productId}`);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const product = await response.json();
            this.renderProductDetail(product);
            this.showView('detail');
            
            this.hideLoading();
        } catch (error) {
            this.showError('Failed to load product details.');
            console.error('Product detail loading error:', error);
        }
    }

    async loadStatistics() {
        try {
            this.showLoading();
            
            const response = await fetch(`${this.apiBase}/products/stats`);
            const stats = await response.json();
            this.renderStatistics(stats);
            
            this.hideLoading();
        } catch (error) {
            this.showError('Failed to load statistics.');
            console.error('Statistics loading error:', error);
        }
    }

    renderProducts(data) {
        const container = document.getElementById('products-container');
        
        if (data.products.length === 0) {
            container.innerHTML = `
                <div class="text-center" style="grid-column: 1 / -1; padding: 3rem;">
                    <i class="fas fa-search" style="font-size: 3rem; color: #6c757d; margin-bottom: 1rem;"></i>
                    <h3>No products found</h3>
                    <p>Try adjusting your search or filters.</p>
                </div>
            `;
            return;
        }

        container.innerHTML = data.products.map(product => `
            <div class="product-card" onclick="app.loadProductDetail('${product.id}')">
                <div class="product-image">
                    <i class="fas fa-tshirt"></i>
                </div>
                <div class="product-info">
                    <div class="product-name">${this.truncateText(product.name, 60)}</div>
                    <div class="product-brand">${product.brand}</div>
                    <div class="product-category">${product.category}</div>
                    <div class="product-price">$${product.retail_price.toFixed(2)}</div>
                    <div class="product-margin">Profit: $${product.profit_margin.toFixed(2)} (${product.profit_margin_percentage}%)</div>
                </div>
            </div>
        `).join('');
    }

    renderProductDetail(product) {
        const container = document.getElementById('product-detail');
        
        container.innerHTML = `
            <div class="detail-image">
                <i class="fas fa-tshirt"></i>
            </div>
            <div class="detail-content">
                <h1 class="detail-name">${product.name}</h1>
                <div class="detail-brand">by ${product.brand}</div>
                <div class="detail-category">${product.category}</div>
                <div class="detail-price">$${product.retail_price.toFixed(2)}</div>
                <div class="detail-margin">
                    Profit Margin: $${product.profit_margin.toFixed(2)} (${product.profit_margin_percentage}%)
                </div>
                <div class="detail-info">
                    <div class="info-item">
                        <div class="info-label">Product ID</div>
                        <div class="info-value">${product.id}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Cost</div>
                        <div class="info-value">$${product.cost.toFixed(2)}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Department</div>
                        <div class="info-value">${product.department}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">SKU</div>
                        <div class="info-value">${product.sku}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Distribution Center</div>
                        <div class="info-value">${product.distribution_center_id}</div>
                    </div>
                </div>
            </div>
        `;
    }

    renderStatistics(stats) {
        const container = document.getElementById('stats-container');
        
        container.innerHTML = `
            <div class="stat-card">
                <div class="stat-value">${stats.total_products.toLocaleString()}</div>
                <div class="stat-label">Total Products</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">${stats.total_categories}</div>
                <div class="stat-label">Categories</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">${stats.total_brands.toLocaleString()}</div>
                <div class="stat-label">Brands</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">$${stats.price_stats.average_price}</div>
                <div class="stat-label">Average Price</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">$${stats.price_stats.min_price}</div>
                <div class="stat-label">Lowest Price</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">$${stats.price_stats.max_price}</div>
                <div class="stat-label">Highest Price</div>
            </div>
        `;

        // Add top categories and brands
        container.innerHTML += `
            <div class="top-categories">
                <h3>Top Categories</h3>
                ${stats.top_categories.map(cat => `
                    <div class="category-item">
                        <span class="category-name">${cat.category}</span>
                        <span class="category-count">${cat.count}</span>
                    </div>
                `).join('')}
            </div>
            <div class="top-brands">
                <h3>Top Brands</h3>
                ${stats.top_brands.map(brand => `
                    <div class="brand-item">
                        <span class="brand-name">${brand.brand}</span>
                        <span class="brand-count">${brand.count}</span>
                    </div>
                `).join('')}
            </div>
        `;
    }

    populateFilter(filterId, options) {
        const select = document.getElementById(filterId);
        const currentValue = select.value;
        
        // Clear existing options except the first one
        select.innerHTML = select.options[0].outerHTML;
        
        // Add new options
        options.forEach(option => {
            const optionElement = document.createElement('option');
            optionElement.value = option;
            optionElement.textContent = option;
            select.appendChild(optionElement);
        });
        
        // Restore previous selection if it still exists
        if (currentValue && options.includes(currentValue)) {
            select.value = currentValue;
        }
    }

    updatePagination(pagination) {
        const paginationElement = document.getElementById('pagination');
        const pageInfo = document.getElementById('page-info');
        const prevBtn = document.getElementById('prev-btn');
        const nextBtn = document.getElementById('next-btn');

        if (pagination.total_pages <= 1) {
            paginationElement.classList.add('hidden');
            return;
        }

        paginationElement.classList.remove('hidden');
        pageInfo.textContent = `Page ${pagination.page} of ${pagination.total_pages}`;
        
        prevBtn.disabled = !pagination.has_prev;
        nextBtn.disabled = !pagination.has_next;
    }

    handleSearch() {
        const searchTerm = document.getElementById('search-input').value.trim();
        
        if (searchTerm) {
            // For now, we'll filter client-side since the API doesn't have search
            // In a real app, you'd send the search term to the API
            this.currentFilters = { ...this.currentFilters, search: searchTerm };
        } else {
            delete this.currentFilters.search;
        }
        
        this.currentPage = 1;
        this.loadProducts();
    }

    handleFilterChange() {
        const category = document.getElementById('category-filter').value;
        const brand = document.getElementById('brand-filter').value;
        const department = document.getElementById('department-filter').value;

        this.currentFilters = {};
        
        if (category) this.currentFilters.category = category;
        if (brand) this.currentFilters.brand = brand;
        if (department) this.currentFilters.department = department;

        this.currentPage = 1;
        this.loadProducts();
    }

    previousPage() {
        if (this.currentPage > 1) {
            this.currentPage--;
            this.loadProducts();
        }
    }

    nextPage() {
        this.currentPage++;
        this.loadProducts();
    }

    showView(view) {
        // Hide all views
        document.querySelectorAll('.view').forEach(v => v.classList.add('hidden'));
        
        // Show selected view
        document.getElementById(`${view}-view`).classList.remove('hidden');
        
        // Update navigation
        document.querySelectorAll('.nav-btn').forEach(btn => btn.classList.remove('active'));
        document.getElementById(`${view}-btn`).classList.add('active');
        
        this.currentView = view;
        
        // Load view-specific data
        if (view === 'stats') {
            this.loadStatistics();
        } else if (view === 'home') {
            this.loadProducts();
        }
    }

    showLoading() {
        document.getElementById('loading').classList.remove('hidden');
        document.getElementById('error').classList.add('hidden');
    }

    hideLoading() {
        document.getElementById('loading').classList.add('hidden');
    }

    showError(message) {
        this.hideLoading();
        document.getElementById('error').classList.remove('hidden');
        document.getElementById('error-message').textContent = message;
    }

    truncateText(text, maxLength) {
        if (text.length <= maxLength) return text;
        return text.substring(0, maxLength) + '...';
    }

    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
}

// Initialize the application when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new ProductsApp();
});

// Handle API connection errors
window.addEventListener('error', (event) => {
    if (event.target.tagName === 'SCRIPT' || event.target.tagName === 'LINK') {
        console.error('Resource loading error:', event);
    }
});

// Handle unhandled promise rejections
window.addEventListener('unhandledrejection', (event) => {
    console.error('Unhandled promise rejection:', event.reason);
}); 
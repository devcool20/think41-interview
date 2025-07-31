// Products Catalog Frontend Application
// Milestone 6: Add Department Page

class ProductsApp {
    constructor() {
        this.apiBase = 'http://localhost:5000/api';
        this.currentPage = 1;
        this.currentLimit = 12;
        this.currentFilters = {};
        this.currentView = 'home';
        this.currentDepartmentId = null;
        this.departments = [];
        
        this.init();
    }

    init() {
        this.bindEvents();
        this.handleInitialRoute();
        this.loadInitialData();
    }

    bindEvents() {
        // Navigation
        document.getElementById('home-btn').addEventListener('click', () => this.navigateToHome());
        document.getElementById('departments-btn').addEventListener('click', () => this.navigateToDepartments());
        document.getElementById('stats-btn').addEventListener('click', () => this.showView('stats'));
        document.getElementById('back-btn').addEventListener('click', () => this.goBack());
        document.getElementById('back-to-departments-btn').addEventListener('click', () => this.navigateToDepartments());

        // Search and filters (Home view)
        document.getElementById('search-input').addEventListener('input', this.debounce(() => this.handleSearch(), 300));
        document.getElementById('category-filter').addEventListener('change', () => this.handleFilterChange());
        document.getElementById('brand-filter').addEventListener('change', () => this.handleFilterChange());
        document.getElementById('department-filter').addEventListener('change', () => this.handleFilterChange());

        // Search and filters (Department view)
        document.getElementById('dept-search-input').addEventListener('input', this.debounce(() => this.handleDepartmentSearch(), 300));
        document.getElementById('dept-category-filter').addEventListener('change', () => this.handleDepartmentFilterChange());
        document.getElementById('dept-brand-filter').addEventListener('change', () => this.handleDepartmentFilterChange());

        // Pagination
        document.getElementById('prev-btn').addEventListener('click', () => this.previousPage());
        document.getElementById('next-btn').addEventListener('click', () => this.nextPage());
        document.getElementById('dept-prev-btn').addEventListener('click', () => this.previousDepartmentPage());
        document.getElementById('dept-next-btn').addEventListener('click', () => this.nextDepartmentPage());

        // Handle browser back/forward
        window.addEventListener('popstate', (event) => {
            this.handleRouteChange();
        });
    }

    handleInitialRoute() {
        const path = window.location.pathname;
        if (path.startsWith('/departments/')) {
            const departmentId = path.split('/')[2];
            if (departmentId && !isNaN(departmentId)) {
                this.currentDepartmentId = parseInt(departmentId);
                this.showDepartmentView(this.currentDepartmentId);
            } else {
                this.navigateToHome();
            }
        } else if (path === '/departments') {
            this.navigateToDepartments();
        } else {
            this.navigateToHome();
        }
    }

    handleRouteChange() {
        const path = window.location.pathname;
        if (path.startsWith('/departments/')) {
            const departmentId = path.split('/')[2];
            if (departmentId && !isNaN(departmentId)) {
                this.currentDepartmentId = parseInt(departmentId);
                this.showDepartmentView(this.currentDepartmentId);
            } else {
                this.navigateToHome();
            }
        } else if (path === '/departments') {
            this.navigateToDepartments();
        } else {
            this.navigateToHome();
        }
    }

    async loadInitialData() {
        try {
            this.showLoading();
            
            // Load departments first
            await this.loadDepartments();
            
            // Load other data
            await Promise.all([
                this.loadCategories(),
                this.loadBrands()
            ]);
            
            // Load view-specific data
            if (this.currentView === 'home') {
                await this.loadProducts();
            } else if (this.currentView === 'departments') {
                // Departments are already loaded
            } else if (this.currentView === 'department' && this.currentDepartmentId) {
                await this.loadDepartmentProducts();
            } else if (this.currentView === 'stats') {
                await this.loadStatistics();
            }
            
            this.hideLoading();
        } catch (error) {
            this.showError('Failed to load initial data. Please check if the API is running.');
            console.error('Initial data loading error:', error);
        }
    }

    async loadDepartments() {
        try {
            const response = await fetch(`${this.apiBase}/departments`);
            const data = await response.json();
            this.departments = data.departments;
            this.populateDepartmentFilter();
        } catch (error) {
            console.error('Departments loading error:', error);
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

    async loadDepartmentProducts() {
        try {
            const params = new URLSearchParams({
                page: this.currentPage,
                limit: this.currentLimit,
                ...this.currentFilters
            });

            const response = await fetch(`${this.apiBase}/departments/${this.currentDepartmentId}/products?${params}`);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            this.renderDepartmentProducts(data);
            this.updateDepartmentPagination(data.pagination);
            
        } catch (error) {
            this.showError('Failed to load department products. Please try again.');
            console.error('Department products loading error:', error);
        }
    }

    async loadCategories() {
        try {
            const response = await fetch(`${this.apiBase}/categories`);
            const data = await response.json();
            this.populateFilter('category-filter', data.categories);
            this.populateFilter('dept-category-filter', data.categories);
        } catch (error) {
            console.error('Categories loading error:', error);
        }
    }

    async loadBrands() {
        try {
            const response = await fetch(`${this.apiBase}/brands`);
            const data = await response.json();
            this.populateFilter('brand-filter', data.brands);
            this.populateFilter('dept-brand-filter', data.brands);
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

    renderDepartments() {
        const container = document.getElementById('departments-container');
        
        if (this.departments.length === 0) {
            container.innerHTML = `
                <div class="text-center" style="grid-column: 1 / -1; padding: 3rem;">
                    <i class="fas fa-th-large" style="font-size: 3rem; color: #6c757d; margin-bottom: 1rem;"></i>
                    <h3>No departments found</h3>
                    <p>There are no departments available at the moment.</p>
                </div>
            `;
            return;
        }

        container.innerHTML = this.departments.map(department => `
            <div class="department-card" onclick="app.navigateToDepartment(${department.id})">
                <div class="department-icon">
                    <i class="fas fa-tshirt"></i>
                </div>
                <div class="department-name">${department.name}</div>
                <div class="department-count">${department.product_count.toLocaleString()} products</div>
                <div class="department-description">
                    Browse all ${department.name.toLowerCase()} products in our catalog
                </div>
            </div>
        `).join('');
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

    renderDepartmentProducts(data) {
        const container = document.getElementById('department-products-container');
        
        if (data.products.length === 0) {
            container.innerHTML = `
                <div class="text-center" style="grid-column: 1 / -1; padding: 3rem;">
                    <i class="fas fa-search" style="font-size: 3rem; color: #6c757d; margin-bottom: 1rem;"></i>
                    <h3>No products found in this department</h3>
                    <p>Try adjusting your search or filters, or browse other departments.</p>
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
                        <div class="info-value">${product.department.name}</div>
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
                <div class="stat-value">${stats.total_departments || 0}</div>
                <div class="stat-label">Departments</div>
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

        // Add top categories, brands, and departments
        container.innerHTML += `
            <div class="top-categories">
                <h3>Top Categories</h3>
                ${(stats.top_categories || []).map(cat => `
                    <div class="category-item">
                        <span class="category-name">${cat.category}</span>
                        <span class="category-count">${cat.count}</span>
                    </div>
                `).join('')}
            </div>
            <div class="top-brands">
                <h3>Top Brands</h3>
                ${(stats.top_brands || []).map(brand => `
                    <div class="brand-item">
                        <span class="brand-name">${brand.brand}</span>
                        <span class="brand-count">${brand.count}</span>
                    </div>
                `).join('')}
            </div>
            ${stats.top_departments ? `
            <div class="top-departments">
                <h3>Top Departments</h3>
                ${stats.top_departments.map(dept => `
                    <div class="department-item">
                        <span class="department-name">${dept.name}</span>
                        <span class="department-count">${dept.product_count}</span>
                    </div>
                `).join('')}
            </div>
            ` : ''}
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

    populateDepartmentFilter() {
        const select = document.getElementById('department-filter');
        const currentValue = select.value;
        
        // Clear existing options except the first one
        select.innerHTML = select.options[0].outerHTML;
        
        // Add department options
        this.departments.forEach(dept => {
            const optionElement = document.createElement('option');
            optionElement.value = dept.name;
            optionElement.textContent = `${dept.name} (${dept.product_count})`;
            select.appendChild(optionElement);
        });
        
        // Restore previous selection if it still exists
        if (currentValue && this.departments.some(d => d.name === currentValue)) {
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

    updateDepartmentPagination(pagination) {
        const paginationElement = document.getElementById('dept-pagination');
        const pageInfo = document.getElementById('dept-page-info');
        const prevBtn = document.getElementById('dept-prev-btn');
        const nextBtn = document.getElementById('dept-next-btn');

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
            this.currentFilters = { ...this.currentFilters, search: searchTerm };
        } else {
            delete this.currentFilters.search;
        }
        
        this.currentPage = 1;
        this.loadProducts();
    }

    handleDepartmentSearch() {
        const searchTerm = document.getElementById('dept-search-input').value.trim();
        
        if (searchTerm) {
            this.currentFilters = { ...this.currentFilters, search: searchTerm };
        } else {
            delete this.currentFilters.search;
        }
        
        this.currentPage = 1;
        this.loadDepartmentProducts();
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

    handleDepartmentFilterChange() {
        const category = document.getElementById('dept-category-filter').value;
        const brand = document.getElementById('dept-brand-filter').value;

        this.currentFilters = {};
        
        if (category) this.currentFilters.category = category;
        if (brand) this.currentFilters.brand = brand;

        this.currentPage = 1;
        this.loadDepartmentProducts();
    }

    previousPage() {
        if (this.currentPage > 1) {
            this.currentPage--;
            if (this.currentView === 'department') {
                this.loadDepartmentProducts();
            } else {
                this.loadProducts();
            }
        }
    }

    nextPage() {
        this.currentPage++;
        if (this.currentView === 'department') {
            this.loadDepartmentProducts();
        } else {
            this.loadProducts();
        }
    }

    previousDepartmentPage() {
        if (this.currentPage > 1) {
            this.currentPage--;
            this.loadDepartmentProducts();
        }
    }

    nextDepartmentPage() {
        this.currentPage++;
        this.loadDepartmentProducts();
    }

    navigateToHome() {
        this.currentView = 'home';
        this.currentDepartmentId = null;
        this.currentPage = 1;
        this.currentFilters = {};
        
        // Update URL
        window.history.pushState({}, '', '/');
        
        this.showView('home');
        this.loadProducts();
    }

    navigateToDepartments() {
        this.currentView = 'departments';
        this.currentDepartmentId = null;
        
        // Update URL
        window.history.pushState({}, '', '/departments');
        
        this.showView('departments');
        this.renderDepartments();
    }

    navigateToDepartment(departmentId) {
        this.currentView = 'department';
        this.currentDepartmentId = departmentId;
        this.currentPage = 1;
        this.currentFilters = {};
        
        // Update URL
        window.history.pushState({}, '', `/departments/${departmentId}`);
        
        this.showDepartmentView(departmentId);
    }

    async showDepartmentView(departmentId) {
        this.currentView = 'department';
        this.currentDepartmentId = departmentId;
        
        // Find department info
        const department = this.departments.find(d => d.id === departmentId);
        if (department) {
            document.getElementById('department-name').textContent = department.name;
            document.getElementById('department-count').textContent = `${department.product_count.toLocaleString()} products`;
        }
        
        this.showView('department');
        await this.loadDepartmentProducts();
    }

    goBack() {
        if (this.currentView === 'detail') {
            if (this.currentView === 'department') {
                this.showDepartmentView(this.currentDepartmentId);
            } else {
                this.navigateToHome();
            }
        } else {
            this.navigateToHome();
        }
    }

    showView(view) {
        // Hide all views
        document.querySelectorAll('.view').forEach(v => v.classList.add('hidden'));
        
        // Show selected view
        document.getElementById(`${view}-view`).classList.remove('hidden');
        
        // Update navigation
        document.querySelectorAll('.nav-btn').forEach(btn => btn.classList.remove('active'));
        if (view === 'home') {
            document.getElementById('home-btn').classList.add('active');
        } else if (view === 'departments') {
            document.getElementById('departments-btn').classList.add('active');
        } else if (view === 'stats') {
            document.getElementById('stats-btn').classList.add('active');
        }
        
        this.currentView = view;
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
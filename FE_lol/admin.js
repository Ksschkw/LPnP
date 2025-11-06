// admin.js - Fixed with safe API call access
class AdminModule {
    constructor(app) {
        this.app = app;
        this.adminKey = null;
    }

    async loadAdmin() {
        const view = document.getElementById('adminView');
        
        try {
            // Check if user should have admin access
            const isAdmin = await this.verifyAdminAccess();
            
            if (!isAdmin) {
                view.innerHTML = `
                    <div class="error-state">
                        <i class="fas fa-lock"></i>
                        <h3>Admin Access Required</h3>
                        <p>You need administrator privileges to access this section.</p>
                    </div>
                `;
                return;
            }

            view.innerHTML = `
                <div class="view-header">
                    <h1>Admin Panel</h1>
                    <p>Platform management and analytics</p>
                </div>

                <div class="admin-container">
                    <div class="admin-tabs">
                        <button class="tab-btn active" data-tab="users">Users</button>
                        <button class="tab-btn" data-tab="categories">Categories</button>
                        <button class="tab-btn" data-tab="analytics">Analytics</button>
                    </div>

                    <div class="tab-content">
                        <div id="usersTab" class="tab-pane active">
                            <div class="admin-section">
                                <h2>User Management</h2>
                                <div class="admin-actions">
                                    <button class="btn btn-primary" onclick="window.adminModule.loadAllUsers()">
                                        Load All Users
                                    </button>
                                </div>
                                <div id="usersList" class="admin-list">
                                    <div class="empty-state">
                                        <i class="fas fa-users"></i>
                                        <p>Click "Load All Users" to view user data</p>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div id="categoriesTab" class="tab-pane">
                            <div class="admin-section">
                                <h2>Category Management</h2>
                                <div class="category-form">
                                    <div class="form-row">
                                        <div class="form-group">
                                            <input type="text" id="categoryName" placeholder="Category name">
                                        </div>
                                        <div class="form-group">
                                            <input type="text" id="categoryDescription" placeholder="Description (optional)">
                                        </div>
                                        <button class="btn btn-primary" onclick="window.adminModule.createCategory()">
                                            Create Category
                                        </button>
                                    </div>
                                </div>
                                <div id="categoriesList" class="admin-list">
                                    <!-- Categories will be loaded here -->
                                </div>
                            </div>
                        </div>

                        <div id="analyticsTab" class="tab-pane">
                            <div class="admin-section">
                                <h2>Platform Analytics</h2>
                                <div class="analytics-grid">
                                    <div class="analytics-card">
                                        <h3>Total Users</h3>
                                        <div class="analytics-value">-</div>
                                    </div>
                                    <div class="analytics-card">
                                        <h3>Active Services</h3>
                                        <div class="analytics-value">-</div>
                                    </div>
                                    <div class="analytics-card">
                                        <h3>Completed Jobs</h3>
                                        <div class="analytics-value">-</div>
                                    </div>
                                    <div class="analytics-card">
                                        <h3>Total Vouches</h3>
                                        <div class="analytics-value">-</div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `;

            this.setupAdminTabs();
            await this.loadCategories();

        } catch (error) {
            console.error('Error loading admin panel:', error);
            view.innerHTML = `
                <div class="error-state">
                    <i class="fas fa-exclamation-triangle"></i>
                    <h3>Failed to load admin panel</h3>
                    <p>${error.message || 'Please try again later'}</p>
                    <button onclick="window.adminModule.loadAdmin()" class="btn btn-primary">Retry</button>
                </div>
            `;
        }
    }

    // ... rest of the admin.js methods remain the same, but ensure they use this.app instead of window.app ...
// }

    async verifyAdminAccess() {
        // In a real application, you'd verify admin status with the backend
        // For now, we'll use a simple prompt for demo purposes
        if (!this.adminKey) {
            this.adminKey = prompt('Enter admin key to access this section:');
        }
        return !!this.adminKey;
    }

    setupAdminTabs() {
        const tabBtns = document.querySelectorAll('.admin-tabs .tab-btn');
        const tabPanes = document.querySelectorAll('.admin-container .tab-pane');

        tabBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                tabBtns.forEach(b => b.classList.remove('active'));
                tabPanes.forEach(p => p.classList.remove('active'));

                btn.classList.add('active');
                const tabName = btn.getAttribute('data-tab');
                document.getElementById(`${tabName}Tab`).classList.add('active');
            });
        });
    }

    async loadAllUsers() {
        try {
            const users = await this.app.apiCall(`/admin/categories/users?admin_key=${this.adminKey}&limit=50`);
            this.displayUsersList(users);
        } catch (error) {
            this.app.showToast('Failed to load users', 'error');
        }
    }

    displayUsersList(users) {
        const usersList = document.getElementById('usersList');
        if (users.length === 0) {
            usersList.innerHTML = '<div class="empty-state">No users found</div>';
            return;
        }

        usersList.innerHTML = `
            <div class="table-container">
                <table class="admin-table">
                    <thead>
                        <tr>
                            <th>Name</th>
                            <th>Phone</th>
                            <th>Email</th>
                            <th>Trust Score</th>
                            <th>Verified</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${users.map(user => `
                            <tr>
                                <td>${user.name}</td>
                                <td>${user.phone}</td>
                                <td>${user.email || '-'}</td>
                                <td>${user.trust_score}</td>
                                <td>${user.nin_verified ? 'Yes' : 'No'}</td>
                                <td>
                                    <button class="btn btn-outline btn-small" 
                                            onclick="window.adminModule.viewUserDetails('${user.id}')">
                                        View
                                    </button>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;
    }

    async loadCategories() {
        try {
            const categories = await this.app.apiCall(`/admin/categories/categories?admin_key=${this.adminKey}`);
            this.displayCategoriesList(categories);
        } catch (error) {
            console.error('Error loading categories:', error);
        }
    }

    displayCategoriesList(categories) {
        const categoriesList = document.getElementById('categoriesList');
        if (!categories || categories.length === 0) {
            categoriesList.innerHTML = '<div class="empty-state">No categories found</div>';
            return;
        }

        categoriesList.innerHTML = `
            <div class="table-container">
                <table class="admin-table">
                    <thead>
                        <tr>
                            <th>Name</th>
                            <th>Description</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${categories.map(category => `
                            <tr>
                                <td>${category.name}</td>
                                <td>${category.description || '-'}</td>
                                <td>
                                    <button class="btn btn-outline btn-small">
                                        Edit
                                    </button>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;
    }

    async createCategory() {
        const name = document.getElementById('categoryName').value;
        const description = document.getElementById('categoryDescription').value;

        if (!name) {
            this.app.showToast('Category name is required', 'warning');
            return;
        }

        try {
            await this.app.apiCall(`/admin/categories/categories?admin_key=${this.adminKey}&name=${encodeURIComponent(name)}&description=${encodeURIComponent(description || '')}`, 'POST');
            this.app.showToast('Category created successfully', 'success');
            
            // Clear form and refresh list
            document.getElementById('categoryName').value = '';
            document.getElementById('categoryDescription').value = '';
            await this.loadCategories();
            
        } catch (error) {
            this.app.showToast('Failed to create category', 'error');
        }
    }

    async viewUserDetails(userId) {
        this.app.showToast(`Viewing user details for ${userId}`, 'info');
        // Implement detailed user view
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.adminModule = new AdminModule(this.app);
});
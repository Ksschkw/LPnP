// app.js - Updated with proper module initialization
class LocaLeApp {
    constructor() {
        this.apiBaseUrl = 'http://127.0.0.1:8000'; // Use relative URLs
        this.currentUser = null;
        this.currentView = 'dashboard';
        this.modules = {};
        
        // Set global app instance immediately
        window.app = this;
        
        this.init();
    }

    async init() {
        // Initialize modules first
        this.initializeModules();
        
        // Then load user data and setup
        await this.loadUserData();
        this.setupEventListeners();
        this.setupNavigation();
        this.setupInterceptors();
        
        // Hide loading screen
        this.hideLoading();
    }

    initializeModules() {
        // Initialize all modules with proper app reference
        this.modules.auth = new AuthModule(this);
        this.modules.services = new ServicesModule(this);
        this.modules.jobs = new JobsModule(this);
        this.modules.vouches = new VouchesModule(this);
        this.modules.admin = new AdminModule(this);
        
        // Also set on window for global access
        window.authModule = this.modules.auth;
        window.servicesModule = this.modules.services;
        window.jobsModule = this.modules.jobs;
        window.vouchesModule = this.modules.vouches;
        window.adminModule = this.modules.admin;
    }

    async loadUserData() {
        const token = this.getToken();
        if (token) {
            try {
                this.currentUser = await this.apiCall('/users/me', 'GET');
                this.updateUI();
                this.showApp();
            } catch (error) {
                this.clearAuth();
                this.showLanding();
            }
        } else {
            this.showLanding();
        }
    }

    setupEventListeners() {
        // Authentication events
        document.getElementById('loginBtn')?.addEventListener('click', () => this.showLogin());
        document.getElementById('registerBtn')?.addEventListener('click', () => this.showRegister());
        document.getElementById('heroLoginBtn')?.addEventListener('click', () => this.showLogin());
        document.getElementById('logoutBtn')?.addEventListener('click', () => this.logout());

        // Modal events
        document.querySelectorAll('.modal-close').forEach(btn => {
            btn.addEventListener('click', (e) => this.closeModal(e.target.closest('.modal')));
        });

        // Auth form switching
        document.getElementById('showRegister')?.addEventListener('click', (e) => {
            e.preventDefault();
            this.showRegister();
        });
        document.getElementById('showLogin')?.addEventListener('click', (e) => {
            e.preventDefault();
            this.showLogin();
        });

        // Close modal on outside click
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal')) {
                this.closeModal(e.target);
            }
        });
    }

    setupNavigation() {
        // Navigation links
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const view = link.getAttribute('data-view');
                this.showView(view);
            });
        });

        // User dropdown
        const userDropdown = document.querySelector('.user-dropdown');
        const dropdownMenu = document.querySelector('.dropdown-menu');
        
        userDropdown?.addEventListener('click', (e) => {
            e.stopPropagation();
            dropdownMenu.classList.toggle('show');
        });

        document.addEventListener('click', () => {
            dropdownMenu?.classList.remove('show');
        });
    }

    setupInterceptors() {
        // Global error handling
        window.addEventListener('unhandledrejection', (event) => {
            console.error('Unhandled promise rejection:', event.reason);
            this.showToast('An unexpected error occurred', 'error');
        });

        // Network status monitoring
        window.addEventListener('online', () => {
            this.showToast('Connection restored', 'success');
        });

        window.addEventListener('offline', () => {
            this.showToast('You are offline', 'warning');
        });
    }

    // View Management
    showView(viewName) {
        // Hide all views
        document.querySelectorAll('.view').forEach(view => {
            view.classList.remove('active');
        });

        // Remove active class from all nav links
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
        });

        // Show target view
        const targetView = document.getElementById(`${viewName}View`);
        const targetLink = document.querySelector(`[data-view="${viewName}"]`);
        
        if (targetView) {
            targetView.classList.add('active');
            targetLink?.classList.add('active');
            this.currentView = viewName;
            
            // Load view-specific content
            this.loadViewContent(viewName);
        }
    }

    async loadViewContent(viewName) {
        const view = document.getElementById(`${viewName}View`);
        if (!view) return;

        // Show loading state
        view.innerHTML = `
            <div class="view-header">
                <h1>${viewName.charAt(0).toUpperCase() + viewName.slice(1)}</h1>
                <p>Loading...</p>
            </div>
            <div class="loading-content">
                <div class="loading-spinner"></div>
            </div>
        `;

        try {
            // Use the modules from this.modules to ensure they're properly initialized
            switch (viewName) {
                case 'dashboard':
                    await this.loadDashboard();
                    break;
                case 'services':
                    await this.modules.services.loadServices();
                    break;
                case 'jobs':
                    await this.modules.jobs.loadJobs();
                    break;
                case 'vouches':
                    await this.modules.vouches.loadVouches();
                    break;
                case 'admin':
                    await this.modules.admin.loadAdmin();
                    break;
                case 'profile':
                    await this.loadProfile();
                    break;
            }
        } catch (error) {
            console.error(`Error loading ${viewName}:`, error);
            this.showToast(`Failed to load ${viewName}: ${error.message}`, 'error');
        }
    }

    async loadDashboard() {
        const view = document.getElementById('dashboardView');
        
        try {
            // Fetch recent data
            const [services, myServices, jobRequests, jobOffers] = await Promise.all([
                this.apiCall('/services/?limit=6'),
                this.apiCall('/services/my'),
                this.apiCall('/jobs/my-requests'),
                this.apiCall('/jobs/my-offers')
            ]);

            view.innerHTML = `
                <div class="view-header">
                    <h1>Dashboard</h1>
                    <p>Welcome back, ${this.currentUser.name}!</p>
                </div>
                
                <div class="dashboard-grid">
                    <!-- Stats Cards -->
                    <div class="stats-grid">
                        <div class="stat-card">
                            <div class="stat-icon">
                                <i class="fas fa-concierge-bell"></i>
                            </div>
                            <div class="stat-info">
                                <h3>${myServices.length}</h3>
                                <p>My Services</p>
                            </div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-icon">
                                <i class="fas fa-briefcase"></i>
                            </div>
                            <div class="stat-info">
                                <h3>${jobRequests.length}</h3>
                                <p>Job Requests</p>
                            </div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-icon">
                                <i class="fas fa-handshake"></i>
                            </div>
                            <div class="stat-info">
                                <h3>${jobOffers.length}</h3>
                                <p>Job Offers</p>
                            </div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-icon">
                                <i class="fas fa-star"></i>
                            </div>
                            <div class="stat-info">
                                <h3>${this.currentUser.trust_score}</h3>
                                <p>Trust Score</p>
                            </div>
                        </div>
                    </div>

                    <!-- Quick Actions -->
                    <div class="action-cards">
                        <div class="action-card" onclick="app.showView('services')">
                            <i class="fas fa-plus"></i>
                            <h3>Create Service</h3>
                            <p>Offer your skills to the community</p>
                        </div>
                        <div class="action-card" onclick="app.showView('services')">
                            <i class="fas fa-search"></i>
                            <h3>Find Services</h3>
                            <p>Discover local service providers</p>
                        </div>
                        <div class="action-card" onclick="app.showView('jobs')">
                            <i class="fas fa-tasks"></i>
                            <h3>Manage Jobs</h3>
                            <p>View your requests and offers</p>
                        </div>
                    </div>

                    <!-- Recent Services -->
                    <div class="recent-section">
                        <h2>Recent Services</h2>
                        <div class="services-grid">
                            ${services.map(service => this.renderServiceCard(service)).join('')}
                        </div>
                    </div>
                </div>
            `;
        } catch (error) {
            view.innerHTML = `
                <div class="view-header">
                    <h1>Dashboard</h1>
                    <p>Welcome back, ${this.currentUser.name}!</p>
                </div>
                <div class="error-state">
                    <i class="fas fa-exclamation-triangle"></i>
                    <h3>Failed to load dashboard data</h3>
                    <button onclick="app.loadDashboard()" class="btn btn-primary">Retry</button>
                </div>
            `;
        }
    }

    // Update the service card rendering to use safe method calls
    // Update the service card rendering to use safe method calls
    renderServiceCard(service) {
        return `
            <div class="service-card" onclick="app.showServiceDetail('${service.id}')">
                <div class="service-header">
                    <h3>${service.title}</h3>
                    <span class="price-tag">$${service.base_price}</span>
                </div>
                <p class="service-description">${service.description || 'No description provided'}</p>
                <div class="service-meta">
                    <span class="trust-badge">
                        <i class="fas fa-star"></i> ${service.trust_points}
                    </span>
                    <span class="availability ${service.is_available_now ? 'available' : 'unavailable'}">
                        ${service.is_available_now ? 'Available Now' : 'Not Available'}
                    </span>
                </div>
            </div>
        `;
    }

    // Add this method to handle service detail clicks safely
    async showServiceDetail(serviceId) {
        try {
            if (this.modules.services && this.modules.services.showServiceDetail) {
                await this.modules.services.showServiceDetail(serviceId);
            } else {
                this.showToast('Service details feature is not available yet', 'info');
            }
        } catch (error) {
            console.error('Error showing service detail:', error);
            this.showToast('Failed to load service details', 'error');
        }
    }

    // Add profile loading method
    async loadProfile() {
        const view = document.getElementById('profileView');
        try {
            view.innerHTML = `
                <div class="view-header">
                    <h1>My Profile</h1>
                    <p>Manage your account information</p>
                </div>
                <div class="profile-container">
                    <div class="profile-card">
                        <h2>Profile Information</h2>
                        <div class="profile-info">
                            <div class="info-item">
                                <label>Name:</label>
                                <span>${this.currentUser.name}</span>
                            </div>
                            <div class="info-item">
                                <label>Phone:</label>
                                <span>${this.currentUser.phone}</span>
                            </div>
                            <div class="info-item">
                                <label>Email:</label>
                                <span>${this.currentUser.email || 'Not provided'}</span>
                            </div>
                            <div class="info-item">
                                <label>Trust Score:</label>
                                <span>${this.currentUser.trust_score}</span>
                            </div>
                            <div class="info-item">
                                <label>Verification Level:</label>
                                <span>${this.currentUser.verification_level}</span>
                            </div>
                        </div>
                        <button class="btn btn-primary" onclick="app.showEditProfile()">
                            Edit Profile
                        </button>
                    </div>
                </div>
            `;
        } catch (error) {
            console.error('Error loading profile:', error);
            view.innerHTML = `
                <div class="error-state">
                    <i class="fas fa-exclamation-triangle"></i>
                    <h3>Failed to load profile</h3>
                    <p>${error.message}</p>
                    <button onclick="app.loadProfile()" class="btn btn-primary">Retry</button>
                </div>
            `;
        }
    }

    showEditProfile() {
        this.showToast('Edit profile feature coming soon', 'info');
    }
// }

    // Authentication Methods
    showLogin() {
        this.showModal('loginModal');
    }

    showRegister() {
        this.showModal('registerModal');
    }

    async login(phone, password) {
        try {
            const response = await this.apiCall('/users/login', 'POST', {
                phone,
                password
            });

            this.setToken(response.access_token);
            this.currentUser = response;
            this.updateUI();
            this.showApp();
            this.closeAllModals();
            this.showToast('Login successful!', 'success');
            
        } catch (error) {
            this.handleAuthError(error, 'login');
        }
    }

    async register(userData) {
        try {
            const response = await this.apiCall('/users/', 'POST', userData);
            
            // Auto-login after registration
            await this.login(userData.phone, userData.password);
            
        } catch (error) {
            this.handleAuthError(error, 'registration');
        }
    }

    async logout() {
        this.clearAuth();
        this.showLanding();
        this.showToast('Logged out successfully', 'success');
    }

    // UI Management
    showLanding() {
        document.getElementById('landingPage').classList.remove('hidden');
        document.getElementById('app').classList.add('hidden');
    }

    showApp() {
        document.getElementById('landingPage').classList.add('hidden');
        document.getElementById('app').classList.remove('hidden');
        this.showView('dashboard');
    }

    hideLoading() {
        document.getElementById('loadingScreen').style.display = 'none';
    }

    showModal(modalId) {
        const modal = document.getElementById(modalId);
        modal.style.display = 'flex';
        setTimeout(() => modal.classList.add('show'), 10);
    }

    closeModal(modal) {
        modal.classList.remove('show');
        setTimeout(() => modal.style.display = 'none', 300);
    }

    closeAllModals() {
        document.querySelectorAll('.modal').forEach(modal => this.closeModal(modal));
    }

    updateUI() {
        if (this.currentUser) {
            document.getElementById('userName').textContent = this.currentUser.name;
            if (this.currentUser.avatar_url) {
                document.getElementById('userAvatar').src = this.currentUser.avatar_url;
            }
        }
    }

    // API Utilities
    // async apiCall(endpoint, method = 'GET', data = null) {
    // In app.js - Update the apiCall method for better debugging
    async apiCall(endpoint, method = 'GET', data = null) {
        const url = `${this.apiBaseUrl}${endpoint}`;
        const options = {
            method,
            headers: {
                'Content-Type': 'application/json',
            },
        };

        const token = this.getToken();
        if (token) {
            options.headers['Authorization'] = `Bearer ${token}`;
        }

        if (data && method !== 'GET') {
            options.body = JSON.stringify(data);
        }

        console.log(`API Call: ${method} ${url}`, data); // Debug log

        try {
            const response = await fetch(url, options);
            
            console.log(`API Response: ${response.status} ${response.statusText}`); // Debug log

            if (!response.ok) {
                const errorText = await response.text();
                console.error('API Error Response:', errorText); // Debug log
                
                let errorData;
                try {
                    errorData = JSON.parse(errorText);
                } catch {
                    errorData = { detail: errorText || response.statusText };
                }

                throw {
                    status: response.status,
                    message: errorData.detail || response.statusText,
                    data: errorData
                };
            }

            if (response.status === 204) {
                return null; // No content
            }

            const responseData = await response.json();
            console.log('API Success Response:', responseData); // Debug log
            return responseData;

        } catch (error) {
            console.error('API Call Failed:', error); // Debug log
            throw error;
        }
    }

    getToken() {
        return localStorage.getItem('locale_token');
    }

    setToken(token) {
        localStorage.setItem('locale_token', token);
    }

    clearAuth() {
        localStorage.removeItem('locale_token');
        this.currentUser = null;
    }

    // Error Handling
    handleAuthError(error, context) {
        let message = `Failed to ${context}`;
        
        if (error.status === 400 || error.status === 401) {
            message = 'Invalid phone number or password';
        } else if (error.status === 409) {
            message = 'Phone number already registered';
        } else if (error.data?.detail) {
            message = Array.isArray(error.data.detail) 
                ? error.data.detail[0].msg 
                : error.data.detail;
        }

        this.showToast(message, 'error');
    }

    // Toast Notifications
    showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.innerHTML = `
            <div class="toast-content">
                <i class="fas fa-${this.getToastIcon(type)}"></i>
                <span>${message}</span>
            </div>
            <button class="toast-close">&times;</button>
        `;

        const container = document.getElementById('toastContainer');
        container.appendChild(toast);

        // Animate in
        setTimeout(() => toast.classList.add('show'), 10);

        // Auto remove
        const autoRemove = setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, 5000);

        // Manual close
        toast.querySelector('.toast-close').addEventListener('click', () => {
            clearTimeout(autoRemove);
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        });
    }

    getToastIcon(type) {
        const icons = {
            success: 'check-circle',
            error: 'exclamation-circle',
            warning: 'exclamation-triangle',
            info: 'info-circle'
        };
        return icons[type] || 'info-circle';
    }
}

// Initialize app when DOM is loaded
let app;
document.addEventListener('DOMContentLoaded', () => {
    app = new LocaLeApp();
    
    // Setup auth form handlers
    // Setup auth form handlers
    document.getElementById('loginForm')?.addEventListener('submit', async (e) => {
        e.preventDefault();
        const phoneInput = document.getElementById('loginPhone');
        const rawPhone = window.authModule.getRawPhoneNumber(phoneInput);
        const password = document.getElementById('loginPassword').value;
        
        console.log('Login attempt with phone:', rawPhone); // Debug log
        
        await app.login(rawPhone, password);
    });

    document.getElementById('registerForm')?.addEventListener('submit', async (e) => {
        e.preventDefault();
        const phoneInput = document.getElementById('registerPhone');
        const rawPhone = window.authModule.getRawPhoneNumber(phoneInput);
        
        const formData = {
            name: document.getElementById('registerName').value,
            email: document.getElementById('registerEmail').value || null,
            phone: rawPhone, // Use raw phone without spaces
            password: document.getElementById('registerPassword').value
        };
        
        console.log('Register attempt with phone:', formData.phone); // Debug log
        
        await app.register(formData);
    });
});

// Initialize app when DOM is loaded - SIMPLIFIED
document.addEventListener('DOMContentLoaded', () => {
    new LocaLeApp();
});

// Make app globally available for onclick handlers
window.app = app;
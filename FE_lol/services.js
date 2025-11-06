// services.js - Fixed with safe API call access
class ServicesModule {
    constructor(app) {
        this.app = app;
        this.currentLocation = null;
        this.locationInput = null;
        
        // Initialize location services after a brief delay to ensure app is ready
        setTimeout(() => {
            this.initLocationServices();
        }, 100);
    }

    async initLocationServices() {
        try {
            await this.loadCurrentLocation();
            this.setupLocationAutocomplete();
        } catch (error) {
            console.warn('Location services not available:', error);
        }
    }

    async loadCurrentLocation() {
        try {
            const position = await Utils.getCurrentLocation();
            this.currentLocation = {
                lat: position.latitude,
                lng: position.longitude,
                name: await Utils.getLocationName(position.latitude, position.longitude)
            };
            return this.currentLocation;
        } catch (error) {
            console.error('Error getting current location:', error);
            this.app.showToast('Unable to get your location. Please enable location services.', 'warning');
            return null;
        }
    }

    async loadServices() {
        const view = document.getElementById('servicesView');
        
        try {
            // Use this.app for API calls instead of window.app
            const [services, myServices, categories] = await Promise.all([
                this.app.apiCall('/services/?limit=20'),
                this.app.apiCall('/services/my'),
                this.getCategories()
            ]);

            view.innerHTML = `
                <div class="view-header">
                    <div class="header-actions">
                        <h1>Services</h1>
                        <button class="btn btn-primary" onclick="window.servicesModule.showCreateServiceForm()">
                            <i class="fas fa-plus"></i> Create Service
                        </button>
                    </div>
                    <p>Discover and offer local services</p>
                </div>

                <div class="services-container">
                    <!-- Search and Filters -->
                    <div class="search-section">
                        <div class="search-box">
                            <i class="fas fa-search"></i>
                            <input type="text" id="serviceSearch" placeholder="Search services by category or location...">
                            <button class="btn btn-primary" onclick="window.servicesModule.searchServices()">
                                Search
                            </button>
                        </div>
                        
                        <div class="filters">
                            <div class="filter-group">
                                <label for="maxPrice">Max Price</label>
                                <input type="number" id="maxPrice" placeholder="Any price">
                            </div>
                            <div class="filter-group">
                                <label for="minTrust">Min Trust Score</label>
                                <input type="number" id="minTrust" placeholder="0" min="0" max="100">
                            </div>
                            <div class="filter-group">
                                <label for="maxDistance">Max Distance (km)</label>
                                <input type="number" id="maxDistance" value="10" min="1" max="100">
                            </div>
                        </div>
                    </div>

                    <!-- My Services -->
                    <div class="section">
                        <h2>My Services</h2>
                        ${myServices.length ? `
                            <div class="services-grid">
                                ${myServices.map(service => this.renderServiceCard(service, true)).join('')}
                            </div>
                        ` : `
                            <div class="empty-state">
                                <i class="fas fa-concierge-bell"></i>
                                <h3>No services yet</h3>
                                <p>Create your first service to start earning</p>
                                <button class="btn btn-primary" onclick="window.servicesModule.showCreateServiceForm()">
                                    Create Service
                                </button>
                            </div>
                        `}
                    </div>

                    <!-- All Services -->
                    <div class="section">
                        <h2>Available Services</h2>
                        ${services.length ? `
                            <div class="services-grid">
                                ${services.map(service => this.renderServiceCard(service)).join('')}
                            </div>
                        ` : `
                            <div class="empty-state">
                                <i class="fas fa-search"></i>
                                <h3>No services found</h3>
                                <p>Try adjusting your search filters</p>
                            </div>
                        `}
                    </div>
                </div>

                <!-- Create Service Modal -->
                <div id="createServiceModal" class="modal">
                    <div class="modal-content modal-large">
                        <div class="modal-header">
                            <h2>Create New Service</h2>
                            <button class="modal-close">&times;</button>
                        </div>
                        <form id="createServiceForm" class="service-form">
                            <div class="form-row">
                                <div class="form-group">
                                    <label for="serviceTitle">Service Title *</label>
                                    <input type="text" id="serviceTitle" required>
                                </div>
                                <div class="form-group">
                                    <label for="serviceCategory">Category *</label>
                                    <input type="text" id="serviceCategory" required list="categoryList">
                                    <datalist id="categoryList"></datalist>
                                </div>
                            </div>
                            
                            <div class="form-group">
                                <label for="serviceDescription">Description</label>
                                <textarea id="serviceDescription" rows="3" placeholder="Describe your service..."></textarea>
                            </div>

                            <div class="form-row">
                                <div class="form-group">
                                    <label for="serviceBasePrice">Base Price ($) *</label>
                                    <input type="number" id="serviceBasePrice" step="0.01" min="0" required>
                                </div>
                                <div class="form-group">
                                    <label for="serviceHourlyRate">Hourly Rate ($)</label>
                                    <input type="number" id="serviceHourlyRate" step="0.01" min="0">
                                </div>
                            </div>

                            <div class="form-row">
                                <div class="form-group">
                                    <label for="serviceRadius">Service Radius (km) *</label>
                                    <input type="number" id="serviceRadius" value="10" min="1" max="100" required>
                                </div>
                                <div class="form-group">
                                    <label for="serviceLocation">Current Location</label>
                                    <div class="location-input-group">
                                        <input type="text" id="serviceLocation" class="location-input" 
                                               placeholder="Click to set location">
                                        <button type="button" class="btn btn-outline btn-small" 
                                                onclick="window.servicesModule.useCurrentLocation()">
                                            <i class="fas fa-location-arrow"></i>
                                        </button>
                                    </div>
                                </div>
                            </div>

                            <div class="form-group">
                                <label class="checkbox-label">
                                    <input type="checkbox" id="serviceAvailableNow" checked>
                                    <span class="checkmark"></span>
                                    Available for immediate work
                                </label>
                            </div>

                            <div class="form-actions">
                                <button type="button" class="btn btn-outline" onclick="app.closeModal(document.getElementById('createServiceModal'))">
                                    Cancel
                                </button>
                                <button type="submit" class="btn btn-primary">
                                    Create Service
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            `;

            this.loadCategoriesList();
            this.setupServiceEventListeners();

        } catch (error) {
            console.error('Error loading services:', error);
            view.innerHTML = `
                <div class="error-state">
                    <i class="fas fa-exclamation-triangle"></i>
                    <h3>Failed to load services</h3>
                    <p>${error.message || 'Please try again later'}</p>
                    <button onclick="window.servicesModule.loadServices()" class="btn btn-primary">Retry</button>
                </div>
            `;
        }
    }

    renderServiceCard(service, isOwnService = false) {
        return `
            <div class="service-card ${isOwnService ? 'own-service' : ''}" 
                 onclick="window.servicesModule.showServiceDetail('${service.id}')">
                <div class="service-header">
                    <h3>${Utils.sanitizeHTML(service.title)}</h3>
                    <span class="price-tag">$${service.base_price}</span>
                </div>
                
                <p class="service-description">${service.description ? Utils.sanitizeHTML(service.description) : 'No description provided'}</p>
                
                <div class="service-meta">
                    <div class="meta-item">
                        <i class="fas fa-map-marker-alt"></i>
                        <span>${service.current_location || 'Remote'}</span>
                    </div>
                    <div class="meta-item">
                        <i class="fas fa-clock"></i>
                        <span>${service.service_radius_km}km radius</span>
                    </div>
                </div>

                <div class="service-footer">
                    <div class="trust-info">
                        <span class="trust-score">
                            <i class="fas fa-star"></i> ${service.trust_points}
                        </span>
                        <span class="completion-count">
                            <i class="fas fa-check-circle"></i> ${service.completion_count}
                        </span>
                    </div>
                    <div class="availability ${service.is_available_now ? 'available' : 'unavailable'}">
                        ${service.is_available_now ? 'Available' : 'Busy'}
                    </div>
                </div>

                ${isOwnService ? `
                    <div class="service-actions">
                        <button class="btn btn-outline btn-small" onclick="event.stopPropagation(); window.servicesModule.editService('${service.id}')">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-outline btn-small" onclick="event.stopPropagation(); window.servicesModule.deleteService('${service.id}')">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                ` : ''}
            </div>
        `;
    }

    async showCreateServiceForm() {
        const modal = document.getElementById('createServiceModal');
        this.app.showModal('createServiceModal');
        
        // Pre-fill location if available
        if (this.currentLocation) {
            document.getElementById('serviceLocation').value = this.currentLocation.name;
        }
    }

    async useCurrentLocation() {
        const location = await this.loadCurrentLocation();
        if (location) {
            document.getElementById('serviceLocation').value = location.name;
            this.app.showToast('Location set to your current position', 'success');
        }
    }

    async getCategories() {
        try {
            // This would typically come from an API endpoint
            return ['Plumbing', 'Electrical', 'Cleaning', 'Tutoring', 'Repair', 'Beauty', 'Fitness', 'Transport'];
        } catch (error) {
            console.error('Error loading categories:', error);
            return [];
        }
    }

    loadCategoriesList() {
        const datalist = document.getElementById('categoryList');
        if (datalist) {
            this.getCategories().then(categories => {
                datalist.innerHTML = categories.map(cat => 
                    `<option value="${cat}">`
                ).join('');
            });
        }
    }

    setupServiceEventListeners() {
        // Search functionality
        const searchInput = document.getElementById('serviceSearch');
        if (searchInput) {
            searchInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.searchServices();
                }
            });
        }

        // Create service form
        const createForm = document.getElementById('createServiceForm');
        if (createForm) {
            createForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                await this.createService();
            });
        }
    }

    async createService() {
        const form = document.getElementById('createServiceForm');
        const formData = {
            title: document.getElementById('serviceTitle').value,
            description: document.getElementById('serviceDescription').value || null,
            base_price: parseFloat(document.getElementById('serviceBasePrice').value),
            hourly_rate: document.getElementById('serviceHourlyRate').value ? 
                        parseFloat(document.getElementById('serviceHourlyRate').value) : null,
            service_radius_km: parseInt(document.getElementById('serviceRadius').value),
            current_location: document.getElementById('serviceLocation').value || null,
            category_name: document.getElementById('serviceCategory').value,
            is_available_now: document.getElementById('serviceAvailableNow').checked
        };

        try {
            await this.app.apiCall('/services/', 'POST', formData);
            this.app.closeModal(document.getElementById('createServiceModal'));
            this.app.showToast('Service created successfully!', 'success');
            await this.loadServices(); // Refresh the list
        } catch (error) {
            this.app.showToast(`Failed to create service: ${error.message}`, 'error');
        }
    }

    async searchServices() {
        const searchTerm = document.getElementById('serviceSearch').value;
        const maxPrice = document.getElementById('maxPrice').value;
        const minTrust = document.getElementById('minTrust').value;
        const maxDistance = document.getElementById('maxDistance').value;

        const params = new URLSearchParams();
        if (searchTerm) params.append('category_name', searchTerm);
        if (maxPrice) params.append('max_price', maxPrice);
        if (minTrust) params.append('min_trust_score', minTrust);
        if (maxDistance) params.append('max_distance_km', maxDistance);

        try {
            const services = await this.app.apiCall(`/services/search/?${params}`);
            this.displaySearchResults(services);
        } catch (error) {
            this.app.showToast('Search failed', 'error');
        }
    }

    displaySearchResults(services) {
        const servicesGrid = document.querySelector('.services-grid');
        if (servicesGrid) {
            if (services.length === 0) {
                servicesGrid.innerHTML = `
                    <div class="empty-state">
                        <i class="fas fa-search"></i>
                        <h3>No services found</h3>
                        <p>Try different search criteria</p>
                    </div>
                `;
            } else {
                servicesGrid.innerHTML = services.map(service => 
                    this.renderServiceCard(service)
                ).join('');
            }
        }
    }

    async showServiceDetail(serviceId) {
        try {
            const service = await this.app.apiCall(`/services/${serviceId}`);
            // Implement service detail view
            this.app.showToast(`Showing details for ${service.title}`, 'info');
        } catch (error) {
            this.app.showToast('Failed to load service details', 'error');
        }
    }

    async editService(serviceId) {
        this.app.showToast('Edit service functionality coming soon', 'info');
    }

    async deleteService(serviceId) {
        if (confirm('Are you sure you want to delete this service?')) {
            try {
                await this.app.apiCall(`/services/${serviceId}`, 'DELETE');
                this.app.showToast('Service deleted successfully', 'success');
                await this.loadServices();
            } catch (error) {
                this.app.showToast('Failed to delete service', 'error');
            }
        }
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.servicesModule = new ServicesModule(this.app); // window.app);
});
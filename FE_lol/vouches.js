// vouches.js - Fixed with safe currentUser access
class VouchesModule {
    constructor(app) {
        this.app = app;
    }

    async loadVouches() {
        const view = document.getElementById('vouchesView');
        
        try {
            // Safe access to currentUser
            const currentUser = this.app.currentUser;
            if (!currentUser) {
                throw new Error('User not authenticated');
            }

            view.innerHTML = `
                <div class="view-header">
                    <h1>Vouches</h1>
                    <p>Build trust in your community through endorsements</p>
                </div>

                <div class="vouches-container">
                    <div class="vouches-stats">
                        <div class="stat-card">
                            <div class="stat-icon">
                                <i class="fas fa-star"></i>
                            </div>
                            <div class="stat-info">
                                <h3>${currentUser.trust_score}</h3>
                                <p>Your Trust Score</p>
                            </div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-icon">
                                <i class="fas fa-handshake"></i>
                            </div>
                            <div class="stat-info">
                                <h3>0</h3>
                                <p>Vouches Given</p>
                            </div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-icon">
                                <i class="fas fa-users"></i>
                            </div>
                            <div class="stat-info">
                                <h3>0</h3>
                                <p>Vouches Received</p>
                            </div>
                        </div>
                    </div>

                    <div class="vouches-content">
                        <div class="section">
                            <h2>Give a Vouch</h2>
                            <div class="vouch-form-card">
                                <p>Vouch for services you've used to help build community trust.</p>
                                <div class="form-group">
                                    <label for="vouchService">Service ID</label>
                                    <input type="text" id="vouchService" placeholder="Enter service ID">
                                </div>
                                <div class="form-group">
                                    <label for="vouchComment">Comment (Optional)</label>
                                    <textarea id="vouchComment" placeholder="Share your experience..."></textarea>
                                </div>
                                <button class="btn btn-primary" onclick="window.vouchesModule.createVouch()">
                                    Submit Vouch
                                </button>
                            </div>
                        </div>

                        <div class="section">
                            <h2>Recent Vouches</h2>
                            <div class="empty-state">
                                <i class="fas fa-star"></i>
                                <h3>No vouches yet</h3>
                                <p>Vouches you give and receive will appear here</p>
                            </div>
                        </div>
                    </div>
                </div>
            `;

        } catch (error) {
            console.error('Error loading vouches:', error);
            view.innerHTML = `
                <div class="error-state">
                    <i class="fas fa-exclamation-triangle"></i>
                    <h3>Failed to load vouches</h3>
                    <p>${error.message || 'Please try again later'}</p>
                    <button onclick="window.vouchesModule.loadVouches()" class="btn btn-primary">Retry</button>
                </div>
            `;
        }
    }

    async createVouch() {
        const serviceId = document.getElementById('vouchService').value;
        const comment = document.getElementById('vouchComment').value;

        if (!serviceId) {
            this.app.showToast('Please enter a service ID', 'warning');
            return;
        }

        try {
            const currentUser = this.app.currentUser;
            if (!currentUser) {
                throw new Error('User not authenticated');
            }

            const vouchData = {
                comment: comment || null,
                voucher_phone: currentUser.phone
            };

            await this.app.apiCall(`/vouches/services/${serviceId}/vouch`, 'POST', vouchData);
            this.app.showToast('Vouch submitted successfully!', 'success');
            
            // Clear form
            document.getElementById('vouchService').value = '';
            document.getElementById('vouchComment').value = '';
            
        } catch (error) {
            this.app.showToast(`Failed to submit vouch: ${error.message}`, 'error');
        }
    }

    async getServiceVouches(serviceId) {
        try {
            return await this.app.apiCall(`/vouches/services/${serviceId}/vouches`);
        } catch (error) {
            console.error('Error fetching service vouches:', error);
            return [];
        }
    }

    async getServiceTrustScore(serviceId) {
        try {
            return await this.app.apiCall(`/vouches/services/${serviceId}/trust-score`);
        } catch (error) {
            console.error('Error fetching trust score:', error);
            return null;
        }
    }
}
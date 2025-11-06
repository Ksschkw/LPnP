// jobs.js - Jobs management module
// jobs.js - Fixed with safe API call access
class JobsModule {
    constructor(app) {
        this.app = app;
    }

    async loadJobs() {
        const view = document.getElementById('jobsView');
        
        try {
            const [myRequests, myOffers] = await Promise.all([
                this.app.apiCall('/jobs/my-requests'),
                this.app.apiCall('/jobs/my-offers')
            ]);

            view.innerHTML = `
                <div class="view-header">
                    <h1>Jobs</h1>
                    <p>Manage your service requests and offers</p>
                </div>

                <div class="jobs-container">
                    <div class="jobs-tabs">
                        <button class="tab-btn active" data-tab="requests">My Requests (${myRequests.length})</button>
                        <button class="tab-btn" data-tab="offers">My Offers (${myOffers.length})</button>
                    </div>

                    <div class="tab-content">
                        <div id="requestsTab" class="tab-pane active">
                            ${this.renderJobsList(myRequests, 'request')}
                        </div>
                        <div id="offersTab" class="tab-pane">
                            ${this.renderJobsList(myOffers, 'offer')}
                        </div>
                    </div>
                </div>
            `;

            this.setupJobTabs();
            this.setupJobEventListeners();

        } catch (error) {
            console.error('Error loading jobs:', error);
            view.innerHTML = `
                <div class="error-state">
                    <i class="fas fa-exclamation-triangle"></i>
                    <h3>Failed to load jobs</h3>
                    <p>${error.message || 'Please try again later'}</p>
                    <button onclick="window.jobsModule.loadJobs()" class="btn btn-primary">Retry</button>
                </div>
            `;
        }
    }

    // ... rest of the jobs.js methods remain the same, but ensure they use this.app instead of window.app ...

    renderJobsList(jobs, type) {
        if (jobs.length === 0) {
            return `
                <div class="empty-state">
                    <i class="fas fa-briefcase"></i>
                    <h3>No ${type === 'request' ? 'requests' : 'offers'} yet</h3>
                    <p>${type === 'request' ? 'Request a service to get started' : 'Your service offers will appear here'}</p>
                </div>
            `;
        }

        return `
            <div class="jobs-list">
                ${jobs.map(job => this.renderJobCard(job, type)).join('')}
            </div>
        `;
    }

    renderJobCard(job, type) {
        const statusClass = this.getStatusClass(job.status);
        
        return `
            <div class="job-card" onclick="window.jobsModule.showJobDetail('${job.id}')">
                <div class="job-header">
                    <h3>${job.job_type}</h3>
                    <span class="status-badge ${statusClass}">${job.status}</span>
                </div>
                
                <div class="job-info">
                    <div class="info-item">
                        <i class="fas fa-dollar-sign"></i>
                        <span>$${job.price_agreed}</span>
                    </div>
                    <div class="info-item">
                        <i class="fas fa-map-marker-alt"></i>
                        <span>${job.work_address}</span>
                    </div>
                    ${job.scheduled_time ? `
                        <div class="info-item">
                            <i class="fas fa-calendar"></i>
                            <span>${Utils.formatDate(job.scheduled_time)}</span>
                        </div>
                    ` : ''}
                </div>

                <div class="job-meta">
                    <span class="date">Created ${Utils.formatDate(job.created_at)}</span>
                    ${type === 'offer' ? this.renderOfferActions(job) : ''}
                </div>
            </div>
        `;
    }

    renderOfferActions(job) {
        if (job.status === 'pending') {
            return `
                <div class="job-actions">
                    <button class="btn btn-success btn-small" 
                            onclick="event.stopPropagation(); window.jobsModule.updateJobStatus('${job.id}', 'accepted')">
                        Accept
                    </button>
                    <button class="btn btn-outline btn-small" 
                            onclick="event.stopPropagation(); window.jobsModule.updateJobStatus('${job.id}', 'rejected')">
                        Reject
                    </button>
                </div>
            `;
        } else if (job.status === 'accepted') {
            return `
                <div class="job-actions">
                    <button class="btn btn-primary btn-small" 
                            onclick="event.stopPropagation(); window.jobsModule.updateJobStatus('${job.id}', 'in_progress')">
                        Start Work
                    </button>
                </div>
            `;
        } else if (job.status === 'in_progress') {
            return `
                <div class="job-actions">
                    <button class="btn btn-success btn-small" 
                            onclick="event.stopPropagation(); window.jobsModule.updateJobStatus('${job.id}', 'completed')">
                        Complete
                    </button>
                </div>
            `;
        }
        return '';
    }

    getStatusClass(status) {
        const statusClasses = {
            'pending': 'status-pending',
            'accepted': 'status-accepted',
            'rejected': 'status-rejected',
            'in_progress': 'status-progress',
            'completed': 'status-completed',
            'cancelled': 'status-cancelled'
        };
        return statusClasses[status] || 'status-pending';
    }

    setupJobTabs() {
        const tabBtns = document.querySelectorAll('.tab-btn');
        const tabPanes = document.querySelectorAll('.tab-pane');

        tabBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                // Remove active class from all buttons and panes
                tabBtns.forEach(b => b.classList.remove('active'));
                tabPanes.forEach(p => p.classList.remove('active'));

                // Add active class to clicked button and corresponding pane
                btn.classList.add('active');
                const tabName = btn.getAttribute('data-tab');
                document.getElementById(`${tabName}Tab`).classList.add('active');
            });
        });
    }

    setupJobEventListeners() {
        // Add any job-specific event listeners here
    }

    async showJobDetail(jobId) {
        try {
            const job = await this.app.apiCall(`/jobs/${jobId}`);
            this.app.showToast(`Showing details for job ${jobId}`, 'info');
            // Implement detailed job view modal
        } catch (error) {
            this.app.showToast('Failed to load job details', 'error');
        }
    }

    async updateJobStatus(jobId, status) {
        try {
            await this.app.apiCall(`/jobs/${jobId}/status?status=${status}`, 'PATCH');
            this.app.showToast(`Job status updated to ${status}`, 'success');
            await this.loadJobs(); // Refresh the list
        } catch (error) {
            this.app.showToast('Failed to update job status', 'error');
        }
    }

    async createJobRequest(serviceId, jobData) {
        try {
            await this.app.apiCall(`/jobs/services/${serviceId}/request`, 'POST', jobData);
            this.app.showToast('Job request created successfully', 'success');
        } catch (error) {
            this.app.showToast('Failed to create job request', 'error');
            throw error;
        }
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.jobsModule = new JobsModule(this.app);
});
from app.repository.Database.job_repo import JobRepository
from app.repository.Database.service_repo import ServiceRepository
from app.models.Requests.job_requests import JobCreateRequest
from app.models.Responses.job_responses import JobBaseResponse, JobDetailResponse
import logging

from app.service.payment_service import PaymentService

logger = logging.getLogger(__name__)

class JobService:
    def __init__(self, db):
        self.job_repo = JobRepository(db)
        self.service_repo = ServiceRepository(db)
    
    def create_job_request(self, service_id: str, job_data: JobCreateRequest, buyer_id: str) -> JobDetailResponse:
        """Create a new job request for a service"""
        # Verify service exists and is active
        service = self.service_repo.get_by_id(service_id)
        if not service:
            raise ValueError("Service not found")
        
        if service.status != "active":
            raise ValueError("This service is not currently available")
        
        # User can't request their own service
        if service.seller_id == buyer_id:
            raise ValueError("You cannot request your own service")
        
        # Create the job
        job = self.job_repo.create(job_data, buyer_id, service_id)
        logger.info(f"Job request created: {job.id} for service {service_id} by user {buyer_id}")
        
        return JobDetailResponse.model_validate(job)
    
    def get_my_job_requests(self, user_id: str) -> list[JobBaseResponse]:
        """Get job requests for current user (as buyer)"""
        jobs = self.job_repo.get_jobs_for_buyer(user_id)
        return [JobBaseResponse.model_validate(job) for job in jobs]
    
    def get_my_job_offers(self, seller_id: str) -> list[JobDetailResponse]:
        """Get job requests for current user's services (as seller)"""
        jobs = self.job_repo.get_jobs_for_seller(seller_id)
        return [JobDetailResponse.model_validate(job) for job in jobs]
    
    # def update_job_status(self, job_id: str, status: str, user_id: str) -> JobDetailResponse:
    def update_job_status(self, job_id: str, status: str, user_id: str) -> JobDetailResponse:
        """Update job status with payment integration - ROBUST VERSION"""
        # Validate status first
        valid_statuses = ['pending', 'accepted', 'in_progress', 'completed', 'cancelled']
        if status not in valid_statuses:
            raise ValueError(f"Invalid status. Must be one of: {valid_statuses}")
        
        job = self.job_repo.get_by_id(job_id)
        if not job:
            raise ValueError("Job not found")
        
        # Check permissions
        if user_id != job.service.seller_id:
            raise ValueError("You can only update jobs for your own services")
        
        try:
            # Handle payment creation when job is accepted
            if status == 'accepted' and job.status == 'pending':
                from app.service.payment_service import PaymentService
                payment_service = PaymentService(self.db)
                payment_service.create_payment_for_job(job_id)
            
            # Handle payment release when job is completed
            if status == 'completed' and job.status in ['accepted', 'in_progress']:
                from app.service.payment_service import PaymentService
                payment_service = PaymentService(self.db)
                #Require buyer confirmation before releasing payment
                if not hasattr(job, 'buyer_confirmed') or not job.buyer_confirmed:
                    # Mark as pending completion, wait for buyer confirmation
                    job = self.job_repo.update_status(job_id, 'pending_completion')
                    # Notify buyer to confirm completion
                    self._notify_buyer_completion(job_id)
                    return JobDetailResponse.model_validate(job)
                
                # OPTION 2: 24-hour automatic release if no dispute -- This is dumb because people can forget
                # completion_time = datetime.utcnow()
                # if completion_time - job.started_at < timedelta(hours=24):
                #     raise ValueError("24-hour waiting period for disputes before payment release")
                
                payment_service.release_payment_to_seller(job_id)
            
            job = self.job_repo.update_status(job_id, status)
            return JobDetailResponse.model_validate(job)
            
        except Exception as e:
            logger.error(f"Error updating job status: {e}")
            raise ValueError(f"Failed to update job status: {str(e)}")
        
    def get_job_details(self, job_id: str, user_id: str) -> JobDetailResponse:
        """Get job details - only participants can view"""
        job = self.job_repo.get_by_id(job_id)
        if not job:
            raise ValueError("Job not found")
        
        # Only buyer or seller can view job details
        if user_id not in [job.buyer_id, job.service.seller_id]:
            raise ValueError("You don't have permission to view this job")
        
        return JobDetailResponse.model_validate(job)
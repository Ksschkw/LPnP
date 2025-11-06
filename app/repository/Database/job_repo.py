from sqlalchemy.orm import Session, joinedload
from app.models.entities.job import Job
from app.models.entities.service import Service
from app.models.entities.user import User
from app.models.Requests.job_requests import JobCreateRequest
import uuid

class JobRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, job_data: JobCreateRequest, buyer_id: str, service_id: str) -> Job:
        """Create a new job request"""
        # Get the service to calculate price
        service = self.db.query(Service).filter(Service.id == service_id).first()
        if not service:
            raise ValueError("Service not found")
        
        job = Job(
            id=str(uuid.uuid4()),
            buyer_id=buyer_id,
            service_id=service_id,
            job_type=job_data.job_type,
            price_agreed=float(service.base_price),  # Use service base price
            buyer_requirements=job_data.buyer_requirements,
            work_address=job_data.work_address,
            work_location=job_data.work_location,
            scheduled_time=job_data.scheduled_time,
            estimated_duration_minutes=job_data.estimated_duration_minutes,
            status="pending"  # New jobs start as pending
        )
        
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        return self.get_by_id(job.id)
    
    def get_by_id(self, job_id: str) -> Job:
        """Get job with all relationships"""
        return (self.db.query(Job)
                .options(
                    joinedload(Job.buyer),
                    joinedload(Job.service).joinedload(Service.seller)
                )
                .filter(Job.id == job_id)
                .first())
    
    def get_jobs_for_seller(self, seller_id: str) -> list[Job]:
        """Get all job requests for a seller's services"""
        return (self.db.query(Job)
                .options(joinedload(Job.buyer), joinedload(Job.service))
                .join(Service)
                .filter(Service.seller_id == seller_id)
                .all())
    
    def get_jobs_for_buyer(self, buyer_id: str) -> list[Job]:
        """Get all jobs a buyer has requested"""
        return (self.db.query(Job)
                .options(joinedload(Job.service))
                .filter(Job.buyer_id == buyer_id)
                .all())
    
    def update_status(self, job_id: str, status: str) -> Job:
        """Update job status"""
        valid_statuses = ['pending', 'accepted', 'in_progress', 'completed', 'cancelled']
        if status not in valid_statuses:
            raise ValueError(f"Status must be one of: {valid_statuses}")
        
        job = self.get_by_id(job_id)
        if job:
            job.status = status
            self.db.commit()
            self.db.refresh(job)
        return job
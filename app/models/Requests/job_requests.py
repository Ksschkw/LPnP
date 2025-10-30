from pydantic import BaseModel, field_validator
from typing import Optional
from decimal import Decimal
from datetime import datetime

class JobCreateRequest(BaseModel):
    """Request model for creating a new job booking"""
    
    service_id: str  # ID of the service being booked
    job_type: str  # Type of job: "instant", "scheduled", or "recurring"
    buyer_requirements: Optional[str] = None  # Specific requirements from buyer
    work_address: str  # Where the work will be performed
    work_location: str  # General location/landmark
    scheduled_time: Optional[datetime] = None  # When the job should happen (for scheduled jobs)
    estimated_duration_minutes: Optional[int] = None  # How long the job will take
    
    @field_validator('job_type')
    @classmethod
    def validate_job_type(cls, v: str) -> str:
        """Ensure job type is valid"""
        valid_types = ['instant', 'scheduled', 'recurring']
        if v not in valid_types:
            raise ValueError(f'Job type must be one of: {", ".join(valid_types)}')
        return v

class JobUpdateRequest(BaseModel):
    """Request model for updating job status and details"""
    
    status: Optional[str] = None  # New status: accepted, in_progress, completed, cancelled
    buyer_requirements: Optional[str] = None  # Updated requirements
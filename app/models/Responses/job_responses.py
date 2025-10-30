from pydantic import BaseModel
from pydantic import ConfigDict
from typing import Optional
from datetime import datetime
from decimal import Decimal
from app.models.Responses.user_responses import UserBaseResponse
from app.models.Responses.service_responses import ServiceBaseResponse

class JobBaseResponse(BaseModel):
    """Basic job information"""
    
    id: str  # Unique job ID
    job_type: str  # Type of job: instant, scheduled, recurring
    status: str  # Current status: pending, accepted, in_progress, completed, cancelled
    price_agreed: Decimal  # Final agreed price
    buyer_requirements: Optional[str] = None  # Buyer's specific requirements
    work_address: str  # Where the work will be performed
    work_location: str  # General location/landmark
    scheduled_time: Optional[datetime] = None  # When job is scheduled (UTC)
    created_at: datetime  # When job was created (UTC)
    
    # class Config:
    #     from_attributes = True
    model_config = ConfigDict(from_attributes=True)

class JobDetailResponse(JobBaseResponse):
    """Detailed job information including relationships"""
    
    buyer: UserBaseResponse  # User who booked the job
    service: ServiceBaseResponse  # Service being provided
    started_at: Optional[datetime] = None  # When work actually started (UTC)
    completed_at: Optional[datetime] = None  # When work was completed (UTC)
    estimated_duration_minutes: Optional[int] = None  # Estimated job duration
    updated_at: datetime  # When job was last updated (UTC)

    model_config = ConfigDict(from_attributes=True)

from pydantic import BaseModel, field_validator
from typing import Optional

class ReviewCreateRequest(BaseModel):
    """Request model for creating a review after job completion"""
    
    job_id: str  # ID of the job being reviewed
    rating: int  # Star rating from 1 to 5
    comment: Optional[str] = None  # Written feedback
    
    @field_validator('rating')
    @classmethod
    def validate_rating(cls, v: int) -> int:
        """Ensure rating is between 1 and 5 stars"""
        if v < 1 or v > 5:
            raise ValueError('Rating must be between 1 and 5 stars')
        return v
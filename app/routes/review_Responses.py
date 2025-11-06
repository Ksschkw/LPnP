from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from app.models.Responses.user_responses import UserBaseResponse

class ReviewResponse(BaseModel):
    id: str
    job_id: str
    reviewer: UserBaseResponse
    review_type: str
    rating: int
    comment: Optional[str] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
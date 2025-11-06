from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from app.models.Responses.user_responses import UserBaseResponse

class VouchResponse(BaseModel):
    id: str
    service_id: str
    voucher_user: Optional[UserBaseResponse] = None
    voucher_phone: str
    vouch_type: str
    points_given: int
    comment: Optional[str] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class ServiceTrustScoreResponse(BaseModel):
    total_points: int
    trusted_vouches: int
    quick_vouches: int
    total_vouches: int
    status: str
    needed_for_activation: int
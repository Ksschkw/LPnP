from pydantic import BaseModel
from pydantic import ConfigDict
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from app.models.Responses.user_responses import UserBaseResponse

class ServiceCategoryResponse(BaseModel):
    """Service category information"""
    
    id: str  # Unique category ID
    name: str  # Category name (e.g., "Plumbing", "Electrical")
    description: Optional[str] = None  # Category description
    icon_url: Optional[str] = None  # URL to category icon
    
    
    # class Config:
    #     from_attributes = True
    model_config = ConfigDict(from_attributes=True)

class ServiceBaseResponse(BaseModel):
    """Basic service information"""
    
    id: str  # Unique service ID
    title: str  # Service title
    description: Optional[str] = None  # Service description
    base_price: Decimal  # Base price for the service
    hourly_rate: Optional[Decimal] = None  # Hourly rate (if applicable)
    service_radius_km: int  # How far the provider will travel
    current_location: Optional[str] = None  # Provider's current location
    is_available_now: bool  # Whether provider is currently available
    status: str  # Service status: draft, vouching, active, inactive
    trust_points: int  # Trust points from vouches
    completion_count: int  # Number of completed jobs
    created_at: datetime  # When service was created (UTC)
    
    # class Config:
    #     from_attributes = True
    model_config = ConfigDict(from_attributes=True)

    # Ensure seller includes badge info
    seller: UserBaseResponse  # This now includes badge_level and badge_icon

class ServiceDetailResponse(ServiceBaseResponse):
    """Detailed service information including relationships"""
    
    seller: UserBaseResponse  # User who owns this service
    categories: List[ServiceCategoryResponse]  # Categories this service belongs to
    total_earnings: Decimal  # Total earnings from this service
    updated_at: datetime  # When service was last updated (UTC)

    model_config = ConfigDict(from_attributes=True)
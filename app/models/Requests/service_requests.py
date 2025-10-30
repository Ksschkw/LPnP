from pydantic import BaseModel, field_validator
from typing import Optional, List
from decimal import Decimal

class ServiceCreateRequest(BaseModel):
    """Request model for creating a new service offering"""
    
    title: str  # Service title like "Professional Plumbing Services"
    description: Optional[str] = None  # Detailed service description
    base_price: Decimal  # Base price for the service
    hourly_rate: Optional[Decimal] = None  # Optional hourly rate
    service_radius_km: int = 10  # How far the service provider will travel
    current_location: Optional[str] = None  # Current location of service provider
    category_ids: List[str]  # List of category IDs this service belongs to
    
    @field_validator('base_price')
    @classmethod
    def validate_price(cls, v: Decimal) -> Decimal:
        """Ensure service price is positive"""
        if v <= 0:
            raise ValueError('Service price must be positive')
        return v
    
    @field_validator('service_radius_km')
    @classmethod
    def validate_radius(cls, v: int) -> int:
        """Ensure service radius is reasonable"""
        if v < 1 or v > 100:
            raise ValueError('Service radius must be between 1 and 100 km')
        return v

class ServiceUpdateRequest(BaseModel):
    """Request model for updating an existing service (all fields optional)"""
    
    title: Optional[str] = None
    description: Optional[str] = None
    base_price: Optional[Decimal] = None
    hourly_rate: Optional[Decimal] = None
    service_radius_km: Optional[int] = None
    current_location: Optional[str] = None
    is_available_now: Optional[bool] = None

class ServiceSearchRequest(BaseModel):
    """Request model for searching services"""
    
    category_id: Optional[str] = None  # Filter by specific category
    location: str  # User's current location for proximity search
    max_distance_km: int = 10  # Maximum distance from location
    min_trust_score: int = 0  # Minimum trust score of service provider
    max_price: Optional[Decimal] = None  # Maximum price filter
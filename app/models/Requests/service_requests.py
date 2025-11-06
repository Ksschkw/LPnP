from pydantic import BaseModel, field_validator, Field
from typing import Optional, List
from decimal import Decimal

class ServiceCreateRequest(BaseModel):
    """Request model for creating a new service offering"""
    
    title: str
    description: Optional[str] = None
    base_price: Decimal
    hourly_rate: Optional[Decimal] = None
    service_radius_km: int = 10
    current_location: Optional[str] = None
    # category_ids: List[str]  # List of category IDs this service belongs to
    category_name: str
    
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
    """Smart search request with user-friendly parameters"""
    
    category_name: Optional[str] = None
    location: Optional[str] = None
    max_distance_km: int = Field(default=10, ge=1, le=100)
    min_trust_score: int = Field(default=0, ge=0)
    max_price: Optional[float] = Field(default=None, ge=0)
    
    @field_validator('category_name')
    @classmethod
    def validate_category_name(cls, v: Optional[str]) -> Optional[str]:
        """Clean and validate category name"""
        if v is None:
            return v
        
        cleaned = v.strip()
        if len(cleaned) < 2:
            raise ValueError('Category name must be at least 2 characters')
        
        return cleaned
    
    @field_validator('location')
    @classmethod
    def validate_location(cls, v: Optional[str]) -> Optional[str]:
        """Clean and validate location"""
        if v is None:
            return v
        
        cleaned = v.strip()
        if len(cleaned) < 2:
            raise ValueError('Location must be at least 2 characters')
        
        return cleaned
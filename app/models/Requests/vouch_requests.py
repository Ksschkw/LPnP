from pydantic import BaseModel, field_validator, model_validator
from typing import Optional

class VouchCreateRequest(BaseModel):
    """Request model for creating a vouch/endorsement for a service"""
    
    comment: Optional[str] = None  # Optional comment about why they're vouching
    
    # Only required for non-logged-in users
    voucher_phone: Optional[str] = None  # Phone number of person giving the vouch (only for quick vouches)
    
    @model_validator(mode='after')
    def validate_phone_for_quick_vouch(self) -> 'VouchCreateRequest':
        """Validate that phone is provided for non-logged-in users"""
        # This validation will be handled in the service layer based on auth status
        return self
    
    @field_validator('voucher_phone')
    @classmethod
    def validate_phone_format(cls, v: Optional[str]) -> Optional[str]:
        """Validate phone format if provided"""
        if v is None:
            return v
        
        # Basic phone validation - adjust based on your requirements
        if len(v.strip()) < 5:
            raise ValueError('Phone number must be at least 5 characters')
        
        return v.strip()
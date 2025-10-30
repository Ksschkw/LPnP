from pydantic import BaseModel, field_validator
from typing import Optional

class VouchCreateRequest(BaseModel):
    """Request model for creating a vouch/endorsement for a service"""
    
    service_id: str  # ID of the service being vouched for
    voucher_phone: str  # Phone number of person giving the vouch
    vouch_type: str  # Type of vouch: "trusted" (50 points) or "quick" (10 points)
    comment: Optional[str] = None  # Optional comment about why they're vouching
    
    @field_validator('vouch_type')
    @classmethod
    def validate_vouch_type(cls, v: str) -> str:
        """Ensure vouch type is valid"""
        valid_types = ['trusted', 'quick']
        if v not in valid_types:
            raise ValueError(f'Vouch type must be one of: {", ".join(valid_types)}')
        return v
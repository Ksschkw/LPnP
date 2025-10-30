from pydantic import BaseModel, field_validator
from typing import Optional

class DisputeCreateRequest(BaseModel):
    """Request model for raising a dispute about a job"""
    
    job_id: str  # ID of the disputed job
    reason: str  # Reason for dispute (e.g., "poor_quality", "no_show", "over_charging")
    initial_complaint: str  # Detailed description of the problem
    
    @field_validator('reason')
    @classmethod
    def validate_reason(cls, v: str) -> str:
        """Ensure dispute reason is valid"""
        valid_reasons = ['poor_quality', 'no_show', 'over_charging', 'late_completion', 'safety_concerns']
        if v not in valid_reasons:
            raise ValueError(f'Dispute reason must be one of: {", ".join(valid_reasons)}')
        return v

class DisputeUpdateRequest(BaseModel):
    """Request model for updating dispute resolution progress"""
    
    status: Optional[str] = None  # Updated status: open, in_progress, resolved
    respondent_response: Optional[str] = None  # Response from the other party
    admin_notes: Optional[str] = None  # Internal notes from admin
    final_decision: Optional[str] = None  # Final resolution decision
    refund_amount: Optional[float] = None  # Amount to refund if applicable
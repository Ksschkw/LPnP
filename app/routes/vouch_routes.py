from fastapi import APIRouter, Depends, HTTPException
from app.dependencies import get_vouch_service
from app.utilities.auth import get_current_user
from app.models.entities.user import User
from app.models.Requests.vouch_requests import VouchCreateRequest
from app.models.Responses.vouch_responses import VouchResponse
from typing import List, Optional

router = APIRouter(prefix="/vouches", tags=["vouches"])

@router.post("/services/{service_id}/vouch", response_model=VouchResponse)
async def create_vouch(
    service_id: str,
    vouch_data: VouchCreateRequest,
    current_user: Optional[User] = Depends(get_current_user),  # Optional - can be None if not logged in
    vouch_service=Depends(get_vouch_service)
):
    """
    Vouch for a service
    
    For LOGGED-IN users (Bearer token):
    - 50 points automatically
    - No phone needed (uses account phone)
    - Only comment is optional
    
    For NON-LOGGED-IN users (no token):
    - 10 points automatically  
    - Phone number REQUIRED
    - Comment is optional
    """
    try:
        user_id = current_user.id if current_user else None
        user_phone = current_user.phone if current_user else None
        
        return vouch_service.create_vouch(service_id, vouch_data, user_id, user_phone)
    except ValueError as e:
        raise HTTPException(400, detail=str(e))

@router.get("/services/{service_id}/vouches", response_model=List[VouchResponse])
async def get_service_vouches(
    service_id: str,
    vouch_service=Depends(get_vouch_service)
):
    """Get all vouches for a service"""
    return vouch_service.get_service_vouches(service_id)

@router.get("/services/{service_id}/trust-score")
async def get_service_trust_score(
    service_id: str,
    vouch_service=Depends(get_vouch_service)
):
    """Get detailed trust score breakdown for a service"""
    try:
        return vouch_service.get_service_trust_score(service_id)
    except ValueError as e:
        raise HTTPException(400, detail=str(e))
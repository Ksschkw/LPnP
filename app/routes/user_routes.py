from fastapi import APIRouter, Depends, HTTPException, status
# from sqlalchemy.orm import Session
from typing import List
import logging
logging.basicConfig(level=logging.INFO)
logging.BASIC_FORMATTER = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logger = logging.getLogger(__name__)


# from app.database import get_db
from app.auth import get_current_user
from app.models.entities.user import User
from app.service.user_service import UserService
from app.models.Requests.user_requests import UserCreateRequest, UserLoginRequest, UserUpdateRequest
# from app.models.Responses.user_responses import UserBaseResponse
from app.models.Responses.user_responses import UserBaseResponse, UserDetailResponse
from app.dependencies import get_user_service

from app.models.Responses.user_responses import UserWithTokenResponse
# Create router for all user-related endpoints
router = APIRouter(prefix="/users", tags=["users"])

# ====== /me ENDPOINTS MUST COME FIRST ======
@router.get("/me", response_model=UserBaseResponse)
async def get_my_profile(
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    """Get the current user's profile"""
    logger.info(f"Profile request: {current_user.id}")
    user = user_service.get_user(current_user.id)  # Use the actual user ID, not "me"
    if not user:
        raise HTTPException(404, "User not found")
    return user

@router.put("/me", response_model=UserBaseResponse)
async def update_my_profile(
    update_data: UserUpdateRequest,
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    """Update the current user's profile"""
    logger.info(f"Profile update request: {current_user.id}")
    
    update_dict = update_data.model_dump(exclude_unset=True)
    user = user_service.update_user_profile(current_user.id, update_dict)  # Use actual user ID
    if not user:
        raise HTTPException(404, "User not found")
    return user

@router.post("/", response_model=UserBaseResponse, status_code=status.HTTP_201_CREATED)
def create_user(user_data: UserCreateRequest, user_service: UserService = Depends(get_user_service)):
    """Create a new user account"""
    # user_service = UserService(db)
    try:
        return user_service.create_user(user_data)
    except ValueError as e:
        # Handle validation errors (duplicate phone, etc.)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/login", response_model=UserWithTokenResponse)
async def login_user(login_data: UserLoginRequest, user_service: UserService = Depends(get_user_service)):
    result = user_service.authenticate_user(login_data)
    if not result:
        logger.warning(f"Login failed in route: {login_data.phone}")
        raise HTTPException(status_code=401, detail="Invalid phone or password")
    return result


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: str, user_service: UserService = Depends(get_user_service)):
    """Permanently delete a user account"""
    # user_service = UserService(db)
    success = user_service.delete_user_account(user_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    

@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_my_account(
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    """Delete the current user's account"""
    logger.info(f"Account deletion request: {current_user.id}")
    
    success = user_service.delete_user_account(current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete account"
        )
# ====== GENERAL USER ENDPOINTS ======
@router.get("/{user_id}", response_model=UserBaseResponse)
def get_user(user_id: str, user_service: UserService = Depends(get_user_service)):
    """Get detailed information about a specific user"""
    user = user_service.get_user(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user
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

@router.get("/{user_id}", response_model=UserBaseResponse)
def get_user(user_id: str, user_service: UserService = Depends(get_user_service)):
    """Get detailed information about a specific user"""
    # user_service = UserService(db)
    user = user_service.get_user(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
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

# @router.post("/login", response_model=UserBaseResponse)
# def login_user(login_data: UserLoginRequest, user_service: UserService = Depends(get_user_service)):
#     """Log in a user with phone and password"""
#     # user_service = UserService(db)
#     user = user_service.authenticate_user(login_data)
    
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid phone number or password"
#         )
#     return user

# REPLACE login route
@router.post("/login", response_model=UserWithTokenResponse)
async def login_user(login_data: UserLoginRequest, user_service: UserService = Depends(get_user_service)):
    result = user_service.authenticate_user(login_data)
    if not result:
        logger.warning(f"Login failed in route: {login_data.phone}")
        raise HTTPException(status_code=401, detail="Invalid phone or password")
    return result

@router.put("/{user_id}", response_model=UserBaseResponse)
def update_user(user_id: str, update_data: UserUpdateRequest, user_service: UserService = Depends(get_user_service)):
    """Update user profile information"""
    # user_service = UserService(db)
    
    # Convert to dictionary, only including fields that were actually provided
    # Pydantic v2: Use model_dump(), not dict()
    update_dict = update_data.model_dump(exclude_unset=True)#dict(exclude_unset=True)
    
    
    user = user_service.update_user_profile(user_id, update_dict)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

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
    

# @router.get("/me", response_model=UserDetailResponse)  # Changed to DetailResponse
# async def get_my_profile(
#     current_user: User = Depends(get_current_user),
#     user_service: UserService = Depends(get_user_service)
# ):
#     """Get the current user's full profile"""
#     logger.info(f"Profile request: {current_user.id}")
    
#     # Try to get user directly from repository first
#     from app.repository.Database.user_repo import UserRepository
#     from app.database import get_db
    
#     # Direct database access for debugging
#     user_repo = UserRepository(next(get_db()))
#     user = user_repo.get_by_id(current_user.id)
    
#     if not user:
#         logger.error(f"User not found in database: {current_user.id}")
#         raise HTTPException(404, "User not found")
    
#     logger.info(f"User found: {user.id} - {user.name}")
    
#     # Try both response models
#     try:
#         detail_response = UserDetailResponse.model_validate(user)
#         logger.info("Success with UserDetailResponse")
#         return detail_response
#     except Exception as e:
#         logger.error(f"UserDetailResponse failed: {e}")
#         try:
#             base_response = UserBaseResponse.model_validate(user)
#             logger.info("Success with UserBaseResponse")
#             return base_response
#         except Exception as e2:
#             logger.error(f"UserBaseResponse also failed: {e2}")
#             raise HTTPException(500, "Error processing user data")

# @router.put("/me", response_model=UserBaseResponse)
# async def update_my_profile(
#     update_data: UserUpdateRequest,
#     current_user: User = Depends(get_current_user),
#     user_service: UserService = Depends(get_user_service)
# ):
#     """Update the current user's profile"""
#     logger.info(f"Profile update request: {current_user.id}")
    
#     # Convert to dictionary, only including fields that were actually provided
#     update_dict = update_data.model_dump(exclude_unset=True)
    
#     user = user_service.update_user_profile(current_user.id, update_dict)
#     if not user:
#         raise HTTPException(404, "User not found")
#     return user
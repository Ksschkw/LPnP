from fastapi import APIRouter, Depends, HTTPException, status
# from sqlalchemy.orm import Session
from typing import List

# from app.database import get_db
from app.service.user_service import UserService
from app.models.Requests.user_requests import UserCreateRequest, UserLoginRequest, UserUpdateRequest
# from app.models.Responses.user_responses import UserBaseResponse
from app.models.Responses.user_responses import UserBaseResponse
from app.dependencies import get_user_service

# Create router for all user-related endpoints
router = APIRouter(prefix="/users", tags=["users"])

@router.get("/", response_model=List[UserBaseResponse])
def get_all_users(skip: int = 0, limit: int = 100, user_service: UserService = Depends(get_user_service)):
    """Get a list of all users (for admin purposes)"""
    # user_service = UserService(db)
    users = user_service.get_all_users(skip, limit)
    return users

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

@router.post("/login", response_model=UserBaseResponse)
def login_user(login_data: UserLoginRequest, user_service: UserService = Depends(get_user_service)):
    """Log in a user with phone and password"""
    # user_service = UserService(db)
    user = user_service.authenticate_user(login_data)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid phone number or password"
        )
    return user

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
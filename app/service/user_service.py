from app.repository.Database.user_repo import UserRepository
from app.models.Requests.user_requests import UserCreateRequest, UserLoginRequest
# from app.models.Responses.user_responses import UserBaseResponse
from app.models.Responses.user_responses import UserBaseResponse, UserDetailResponse
import logging

from app.utilities.auth import create_access_token
from app.models.Responses.user_responses import UserWithTokenResponse
from app.service.badge_service import BadgeService

logger = logging.getLogger(__name__)

class UserService:
    """Contains the business rules and logic for user operations"""
    
    def __init__(self, db):
        self.user_repo = UserRepository(db)
        self.badge_service = BadgeService(db)  # Add this
    
    def get_user(self, user_id: str) -> UserBaseResponse:
        """Get user details by ID"""
        user = self.user_repo.get_by_id(user_id)
        if not user:
            logger.warning(f"User not found in repository: {user_id}")
            return None
        
        try:
            # Add detailed logging
            logger.info(f"Found user: {user.id}, name: {user.name}, email: {user.email}")
            response = UserBaseResponse.model_validate(user)
            logger.info(f"Successfully validated user response for: {user_id}")
            return response
        except Exception as e:
            logger.error(f"Error validating user response for {user_id}: {e}")
            return None
    
    def get_user_by_phone(self, phone: str) -> UserBaseResponse:
        """Get user details by phone number"""
        user = self.user_repo.get_by_phone(phone)
        if not user:
            return None
        return UserBaseResponse.model_validate(user)
    
    def create_user(self, user_data: UserCreateRequest) -> UserBaseResponse:
        """Create a new user account with validation"""
        # Check if phone number is already registered
        existing_user = self.user_repo.get_by_phone(user_data.phone)
        if existing_user:
            raise ValueError("This phone number is already registered")
        
        # Check if email is already used (if provided)
        if user_data.email:
            existing_email = self.user_repo.get_by_email(user_data.email)
            if existing_email:
                raise ValueError("This email is already registered")
        
        # Create the new user
        user = self.user_repo.create(user_data)
        logger.info(f"New user created: {user.email}")
        return UserBaseResponse.model_validate(user)
    
    # def authenticate_user(self, login_data: UserLoginRequest) -> UserBaseResponse:
    #     """Verify user credentials and log them in"""
    #     # Find user by phone
    #     user = self.user_repo.get_by_phone(login_data.phone)
    #     if not user:
    #         return None
        
    #     # Check if password is correct
    #     if not self.user_repo.verify_password(login_data.password, user.password_hash):
    #         return None
        
    #     # Mark user as online
    #     self.user_repo.update(user.id, {"is_online": True})
        
    #     logger.info(f"User logged in: {user.phone}")
    #     return UserBaseResponse.model_validate(user)
    def authenticate_user(self, login_data: UserLoginRequest) -> UserWithTokenResponse:
        """Verify credentials and return JWT"""
        logger.info(f"Login attempt for phone: {login_data.phone}")
        
        user = self.user_repo.get_by_phone(login_data.phone)
        if not user:
            logger.warning(f"Login failed: phone not found - {login_data.phone}")
            return None
        
        if not self.user_repo.verify_password(login_data.password, user.password_hash):
            logger.warning(f"Login failed: wrong password - {login_data.phone}")
            return None
        
        # Create JWT
        access_token = create_access_token({"sub": user.id})
        
        logger.info(f"Login successful: {user.phone} - JWT issued")
        
        return UserWithTokenResponse(
            **UserBaseResponse.model_validate(user).model_dump(),
            access_token=access_token,
            token_type="bearer"
        )
    
    def update_user_profile(self, user_id: str, update_data: dict) -> UserBaseResponse:
        """Update user profile information"""
        user = self.user_repo.update(user_id, update_data)
        if not user:
            return None
        return UserBaseResponse.model_validate(user)
    
    def delete_user_account(self, user_id: str) -> bool:
        """Remove user account from the system"""
        return self.user_repo.delete(user_id)
    
    def purchase_elite_badge(self, user_id: str) -> bool:
        return self.badge_service.purchase_elite_badge(user_id)

    def update_trust_points(self, user_id: str, points: int) -> UserBaseResponse:
        user = self.user_repo.update_trust_score(user_id, points)
        if user:
            # Recalculate badge after trust score change
            self.badge_service.update_user_badge(user_id)
        return UserBaseResponse.model_validate(user)
    
    # def update_trust_points(self, user_id: str, points: int) -> UserBaseResponse:
    #     """Increase or decrease user's trust score"""
    #     if points < 0:
    #         raise ValueError("Trust score cannot be negative")
        
    #     user = self.user_repo.update_trust_score(user_id, points)
    #     if not user:
    #         return None
    #     return UserBaseResponse.model_validate(user)
    
    def get_user_detail(self, user_id: str) -> UserDetailResponse:
        """Get user details by ID with all fields"""
        user = self.user_repo.get_by_id(user_id)
        if not user:
            return None
        return UserDetailResponse.model_validate(user)
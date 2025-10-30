from app.repository.Database.user_repo import UserRepository
from app.models.Requests.user_requests import UserCreateRequest, UserLoginRequest
# from app.models.Responses.user_responses import UserBaseResponse
from app.models.Responses.user_responses import UserBaseResponse
import logging

logger = logging.getLogger(__name__)

class UserService:
    """Contains the business rules and logic for user operations"""
    
    def __init__(self, db):
        self.user_repo = UserRepository(db)
    
    def get_user(self, user_id: str) -> UserBaseResponse:
        """Get user details by ID"""
        user = self.user_repo.get_by_id(user_id)
        if not user:
            return None
        return UserBaseResponse.model_validate(user)
    
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
    
    def authenticate_user(self, login_data: UserLoginRequest) -> UserBaseResponse:
        """Verify user credentials and log them in"""
        # Find user by phone
        user = self.user_repo.get_by_phone(login_data.phone)
        if not user:
            return None
        
        # Check if password is correct
        if not self.user_repo.verify_password(login_data.password, user.password_hash):
            return None
        
        # Mark user as online
        self.user_repo.update(user.id, {"is_online": True})
        
        logger.info(f"User logged in: {user.phone}")
        return UserBaseResponse.model_validate(user)
    
    def update_user_profile(self, user_id: str, update_data: dict) -> UserBaseResponse:
        """Update user profile information"""
        user = self.user_repo.update(user_id, update_data)
        if not user:
            return None
        return UserBaseResponse.model_validate(user)
    
    def delete_user_account(self, user_id: str) -> bool:
        """Remove user account from the system"""
        return self.user_repo.delete(user_id)
    
    def update_trust_points(self, user_id: str, points: int) -> UserBaseResponse:
        """Increase or decrease user's trust score"""
        if points < 0:
            raise ValueError("Trust score cannot be negative")
        
        user = self.user_repo.update_trust_score(user_id, points)
        if not user:
            return None
        return UserBaseResponse.model_validate(user)
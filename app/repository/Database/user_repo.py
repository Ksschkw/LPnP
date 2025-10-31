from sqlalchemy.orm import Session
from app.models.entities.user import User
from app.models.Requests.user_requests import UserCreateRequest
import bcrypt
import uuid
import logging
logger = logging.getLogger(__name__)


class UserRepository:
    """Handles all database operations for users"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, user_id: str) -> User:
        """Find user by their unique ID"""
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_by_id(self, user_id: str) -> User:
        """Find user by their unique ID"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            logger.warning(f"User not found in database: {user_id}")
        else:
            logger.info(f"User found in database: {user.id} - {user.name}")
        return user
    
    def get_by_phone(self, phone: str) -> User:
        """Find user by phone number (each phone can only have one account)"""
        return self.db.query(User).filter(User.phone == phone).first()
    
    def get_by_email(self, email: str) -> User:
        """Find user by email address"""
        return self.db.query(User).filter(User.email == email).first()
    
    def get_all(self, skip: int = 0, limit: int = 100) -> list[User]:
        """Get multiple users (for admin purposes)"""
        return self.db.query(User).offset(skip).limit(limit).all()
    
    def create(self, user_data: UserCreateRequest) -> User:
        """Create a new user account with secure password hashing"""
        # Hash the password using bcrypt (secure)
        password_hash = bcrypt.hashpw(user_data.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        user = User(
            id=str(uuid.uuid4()),
            name=user_data.name,
            email=user_data.email,
            phone=user_data.phone,
            password_hash=password_hash  # Store the secure hash
        )
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def update(self, user_id: str, update_data: dict) -> User:
        """Update user information - only changes provided fields"""
        user = self.get_by_id(user_id)
        if user:
            for field, new_value in update_data.items():
                if hasattr(user, field) and new_value is not None:
                    setattr(user, field, new_value)
            self.db.commit()
            self.db.refresh(user)
        return user
    
    def delete(self, user_id: str) -> bool:
        """Permanently delete a user account"""
        user = self.get_by_id(user_id)
        if user:
            self.db.delete(user)
            self.db.commit()
            return True
        return False
    
    #Out - utility
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Check if provided password matches the stored hash"""
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    
    def update_trust_score(self, user_id: str, new_score: int) -> User:
        """Update how much the community trusts this user"""
        return self.update(user_id, {"trust_score": new_score})
    
    def mark_online(self, user_id: str) -> User:
        """Mark user as online and update last active timestamp"""
        from sqlalchemy import func
        user = self.get_by_id(user_id)
        if user:
            user.is_online = True
            user.last_active = func.now()
            self.db.commit()
            self.db.refresh(user)
        return user
    
    def mark_offline(self, user_id: str) -> User:
        """Mark user as offline"""
        return self.update(user_id, {"is_online": False})
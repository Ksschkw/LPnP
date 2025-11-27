from pydantic import BaseModel, EmailStr, ConfigDict, computed_field

from typing import Optional
from datetime import datetime

class UserBaseResponse(BaseModel):
    """Basic user information returned in most API responses"""
    
    id: str  # Unique user ID
    name: str  # User's full name
    email: Optional[EmailStr] = None  # User's email (if provided)
    phone: str  # User's phone number (primary identifier)
    avatar_url: Optional[str] = None  # URL to user's profile picture
    trust_score: int  # Overall trust score (0-100+)
    verification_level: int  # 0=basic, 1=NIN, 2=bank, 3=address verified
    is_online: bool  # Whether user is currently online
    last_active: datetime  # When user was last active (in UTC)

    #FOR BADGE SYSTEM
    badge_level: str  # newbie, trusted, verified, elite, legend
    # badge_icon: str   # emoji representation
    has_paid_badge: bool = False
    
    @computed_field
    @property
    def badge_icon(self) -> str:
        badges = {
            "newbie": "🌱",
            "trusted": "⭐", 
            "verified": "✅",
            "elite": "🏆",
            "legend": "🔥"
        }
        return badges.get(self.badge_level, "🌱")
    
    # class Config:
    #     from_attributes = True  # Allows creating from SQLAlchemy models
    model_config = ConfigDict(from_attributes=True)

class UserDetailResponse(UserBaseResponse):
    """Detailed user information including private data"""
    
    nin_verified: bool  # Whether NIN verification is complete
    completion_count: int  # Number of completed jobs
    total_earnings: Optional[float] = None  # Total earnings (for service providers)
    created_at: datetime  # When user account was created (UTC)
    updated_at: datetime  # When user profile was last updated (UTC)
    password_hash: Optional[str] = None
    nin_encrypted: Optional[str] = None

class UserWithTokenResponse(UserBaseResponse):
    """User response that includes authentication token"""
    
    access_token: str  # JWT token for authenticated requests
    token_type: str = "bearer"  # Token type for Authorization header

    model_config = ConfigDict(from_attributes=True)

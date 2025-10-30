from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional

class UserCreateRequest(BaseModel):
    """Request model for creating a new user"""
    
    name: str
    # Email is optional during initial registration
    email: Optional[EmailStr] = None  
    phone: str
    password: str
    
    @field_validator('password')
    @classmethod
    def password_strength(cls, v: str) -> str:
        """Validate that password meets minimum security requirements"""
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters long')
        return v

class UserLoginRequest(BaseModel):
    """Request model for user login"""
    
    phone: str
    password: str

class UserUpdateRequest(BaseModel):
    """Request model for updating user profile (all fields optional)"""
    
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    avatar_url: Optional[str] = None

class NINVerificationRequest(BaseModel):
    """Request model for NIN verification"""
    
    nin_encrypted: str  # Encrypted National Identification Number
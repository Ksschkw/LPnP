from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, Numeric
from sqlalchemy.sql import func
import uuid
from app.config.database import Base

class User(Base):
    __tablename__ = "users"
    
    # PRIMARY KEY = Unique ID for each user
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Basic Info (REQUIRED fields)
    name = Column(String(100), nullable=False)                    # Must have a name
    phone = Column(String(20), unique=True, nullable=False)      # Must have unique phone
    password_hash = Column(String(255), nullable=False)          # Must have password
    
    # Basic Info (OPTIONAL fields)  
    email = Column(String(255), nullable=True)                   # Can be empty
    avatar_url = Column(String(500), nullable=True)              # Can be empty
    
    # Verification & Trust
    nin_encrypted = Column(String(255), nullable=True)           # NIN number (encrypted)
    nin_verified = Column(Boolean, default=False)                # True/False
    trust_score = Column(Integer, default=0)                     # Number starting at 0
    verification_level = Column(Integer, default=0)              # 0=basic, 1=NIN, 2=bank verified
    
    # Status
    last_active = Column(DateTime, server_default=func.now())    # Auto-set to now
    is_online = Column(Boolean, default=False)                   # True if user is online
    completion_count = Column(Integer, default=0)  # Number of completed jobs

    
    # Timestamps (Auto-managed)
    created_at = Column(DateTime, server_default=func.now())     # Auto-set on creation
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())  # Auto-update when changed

    # NEW FIELDS FOR BADGE SYSTEM
    badge_level = Column(String(20), default="newbie")  # newbie, trusted, verified, elite, legend
    has_paid_badge = Column(Boolean, default=False)     # Whether they paid for Elite badge
    badge_purchased_at = Column(DateTime, nullable=True) # When they bought Elite badge

    # NEW: Earnings tracking
    total_earnings = Column(Numeric(12, 2), default=0)              # Total money earned
    available_balance = Column(Numeric(12, 2), default=0)           # Money they can withdraw
    pending_balance = Column(Numeric(12, 2), default=0)             # Money in escrow
    
    # Platform stats (for admin)
    total_platform_earnings = Column(Numeric(12, 2), default=0)     # Your total commission
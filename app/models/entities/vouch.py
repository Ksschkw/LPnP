from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.database import Base

class Vouch(Base):
    __tablename__ = "vouches"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # FOREIGN KEYS: Which service and who's vouching?
    service_id = Column(String(36), ForeignKey('services.id'), nullable=False)
    voucher_user_id = Column(String(36), ForeignKey('users.id'), nullable=True)  # Can be NULL if non-user
    
    # Vouch Details
    voucher_phone = Column(String(20), nullable=False)               # Phone of person vouching
    vouch_type = Column(String(20), nullable=False)                  # trusted, quick
    points_given = Column(Integer, nullable=False)                   # 50 for trusted, 10 for quick
    comment = Column(Text, nullable=True)                            # What they said
    is_retracted = Column(Boolean, default=False)                    # Did they take it back?
    
    created_at = Column(DateTime, server_default=func.now())
    
    # RELATIONSHIP: Who gave this vouch (if they're a registered user)
    voucher_user = relationship("User", backref="vouches_given")
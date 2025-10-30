from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.database import Base

class Review(Base):
    __tablename__ = "reviews"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # FOREIGN KEYS
    job_id = Column(String(36), ForeignKey('jobs.id'), nullable=False)       # Which job is this for?
    reviewer_id = Column(String(36), ForeignKey('users.id'), nullable=False) # Who's writing the review?
    reviewee_id = Column(String(36), ForeignKey('users.id'), nullable=False) # Who's being reviewed?
    
    # Review Content
    review_type = Column(String(20), nullable=False)                 # buyer_to_seller, seller_to_buyer
    rating = Column(Integer, nullable=False)                         # 1-5 stars
    comment = Column(Text, nullable=True)                            # Written feedback
    is_visible = Column(Boolean, default=True)                       # Can people see this?
    
    # Timing
    created_at = Column(DateTime, server_default=func.now())
    released_at = Column(DateTime, nullable=True)                    # When both reviews are released
    
    # ========== RELATIONSHIPS ==========
    
    # Who wrote this review
    reviewer = relationship("User", foreign_keys=[reviewer_id], backref="reviews_written")
    
    # Who this review is about
    reviewee = relationship("User", foreign_keys=[reviewee_id], backref="reviews_received")
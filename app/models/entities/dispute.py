from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.database import Base

class Dispute(Base):
    __tablename__ = "disputes"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # FOREIGN KEYS
    job_id = Column(String(36), ForeignKey('jobs.id'), nullable=False)
    raised_by_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    resolved_by_id = Column(String(36), ForeignKey('users.id'), nullable=True)  # Which admin resolved it
    
    # Dispute Details
    reason = Column(String(100), nullable=False)                    # Why the dispute was raised
    status = Column(String(20), default="open")                     # open, in_progress, resolved
    resolution_stage = Column(String(20), default="initial")        # initial, escalated, final
    
    # Communication
    initial_complaint = Column(Text, nullable=False)                # What the problem is
    respondent_response = Column(Text, nullable=True)               # Other side's story
    admin_notes = Column(Text, nullable=True)                       # Admin internal notes
    
    # Resolution
    final_decision = Column(String(100), nullable=True)             # What was decided
    refund_amount = Column(Numeric(10, 2), nullable=True)           # Money to refund
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    escalated_at = Column(DateTime, nullable=True)                  # When it went to admin
    resolved_at = Column(DateTime, nullable=True)                   # When it was closed
    
    # ========== RELATIONSHIPS ==========
    
    # Who raised this dispute
    raised_by = relationship("User", foreign_keys=[raised_by_id], backref="disputes_raised")
    
    # Which admin resolved it (if any)
    resolved_by = relationship("User", foreign_keys=[resolved_by_id], backref="disputes_resolved")
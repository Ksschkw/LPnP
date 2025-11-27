from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.config.database import Base

class Job(Base):
    __tablename__ = "jobs"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # FOREIGN KEYS: The person that is buying what service
    buyer_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    service_id = Column(String(36), ForeignKey('services.id'), nullable=False)
    
    # Job Details
    job_type = Column(String(50), nullable=False)                    # instant, scheduled, recurring
    status = Column(String(20), default="pending")                   # pending, accepted, in_progress, completed, cancelled
    price_agreed = Column(Numeric(10, 2), nullable=False)            # Final agreed price
    
    # Requirements & Location
    buyer_requirements = Column(Text, nullable=True)                 # What the buyer needs
    work_address = Column(Text, nullable=True)                       # Full address
    work_location = Column(String(100), nullable=True)               # Simplified location
    
    # Timing
    scheduled_time = Column(DateTime, nullable=True)                 # When the job should happen
    started_at = Column(DateTime, nullable=True)                     # When work actually started
    completed_at = Column(DateTime, nullable=True)                   # When work finished
    estimated_duration_minutes = Column(Integer, nullable=True)      # How long it should take
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # ========== RELATIONSHIPS ==========
    
    # MANY-TO-ONE: One buyer can have many jobs
    buyer = relationship("User", foreign_keys=[buyer_id], backref="jobs_as_buyer")
    
    # ONE-TO-ONE: One job has one payment
    payment = relationship("Payment", backref="job", uselist=False)
    
    # ONE-TO-MANY: One job can have many reviews
    reviews = relationship("Review", backref="job")
    
    # ONE-TO-MANY: One job can have many disputes
    disputes = relationship("Dispute", backref="job")
    
    # ONE-TO-MANY: One job can have many messages
    messages = relationship("Message", backref="job")
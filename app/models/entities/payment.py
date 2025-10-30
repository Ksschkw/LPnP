from sqlalchemy import Column, String, Integer, Boolean, DateTime, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.database import Base

class Payment(Base):
    __tablename__ = "payments"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # FOREIGN KEY
    job_id = Column(String(36), ForeignKey('jobs.id'), nullable=False)
    
    # Payment Details
    amount = Column(Numeric(10, 2), nullable=False)                 # How much money
    status = Column(String(20), default="pending")                  # pending, held_in_escrow, released, refunded
    gateway_reference = Column(String(100), nullable=True)          # ID from payment provider
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # RELATIONSHIP: This payment belongs to one job
    # (defined in Job model as uselist=False for one-to-one)
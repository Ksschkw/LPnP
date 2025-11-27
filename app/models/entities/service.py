from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.config.database import Base

class Service(Base):
    __tablename__ = "services"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # FOREIGN KEY: Which user owns this service?
    seller_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    
    # Service Details
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    base_price = Column(Numeric(10, 2), nullable=False)          # e.g., 5000.00
    hourly_rate = Column(Numeric(10, 2), nullable=True)          # e.g., 2000.00 per hour
    service_radius_km = Column(Integer, default=10)              # How far they'll travel
    
    # Location (simplified for now)
    current_location = Column(String(100), nullable=True)        # e.g., "Lagos, Nigeria"
    
    # Status
    is_available_now = Column(Boolean, default=True)
    status = Column(String(20), default="draft")                 # draft, vouching, active, inactive
    trust_points = Column(Integer, default=0)                    # From vouches
    completion_count = Column(Integer, default=0)                # How many jobs completed
    total_earnings = Column(Numeric(12, 2), default=0)           # Total money earned
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # ========== RELATIONSHIPS ==========
    
    # ONE-TO-MANY: One user can have many services
    seller = relationship("User", backref="services")
    
    # MANY-TO-MANY: One service can be in multiple categories
    categories = relationship("ServiceCategory", secondary="service_service_categories", back_populates="services")
    
    # ONE-TO-MANY: One service can have many jobs
    jobs = relationship("Job", backref="service")
    
    # ONE-TO-MANY: One service can have many vouches
    vouches = relationship("Vouch", backref="service")
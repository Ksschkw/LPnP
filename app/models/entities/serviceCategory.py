from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.database import Base

class ServiceCategory(Base):
    __tablename__ = "service_categories"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    icon_url = Column(String(500), nullable=True)
    
    # SELF-REFERENCE: A category can have a parent category
    # Example: "Plumbing" → parent = "Home Services"
    parent_id = Column(String(36), ForeignKey('service_categories.id'), nullable=True)
    
    min_trust_points = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    
    # RELATIONSHIP: This category's subcategories
    # This creates a tree structure: Parent → Children
    subcategories = relationship("ServiceCategory", backref="parent", remote_side=[id])
    
    # RELATIONSHIP: Services in this category (through the junction table)
    services = relationship("Service", secondary="service_service_categories", back_populates="categories")
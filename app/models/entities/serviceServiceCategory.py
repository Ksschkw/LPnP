from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.sql import func
import uuid
from app.database import Base

class ServiceServiceCategory(Base):
    __tablename__ = "service_service_categories"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # FOREIGN KEYS: Links service + category
    service_id = Column(String(36), ForeignKey('services.id'), nullable=False)
    category_id = Column(String(36), ForeignKey('service_categories.id'), nullable=False)
    
    created_at = Column(DateTime, server_default=func.now())
    
    # NO RELATIONSHIPS HERE - This is just a connection table
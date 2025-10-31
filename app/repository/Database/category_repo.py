from sqlalchemy.orm import Session
from app.models.entities.serviceCategory import ServiceCategory
import uuid

class CategoryRepository:
    """Handles all database operations for service categories"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, category_id: str) -> ServiceCategory:
        """Find category by ID"""
        return self.db.query(ServiceCategory).filter(ServiceCategory.id == category_id).first()
    
    def get_all(self, skip: int = 0, limit: int = 100) -> list[ServiceCategory]:
        """Get all categories"""
        return self.db.query(ServiceCategory).offset(skip).limit(limit).all()
    
    def get_root_categories(self) -> list[ServiceCategory]:
        """Get main categories (no parent)"""
        return self.db.query(ServiceCategory).filter(ServiceCategory.parent_id.is_(None)).all()
    
    def get_subcategories(self, parent_id: str) -> list[ServiceCategory]:
        """Get subcategories of a parent category"""
        return self.db.query(ServiceCategory).filter(ServiceCategory.parent_id == parent_id).all()
    
    def create(self, name: str, description: str = None, parent_id: str = None) -> ServiceCategory:
        """Create a new category"""
        category = ServiceCategory(
            id=str(uuid.uuid4()),
            name=name,
            description=description,
            parent_id=parent_id
        )
        
        self.db.add(category)
        self.db.commit()
        self.db.refresh(category)
        return category
    
    # All lookups by name
    def get_by_name(self, name: str) -> ServiceCategory:
        """Find category by name (case-sensitive)"""
        return self.db.query(ServiceCategory).filter(ServiceCategory.name == name).first()
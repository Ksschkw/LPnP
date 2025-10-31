from sqlalchemy.orm import Session, joinedload
from app.models.entities.service import Service
from app.models.entities.serviceCategory import ServiceCategory
from app.models.entities.serviceServiceCategory import ServiceServiceCategory
from app.models.Requests.service_requests import ServiceCreateRequest
import uuid

class ServiceRepository:
    """Handles all database operations for services"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, service_id: str) -> Service:
        """Find service by ID including seller and category info"""
        return (self.db.query(Service)
                .options(
                    joinedload(Service.seller),
                    joinedload(Service.categories)  # This automatically loads category names
                )
                .filter(Service.id == service_id)
                .first())
    
    def get_by_seller(self, seller_id: str, skip: int = 0, limit: int = 100) -> list[Service]:
        """Get all services offered by a specific user"""
        return (self.db.query(Service)
                .options(joinedload(Service.categories))
                .filter(Service.seller_id == seller_id)
                .offset(skip)
                .limit(limit)
                .all())
    
    def get_active_services(self, skip: int = 0, limit: int = 100) -> list[Service]:
        """Get only services that are currently active and available"""
        return (self.db.query(Service)
                .options(joinedload(Service.seller), joinedload(Service.categories))
                .filter(Service.status == "active")
                .offset(skip)
                .limit(limit)
                .all())
    
    def get_services_by_category(self, category_id: str, skip: int = 0, limit: int = 100) -> list[Service]:
        """Get all services in a specific category (like Plumbing, Electrical, etc.)"""
        return (self.db.query(Service)
                .options(joinedload(Service.seller), joinedload(Service.categories))
                .join(ServiceServiceCategory)
                .filter(ServiceServiceCategory.category_id == category_id)
                .offset(skip)
                .limit(limit)
                .all())
    
    def create(self, service_data: ServiceCreateRequest, seller_id: str, category_name: str) -> Service:
        """Create a new service and link to category by name"""
        
        # Find category by name
        category = self.db.query(ServiceCategory).filter(ServiceCategory.name == category_name).first()
        if not category:
            raise ValueError(f"Category '{category_name}' not found")
        
        # Create the service
        service = Service(
            id=str(uuid.uuid4()),
            seller_id=seller_id,
            title=service_data.title,
            description=service_data.description,
            base_price=service_data.base_price,
            hourly_rate=service_data.hourly_rate,
            service_radius_km=service_data.service_radius_km,
            current_location=service_data.current_location,
            status="draft"  # New services start as draft until vouches are collected
        )
        
        self.db.add(service)
        self.db.flush()  # Flush to get the service ID without committing
        
        # Link service to the SINGLE category using the actual category ID
        link = ServiceServiceCategory(
            id=str(uuid.uuid4()),
            service_id=service.id,
            category_id=category.id  # Use the actual UUID
        )
        self.db.add(link)
        self.db.commit()
        self.db.refresh(service)
        
        # Reload with categories to include them in the response
        service_with_categories = self.get_by_id(service.id)
        return service_with_categories
    
    def update(self, service_id: str, update_data: dict) -> Service:
        """Update service information"""
        service = self.get_by_id(service_id)
        if service:
            for field, new_value in update_data.items():
                if hasattr(service, field) and new_value is not None:
                    setattr(service, field, new_value)
            self.db.commit()
            self.db.refresh(service)
        return service
    
    def delete(self, service_id: str) -> bool:
        """Remove a service from the platform"""
        service = self.get_by_id(service_id)
        if service:
            # First remove connections to categories
            self.db.query(ServiceServiceCategory).filter(
                ServiceServiceCategory.service_id == service_id
            ).delete()
            
            # Then delete the service itself
            self.db.delete(service)
            self.db.commit()
            return True
        return False
    
    def activate_service(self, service_id: str) -> Service:
        """Mark a service as active (ready to receive jobs)"""
        service = self.update(service_id, {"status": "active"})
        if service:
            # Reload with categories
            return self.get_by_id(service_id)
        return None
    
    def deactivate_service(self, service_id: str) -> Service:
        """Mark a service as inactive (temporarily not available)"""
        service = self.update(service_id, {"status": "inactive"})
        if service:
            # Reload with categories
            return self.get_by_id(service_id)
        return None
    
    def add_trust_points(self, service_id: str, points: int) -> Service:
        """Add trust points to a service from vouches"""
        service = self.get_by_id(service_id)
        if service:
            service.trust_points += points
            self.db.commit()
            self.db.refresh(service)
        return service

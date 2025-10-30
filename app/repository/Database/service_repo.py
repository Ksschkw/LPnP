from sqlalchemy.orm import Session
from app.models.entities.service import Service
from app.models.entities.serviceServiceCategory import ServiceServiceCategory
from app.models.Requests.service_requests import ServiceCreateRequest
import uuid

class ServiceRepository:
    """Handles all database operations for services"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, service_id: str) -> Service:
        """Find service by ID including seller and category info"""
        return self.db.query(Service).filter(Service.id == service_id).first()
    
    def get_by_seller(self, seller_id: str, skip: int = 0, limit: int = 100) -> list[Service]:
        """Get all services offered by a specific user"""
        return self.db.query(Service).filter(Service.seller_id == seller_id).offset(skip).limit(limit).all()
    
    def get_active_services(self, skip: int = 0, limit: int = 100) -> list[Service]:
        """Get only services that are currently active and available"""
        return self.db.query(Service).filter(Service.status == "active").offset(skip).limit(limit).all()
    
    def get_services_by_category(self, category_id: str, skip: int = 0, limit: int = 100) -> list[Service]:
        """Get all services in a specific category (like Plumbing, Electrical, etc.)"""
        return (self.db.query(Service)
                .join(ServiceServiceCategory)
                .filter(ServiceServiceCategory.category_id == category_id)
                .offset(skip)
                .limit(limit)
                .all())
    
    def create(self, service_data: ServiceCreateRequest, seller_id: str) -> Service:
        """Create a new service offering"""
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
        self.db.commit()
        self.db.refresh(service)
        
        # Connect service to its categories
        for category_id in service_data.category_ids:
            service_category = ServiceServiceCategory(
                id=str(uuid.uuid4()),
                service_id=service.id,
                category_id=category_id
            )
            self.db.add(service_category)
        
        self.db.commit()
        return service
    
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
        return self.update(service_id, {"status": "active"})
    
    def deactivate_service(self, service_id: str) -> Service:
        """Mark a service as inactive (temporarily not available)"""
        return self.update(service_id, {"status": "inactive"})
    
    def add_trust_points(self, service_id: str, points: int) -> Service:
        """Add trust points to a service from vouches"""
        service = self.get_by_id(service_id)
        if service:
            service.trust_points += points
            self.db.commit()
            self.db.refresh(service)
        return service
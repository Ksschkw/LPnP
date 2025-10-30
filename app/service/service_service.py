from app.repository.Database.service_repo import ServiceRepository
from app.repository.Database.category_repo import CategoryRepository
from app.models.Requests.service_requests import ServiceCreateRequest
from app.models.Responses.service_responses import ServiceBaseResponse, ServiceDetailResponse #ServiceResponse
import logging

logger = logging.getLogger(__name__)

class ServiceService:
    """Contains the business rules and logic for service operations"""
    
    def __init__(self, db):
        self.service_repo = ServiceRepository(db)
        self.category_repo = CategoryRepository(db)
    
    def get_service(self, service_id: str) -> ServiceDetailResponse:
        """Get full details of a specific service"""
        service = self.service_repo.get_by_id(service_id)
        if not service:
            return None
        return ServiceDetailResponse.model_validate(service)
    
    def get_services_by_seller(self, seller_id: str, skip: int = 0, limit: int = 100) -> list[ServiceBaseResponse]:
        """Get all services offered by a specific user"""
        services = self.service_repo.get_by_seller(seller_id, skip, limit)
        return [ServiceBaseResponse.model_validate(service) for service in services]
    
    def get_active_services(self, skip: int = 0, limit: int = 100) -> list[ServiceBaseResponse]:
        """Get all services that are currently active and available"""
        services = self.service_repo.get_active_services(skip, limit)
        return [ServiceBaseResponse.model_validate(service) for service in services]
    
    def create_service(self, service_data: ServiceCreateRequest, seller_id: str) -> ServiceDetailResponse:
        """Create a new service offering with validation"""
        # Verify all category IDs exist
        for category_id in service_data.category_ids:
            category = self.category_repo.get_by_id(category_id)
            if not category:
                raise ValueError(f"Category '{category_id}' does not exist")
        
        # Validate pricing
        if service_data.base_price <= 0:
            raise ValueError("Service price must be greater than 0")
        
        if service_data.hourly_rate and service_data.hourly_rate <= 0:
            raise ValueError("Hourly rate must be greater than 0")
        
        # Validate service radius
        if service_data.service_radius_km < 1 or service_data.service_radius_km > 100:
            raise ValueError("Service radius must be between 1 and 100 km")
        
        # Create the service
        service = self.service_repo.create(service_data, seller_id)
        logger.info(f"New service created: {service.title} by seller {seller_id}")
        return ServiceDetailResponse.model_validate(service)
    
    def update_service(self, service_id: str, update_data: dict) -> ServiceDetailResponse:
        """Update service information"""
        service = self.service_repo.update(service_id, update_data)
        if not service:
            return None
        return ServiceDetailResponse.model_validate(service)
    
    def delete_service(self, service_id: str) -> bool:
        """Remove a service from the platform"""
        success = self.service_repo.delete(service_id)
        if success:
            logger.info(f"Service deleted: {service_id}")
        return success
    
    def activate_service(self, service_id: str) -> ServiceDetailResponse:
        """Make a service active and visible to buyers"""
        service = self.service_repo.activate_service(service_id)
        if not service:
            return None
        logger.info(f"Service activated: {service_id}")
        return ServiceDetailResponse.model_validate(service)
    
    def add_vouch_points(self, service_id: str, points: int) -> ServiceDetailResponse:
        """Add trust points to a service from community vouches"""
        service = self.service_repo.add_trust_points(service_id, points)
        if not service:
            return None
        
        # If service reaches 100 points, automatically activate it
        if service.trust_points >= 100 and service.status == "draft":
            service = self.service_repo.activate_service(service_id)
            logger.info(f"Service auto-activated from vouches: {service_id}")
        
        return ServiceDetailResponse.model_validate(service)
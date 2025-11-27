from app.repository.Database.service_repo import ServiceRepository
from app.repository.Database.category_repo import CategoryRepository
from app.models.Requests.service_requests import ServiceCreateRequest
from app.models.Responses.service_responses import ServiceBaseResponse, ServiceDetailResponse
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
        logger.info(f"Looking for services by seller: {seller_id}")
        
        try:
            services = self.service_repo.get_by_seller(seller_id, skip, limit)
            logger.info(f"Repository returned: {len(services) if services else 0} services")
            
            # Return empty list if no services found (this is normal)
            if not services:
                logger.info(f"No services found for seller {seller_id} - returning empty list")
                return []
            
            validated_services = []
            for service in services:
                try:
                    validated = ServiceBaseResponse.model_validate(service)
                    validated_services.append(validated)
                except Exception as e:
                    logger.error(f"Error validating service {service.id}: {e}")
            
            logger.info(f"Returning {len(validated_services)} validated services")
            return validated_services
            
        except Exception as e:
            logger.error(f"Error in get_services_by_seller: {e}")
            return []
    
    def get_active_services(self, skip: int = 0, limit: int = 100) -> list[ServiceBaseResponse]:
        """Get all services that are currently active and available"""
        services = self.service_repo.get_active_services(skip, limit)
        return [ServiceBaseResponse.model_validate(service) for service in services]
    
    def create_service(self, service_data: ServiceCreateRequest, seller_id: str) -> ServiceDetailResponse:
        """Create a new service with category by name"""
        
        logger.info(f"Creating service: {service_data.title} for seller {seller_id} in category '{service_data.category_name}'")
        
        # Validate category exists
        category = self.category_repo.get_by_name(service_data.category_name)
        if not category:
            logger.warning(f"Category not found: {service_data.category_name}")
            raise ValueError(f"Category '{service_data.category_name}' does not exist")
            
        # Validate pricing
        if service_data.base_price <= 0:
            raise ValueError("Service price must be greater than 0")
        
        if service_data.hourly_rate and service_data.hourly_rate <= 0:
            raise ValueError("Hourly rate must be greater than 0")
        
        # Validate service radius
        if service_data.service_radius_km < 1 or service_data.service_radius_km > 100:
            raise ValueError("Service radius must be between 1 and 100 km")
        
        # Create the service
        service = self.service_repo.create(service_data, seller_id, service_data.category_name)
        logger.info(f"Service created: {service.id} - {service.title} by seller {seller_id}")
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

    # NEW SMART SEARCH METHOD
    def search_services(
        self,
        category_name: str = None,
        location: str = None,
        max_distance_km: int = 10,
        min_trust_score: int = 0,
        max_price: float = None,
        skip: int = 0,
        limit: int = 100
    ) -> list[ServiceBaseResponse]:
        """
        Smart service search with intelligent matching
        - Fuzzy category name matching
        - Intelligent location search with suggestions
        - Error handling for typos and variations
        """
        
        try:
            # Validate inputs
            if max_distance_km < 1 or max_distance_km > 100:
                raise ValueError("Search radius must be between 1 and 100 km")
            
            if min_trust_score < 0:
                raise ValueError("Trust score cannot be negative")
            
            if max_price and max_price < 0:
                raise ValueError("Price cannot be negative")
            
            # Clean and normalize search inputs
            cleaned_category = category_name.strip().lower() if category_name else None
            cleaned_location = location.strip().lower() if location else None
            
            # Perform smart search
            services = self.service_repo.search_services_by_filters(
                category_name=cleaned_category,
                location_query=cleaned_location,
                max_distance_km=max_distance_km,
                min_trust_score=min_trust_score,
                max_price=max_price,
                skip=skip,
                limit=limit
            )
            
            # If no results with filters, try relaxed search
            if not services and (cleaned_category or cleaned_location):
                logger.info(f"No exact matches found, trying relaxed search for: {cleaned_category}, {cleaned_location}")
                
                # Relax trust score for more results
                relaxed_trust = max(0, min_trust_score - 10)
                services = self.service_repo.search_services_by_filters(
                    category_name=cleaned_category,
                    location_query=cleaned_location,
                    max_distance_km=max_distance_km + 5,  # Expand search radius
                    min_trust_score=relaxed_trust,
                    max_price=max_price,
                    skip=skip,
                    limit=limit
                )
            
            # ✅ CONVERT TO RESPONSE MODELS FIRST
            service_responses = [ServiceBaseResponse.model_validate(service) for service in services]
            
            # ✅ NOW SORT BY BADGE PRIORITY (after conversion to response models)
            def get_badge_priority(service_response):
                badge_priorities = {
                    "legend": 5,
                    "elite": 4, 
                    "verified": 3,
                    "trusted": 2,
                    "newbie": 1
                }
                seller_badge = service_response.seller.badge_level
                return badge_priorities.get(seller_badge, 0)
            
            # Sort: higher badges first, then trust points
            service_responses.sort(key=lambda s: (
                -get_badge_priority(s),  # Higher badges first
                -s.trust_points          # Then higher trust points
            ))
            
            return service_responses
            
        except Exception as e:
            logger.error(f"Search error: {str(e)}")
            # Return empty results instead of crashing
            return []
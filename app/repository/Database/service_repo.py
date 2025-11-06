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
                    joinedload(Service.categories)
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
        """Get all services in a specific category"""
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
            status="draft"
        )
        
        self.db.add(service)
        self.db.flush()
        
        # Link service to the SINGLE category using the actual category ID
        link = ServiceServiceCategory(
            id=str(uuid.uuid4()),
            service_id=service.id,
            category_id=category.id
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
            return self.get_by_id(service_id)
        return None
    
    def deactivate_service(self, service_id: str) -> Service:
        """Mark a service as inactive (temporarily not available)"""
        service = self.update(service_id, {"status": "inactive"})
        if service:
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

    # NEW SMART SEARCH METHODS
    def search_services_by_filters(
        self, 
        category_name: str = None,
        location_query: str = None,
        max_distance_km: int = 10,
        min_trust_score: int = 0,
        max_price: float = None,
        skip: int = 0, 
        limit: int = 100
    ) -> list[Service]:
        """Smart search with fuzzy matching"""
        
        query = self.db.query(Service).options(
            joinedload(Service.seller), 
            joinedload(Service.categories)
        ).filter(Service.status == "active")
        
        # FIXED: Better category name matching
        if category_name:
            # Clean the category name
            clean_category = category_name.strip().lower()
            
            # Find categories with similar names (more flexible)
            from sqlalchemy import or_
            matching_categories = self.db.query(ServiceCategory).filter(
                or_(
                    ServiceCategory.name.ilike(f"%{clean_category}%"),
                    ServiceCategory.name.ilike(f"%{clean_category.title()}%"),
                    ServiceCategory.name.ilike(f"{clean_category}%"),
                    ServiceCategory.name.ilike(f"%{clean_category}")
                )
            ).all()
            
            if matching_categories:
                category_ids = [cat.id for cat in matching_categories]
                query = query.join(ServiceServiceCategory).filter(
                    ServiceServiceCategory.category_id.in_(category_ids)
                )
            else:
                # If no categories match, return empty results
                return []
        
        # Filter by trust score
        if min_trust_score > 0:
            query = query.filter(Service.trust_points >= min_trust_score)
        
        # Filter by price
        if max_price:
            query = query.filter(Service.base_price <= max_price)
        
        # Get all services first for location processing
        all_services = query.offset(skip).limit(limit * 3).all()
        
        # Smart location filtering
        if location_query:
            filtered_services = self._filter_services_by_location(all_services, location_query, max_distance_km)
        else:
            filtered_services = all_services
        
        # Sort by relevance: trust points first, then proximity
        filtered_services.sort(key=lambda s: (
            -s.trust_points,
            self._calculate_location_score(s.current_location, location_query) if location_query else 0
        ))
        
        return filtered_services[:limit]

    def _filter_services_by_location(self, services: list, location_query: str, max_distance_km: int) -> list[Service]:
        """Intelligent location filtering with fuzzy matching"""
        if not location_query:
            return services
        
        location_query_clean = location_query.lower().strip()
        
        # Categorize services by location match quality
        exact_matches = []
        partial_matches = []
        nearby_suggestions = []
        
        for service in services:
            if not service.current_location:
                continue
                
            service_location = service.current_location.lower()
            
            # Exact match (contains the exact query)
            if location_query_clean in service_location:
                exact_matches.append(service)
            
            # Partial match (shared words)
            elif self._has_matching_words(location_query_clean, service_location):
                partial_matches.append(service)
            
            # Nearby suggestions (based on common area names)
            elif self._is_nearby_location(location_query_clean, service_location):
                nearby_suggestions.append(service)
        
        # Combine results with exact matches first, then partial, then nearby
        return exact_matches + partial_matches + nearby_suggestions

    def _has_matching_words(self, query: str, location: str) -> bool:
        """Check if query and location share any significant words"""
        query_words = set(query.split())
        location_words = set(location.split())
        
        # Common words to ignore
        ignore_words = {'area', 'street', 'road', 'avenue', 'lane', 'close', 'estate', 'phase'}
        
        significant_query_words = query_words - ignore_words
        significant_location_words = location_words - ignore_words
        
        return bool(significant_query_words & significant_location_words)

    def _is_nearby_location(self, query: str, location: str) -> bool:
        """Check if locations are likely nearby based on common area patterns"""
        # Common area relationships (expand this based on your location data)
        area_relationships = {
            'ikeja': ['allen', 'ogba', 'ojota'],
            'lekki': ['ikate', 'ajah', 'vgc', 'chevyview'],
            'victoria island': ['vi', 'ikoyi', 'lagos island'],
            'surulere': ['itan', 'adesanya', 'adesoye']
        }
        
        for main_area, nearby_areas in area_relationships.items():
            if query in main_area and any(area in location for area in nearby_areas):
                return True
            if query in nearby_areas and main_area in location:
                return True
        
        return False

    def _calculate_location_score(self, service_location: str, query_location: str) -> int:
        """Calculate how well service location matches query"""
        if not service_location or not query_location:
            return 0
        
        service_loc = service_location.lower()
        query_loc = query_location.lower()
        
        score = 0
        
        # Exact match bonus
        if query_loc in service_loc:
            score += 100
        
        # Word match bonus
        query_words = set(query_loc.split())
        service_words = set(service_loc.split())
        common_words = query_words & service_words
        score += len(common_words) * 10
        
        return score

    def get_services_by_category_name(self, category_name: str, skip: int = 0, limit: int = 100) -> list[Service]:
        """Get services by category name (fuzzy matching)"""
        # Find categories with similar names
        matching_categories = self.db.query(ServiceCategory).filter(
            ServiceCategory.name.ilike(f"%{category_name}%")
        ).all()
        
        if not matching_categories:
            return []
        
        category_ids = [cat.id for cat in matching_categories]
        
        return (self.db.query(Service)
                .options(joinedload(Service.seller), joinedload(Service.categories))
                .join(ServiceServiceCategory)
                .filter(ServiceServiceCategory.category_id.in_(category_ids))
                .filter(Service.status == "active")
                .offset(skip)
                .limit(limit)
                .all())

    def get_location_suggestions(self, query: str, limit: int = 10) -> list[str]:
        """Get location suggestions for autocomplete"""
        results = (self.db.query(Service.current_location)
                .filter(
                    Service.current_location.isnot(None),
                    Service.current_location.ilike(f"%{query}%")
                )
                .distinct()
                .limit(limit)
                .all())
        return [result[0] for result in results if result[0]]
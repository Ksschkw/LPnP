from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional

import logging
logging.basicConfig(level=logging.INFO)
logging.BASIC_FORMATTER = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logger = logging.getLogger(__name__)

from app.dependencies import get_service_service, get_service_repo, get_category_repo
from app.service.service_service import ServiceService
from app.repository.Database.service_repo import ServiceRepository
from app.repository.Database.category_repo import CategoryRepository
from app.models.entities.user import User
from app.models.Requests.service_requests import ServiceCreateRequest, ServiceUpdateRequest
from app.models.Responses.service_responses import ServiceBaseResponse, ServiceDetailResponse
from app.auth import get_current_user

router = APIRouter(prefix="/services", tags=["services"])

@router.get("/", response_model=List[ServiceBaseResponse])
def get_active_services(skip: int = 0, limit: int = 100, service_service: ServiceService = Depends(get_service_service)):
    """Get all services that are currently active and available"""
    return service_service.get_active_services(skip, limit)

@router.get("/my", response_model=List[ServiceBaseResponse])
async def get_my_services(
    current_user: User = Depends(get_current_user),
    service_service: ServiceService = Depends(get_service_service)
):
    logger.info(f"User {current_user.id} fetching their services")
    logger.info(f"Current user ID: {current_user.id}")
    
    services = service_service.get_services_by_seller(current_user.id)
    logger.info(f"Found {len(services)} services for user {current_user.id}")
    
    if not services:
        logger.info(f"No services found for user {current_user.id} - returning empty list")
        return []
    
    return services

@router.get("/{service_id}", response_model=ServiceDetailResponse)
def get_service(service_id: str, service_service: ServiceService = Depends(get_service_service)):
    """Get full details of a specific service"""
    service = service_service.get_service(service_id)
    
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found"
        )
    return service

@router.get("/seller/{seller_id}", response_model=List[ServiceBaseResponse])
def get_services_by_seller(seller_id: str, skip: int = 0, limit: int = 100, service_service: ServiceService = Depends(get_service_service)):
    """Get all services offered by a specific seller"""
    return service_service.get_services_by_seller(seller_id, skip, limit)

@router.post("/", response_model=ServiceDetailResponse, status_code=status.HTTP_201_CREATED)
async def create_service(
    service_data: ServiceCreateRequest, 
    current_user: User = Depends(get_current_user),
    service_service: ServiceService = Depends(get_service_service)
):
    """Create a new service offering"""
    try:
        logger.info(f"User {current_user.id} creating service: {service_data.title} by {current_user.id}")
        return service_service.create_service(service_data, seller_id=current_user.id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.put("/{service_id}", response_model=ServiceDetailResponse)
async def update_service(
    service_id: str, 
    update_data: ServiceUpdateRequest,
    current_user: User = Depends(get_current_user),  # ADD THIS
    service_service: ServiceService = Depends(get_service_service)
):
    """Update service information - ONLY if you own it"""
    # First verify the user owns this service
    service = service_service.get_service(service_id)
    if not service:
        raise HTTPException(404, "Service not found")
    
    if service.seller.id != current_user.id:
        raise HTTPException(403, "You can only update your own services")
    
    update_dict = update_data.model_dump(exclude_unset=True)
    service = service_service.update_service(service_id, update_dict)
    return service

@router.delete("/{service_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_service(
    service_id: str, 
    current_user: User = Depends(get_current_user),  # ADD THIS
    service_service: ServiceService = Depends(get_service_service)
):
    """Remove a service - ONLY if you own it"""
    # Verify ownership
    service = service_service.get_service(service_id)
    if not service:
        raise HTTPException(404, "Service not found")
    
    if service.seller.id != current_user.id:
        raise HTTPException(403, "You can only delete your own services")
    
    success = service_service.delete_service(service_id)
    if not success:
        raise HTTPException(404, "Service not found")

@router.post("/{service_id}/activate", response_model=ServiceDetailResponse)
def activate_service(service_id: str, service_service: ServiceService = Depends(get_service_service)):
    """Activate a service (make it visible to buyers)"""
    service = service_service.activate_service(service_id)
    
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found"
        )
    return service

# NEW SMART SEARCH ENDPOINTS
@router.get("/search/", response_model=List[ServiceBaseResponse])
def search_services(
    category_name: Optional[str] = None,
    location: Optional[str] = None,
    max_distance_km: int = 10,
    min_trust_score: int = 0,
    max_price: Optional[float] = None,
    service_service: ServiceService = Depends(get_service_service)
):
    """
    Smart service search with intelligent matching
    
    Features:
    - Search by category name (not ID) with fuzzy matching
    - Location search with typo tolerance and suggestions
    - Automatic nearby suggestions when exact matches are few
    - Error handling for invalid inputs
    """
    
    try:
        results = service_service.search_services(
            category_name=category_name,
            location=location,
            max_distance_km=max_distance_km,
            min_trust_score=min_trust_score,
            max_price=max_price
        )
        
        # Log search performance
        logger.info(f"Search completed: category='{category_name}', location='{location}', results={len(results)}")
        
        return results
        
    except ValueError as e:
        # Handle validation errors gracefully
        logger.warning(f"Search validation error: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        # Handle unexpected errors gracefully
        logger.error(f"Search system error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Search service temporarily unavailable. Please try again."
        )

@router.get("/categories/search/")
def search_categories(
    query: str,
    category_repo: CategoryRepository = Depends(get_category_repo)
):
    """Search categories by name for autocomplete"""
    if len(query.strip()) < 2:
        return []
    
    categories = category_repo.search_by_name(query)
    return [{"id": cat.id, "name": cat.name} for cat in categories]

@router.get("/locations/suggestions/")
def get_location_suggestions(
    query: str,
    service_repo: ServiceRepository = Depends(get_service_repo)
):
    """Get location suggestions for autocomplete"""
    if len(query.strip()) < 2:
        return []
    
    # Get unique locations from services
    locations = service_repo.get_location_suggestions(query)
    return [loc for loc in locations if loc]
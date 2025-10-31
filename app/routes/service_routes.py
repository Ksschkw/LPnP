from fastapi import APIRouter, Depends, HTTPException, status
# from sqlalchemy.orm import Session
from typing import List

import logging
logging.basicConfig(level=logging.INFO)
logging.BASIC_FORMATTER = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logger = logging.getLogger(__name__)


# from app.database import get_db
# from app.dependencies import get_user_service
from app.dependencies import get_service_service
from app.models.entities.user import User
from app.service.service_service import ServiceService
from app.models.Requests.service_requests import ServiceCreateRequest, ServiceUpdateRequest
from app.models.Responses.service_responses import ServiceBaseResponse, ServiceDetailResponse #, ServiceResponse

from app.auth import get_current_user
# Create router for all service-related endpoints
router = APIRouter(prefix="/services", tags=["services"])

@router.get("/", response_model=List[ServiceBaseResponse])
def get_active_services(skip: int = 0, limit: int = 100, service_service: ServiceService = Depends(get_service_service)):
    """Get all services that are currently active and available"""
    # service_service = ServiceService(db)
    return service_service.get_active_services(skip, limit)

@router.get("/my", response_model=List[ServiceBaseResponse])
async def get_my_services(
    current_user: User = Depends(get_current_user),
    service_service: ServiceService = Depends(get_service_service)
):
    logger.info(f"User {current_user.id} fetching their services")
    
    # Debug: Check if user exists and has the right ID
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
    # service_service = ServiceService(db)
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
    # service_service = ServiceService(db)
    return service_service.get_services_by_seller(seller_id, skip, limit)

@router.post("/", response_model=ServiceDetailResponse, status_code=status.HTTP_201_CREATED)
async def create_service(
    service_data: ServiceCreateRequest, 
    # seller_id: str,  # For now, we pass seller_id as query parameter
    current_user: User = Depends(get_current_user),
    service_service: ServiceService = Depends(get_service_service)
):
    """Create a new service offering"""
    # service_service = ServiceService(db)
    try:
        logger.info(f"User {current_user.id} creating service: {service_data.title} by {current_user.id}")
        return service_service.create_service(service_data, seller_id=current_user.id)
        # return service_service.create_service(service_data, seller_id)
    except ValueError as e:
        # Handle validation errors (invalid categories, pricing, etc.)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.put("/{service_id}", response_model=ServiceDetailResponse)
def update_service(service_id: str, update_data: ServiceUpdateRequest, service_service: ServiceService = Depends(get_service_service)):
    """Update service information"""
    # service_service = ServiceService(db)
    
    # Convert to dictionary, only including fields that were actually provided
    update_dict = update_data.model_dump(exclude_unset=True)#dict(exclude_unset=True)
    
    service = service_service.update_service(service_id, update_dict)
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found"
        )
    return service

@router.delete("/{service_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_service(service_id: str, service_service: ServiceService = Depends(get_service_service)):
    """Remove a service from the platform"""
    # service_service = ServiceService(db)
    success = service_service.delete_service(service_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found"
        )

@router.post("/{service_id}/activate", response_model=ServiceDetailResponse)
def activate_service(service_id: str, service_service: ServiceService = Depends(get_service_service)):
    """Activate a service (make it visible to buyers)"""
    # service_service = ServiceService(db)
    service = service_service.activate_service(service_id)
    
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found"
        )
    return service

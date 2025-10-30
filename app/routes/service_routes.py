from fastapi import APIRouter, Depends, HTTPException, status
# from sqlalchemy.orm import Session
from typing import List

# from app.database import get_db
# from app.dependencies import get_user_service
from app.dependencies import get_service_service
from app.service.service_service import ServiceService
from app.models.Requests.service_requests import ServiceCreateRequest, ServiceUpdateRequest
from app.models.Responses.service_responses import ServiceBaseResponse, ServiceDetailResponse #, ServiceResponse

# Create router for all service-related endpoints
router = APIRouter(prefix="/services", tags=["services"])

@router.get("/", response_model=List[ServiceBaseResponse])
def get_active_services(skip: int = 0, limit: int = 100, service_service: ServiceService = Depends(get_service_service)):
    """Get all services that are currently active and available"""
    # service_service = ServiceService(db)
    return service_service.get_active_services(skip, limit)


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
def create_service(
    service_data: ServiceCreateRequest, 
    seller_id: str,  # For now, we pass seller_id as query parameter
    service_service: ServiceService = Depends(get_service_service)
):
    """Create a new service offering"""
    # service_service = ServiceService(db)
    try:
        return service_service.create_service(service_data, seller_id)
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
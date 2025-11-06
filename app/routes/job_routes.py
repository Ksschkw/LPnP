from fastapi import APIRouter, Depends, HTTPException
from app.dependencies import get_job_service
from app.auth import get_current_user
from app.models.entities.user import User
from app.models.Requests.job_requests import JobCreateRequest
from app.models.Responses.job_responses import JobDetailResponse, JobBaseResponse
from typing import List

router = APIRouter(prefix="/jobs", tags=["jobs"])

@router.post("/services/{service_id}/request", response_model=JobDetailResponse)
async def create_job_request(
    service_id: str,
    job_data: JobCreateRequest,
    current_user: User = Depends(get_current_user),
    job_service=Depends(get_job_service)
):
    """Request a job for a service"""
    try:
        return job_service.create_job_request(service_id, job_data, current_user.id)
    except ValueError as e:
        raise HTTPException(400, detail=str(e))

@router.get("/my-requests", response_model=List[JobBaseResponse])
async def get_my_job_requests(
    current_user: User = Depends(get_current_user),
    job_service=Depends(get_job_service)
):
    """Get job requests I made (as buyer)"""
    return job_service.get_my_job_requests(current_user.id)

@router.get("/my-offers", response_model=List[JobDetailResponse])
async def get_my_job_offers(
    current_user: User = Depends(get_current_user),
    job_service=Depends(get_job_service)
):
    """Get job requests for my services (as seller)"""
    return job_service.get_my_job_offers(current_user.id)

@router.patch("/{job_id}/status", response_model=JobDetailResponse)
async def update_job_status(
    job_id: str,
    status: str,
    current_user: User = Depends(get_current_user),
    job_service=Depends(get_job_service)
):
    """Update job status (seller accepts/starts/completes)"""
    try:
        return job_service.update_job_status(job_id, status, current_user.id)
    except ValueError as e:
        raise HTTPException(400, detail=str(e))

@router.get("/{job_id}", response_model=JobDetailResponse)
async def get_job_details(
    job_id: str,
    current_user: User = Depends(get_current_user),
    job_service=Depends(get_job_service)
):
    """Get job details (only for participants)"""
    try:
        return job_service.get_job_details(job_id, current_user.id)
    except ValueError as e:
        raise HTTPException(400, detail=str(e))
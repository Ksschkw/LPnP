from fastapi import APIRouter, Depends, HTTPException
from app.dependencies import get_dispute_service, get_db
from app.utilities.auth import get_current_user
from app.models.entities.user import User
from app.service.dispute_service import DisputeService
from app.models.Requests.dispute_requests import DisputeCreateRequest
from app.repository.Database.dispute_repo import DisputeRepository
from typing import List
from sqlalchemy.orm import Session

router = APIRouter(prefix="/disputes", tags=["disputes"])

@router.post("/jobs/{job_id}/dispute")
async def create_dispute(
    job_id: str,
    dispute_data: DisputeCreateRequest,
    current_user: User = Depends(get_current_user),
    dispute_service: DisputeService = Depends(get_dispute_service)
):
    """Raise a dispute about a job"""
    try:
        dispute_dict = dispute_data.model_dump()
        dispute_dict['raised_by_id'] = current_user.id
        dispute_dict['job_id'] = job_id
        
        dispute = dispute_service.create_dispute(dispute_dict)
        return {
            "message": "Dispute raised successfully",
            "dispute_id": dispute.id,
            "status": dispute.status
        }
    except ValueError as e:
        raise HTTPException(400, detail=str(e))

@router.post("/{dispute_id}/respond")
async def respond_to_dispute(
    dispute_id: str,
    response: str,
    current_user: User = Depends(get_current_user),
    dispute_service: DisputeService = Depends(get_dispute_service)
):
    """Respond to a dispute as the other party"""
    try:
        dispute = dispute_service.add_respondent_response(dispute_id, current_user.id, response)
        return {
            "message": "Response submitted successfully",
            "dispute_id": dispute.id
        }
    except ValueError as e:
        raise HTTPException(400, detail=str(e))

@router.get("/my-disputes")
async def get_my_disputes(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all disputes involving the current user"""
    try:
        dispute_repo = DisputeRepository(db)
        # Get disputes where user is either the raiser or part of the job
        user_disputes = []
        
        # Disputes raised by user
        raised_disputes = dispute_repo.get_by_user(current_user.id)
        user_disputes.extend(raised_disputes)
        
        # Disputes where user is the other party (buyer/seller in the job)
        all_disputes = dispute_repo.get_all(limit=1000)
        for dispute in all_disputes:
            job = dispute.job
            if job:
                # User is the other party (not the one who raised dispute)
                if current_user.id != dispute.raised_by_id:
                    if current_user.id in [job.buyer_id, job.service.seller_id]:
                        user_disputes.append(dispute)
        
        # Remove duplicates and format response
        unique_disputes = []
        seen_ids = set()
        for dispute in user_disputes:
            if dispute.id not in seen_ids:
                seen_ids.add(dispute.id)
                unique_disputes.append({
                    "id": dispute.id,
                    "job_id": dispute.job_id,
                    "reason": dispute.reason,
                    "status": dispute.status,
                    "raised_by": dispute.raised_by.name,
                    "created_at": dispute.created_at,
                    "initial_complaint": dispute.initial_complaint[:100] + "..." if dispute.initial_complaint and len(dispute.initial_complaint) > 100 else dispute.initial_complaint
                })
        
        return unique_disputes
        
    except Exception as e:
        raise HTTPException(500, detail=str(e))

@router.get("/{dispute_id}")
async def get_dispute_details(
    dispute_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get details of a specific dispute (if user is involved)"""
    try:
        dispute_repo = DisputeRepository(db)
        dispute = dispute_repo.get_by_id(dispute_id)
        
        if not dispute:
            raise HTTPException(404, "Dispute not found")
        
        # Check if user is involved in this dispute
        job = dispute.job
        if not job:
            raise HTTPException(404, "Job not found for this dispute")
        
        user_is_involved = (
            current_user.id == dispute.raised_by_id or
            current_user.id == job.buyer_id or 
            current_user.id == job.service.seller_id
        )
        
        if not user_is_involved:
            raise HTTPException(403, "You don't have permission to view this dispute")
        
        return {
            "id": dispute.id,
            "job_id": dispute.job_id,
            "reason": dispute.reason,
            "status": dispute.status,
            "initial_complaint": dispute.initial_complaint,
            "respondent_response": dispute.respondent_response,
            "raised_by": {
                "id": dispute.raised_by.id,
                "name": dispute.raised_by.name
            },
            "job_details": {
                "buyer": job.buyer.name,
                "seller": job.service.seller.name,
                "price_agreed": float(job.price_agreed),
                "status": job.status
            },
            "created_at": dispute.created_at,
            "resolved_at": dispute.resolved_at,
            "final_decision": dispute.final_decision
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, detail=str(e))
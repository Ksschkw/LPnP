from fastapi import APIRouter, Depends, HTTPException
from app.dependencies import get_payment_service
from app.utilities.auth import get_current_user
from app.models.entities.user import User
from app.service.payment_service import PaymentService

router = APIRouter(prefix="/payments", tags=["payments"])

@router.get("/my-earnings")
async def get_my_earnings(
    current_user: User = Depends(get_current_user),
    payment_service: PaymentService = Depends(get_payment_service)
):
    """Get current user's earnings and balance"""
    return {
        "total_earnings": current_user.total_earnings,
        "available_balance": current_user.available_balance,
        "pending_balance": current_user.pending_balance
    }

@router.post("/jobs/{job_id}/refund")
async def refund_job_payment(
    job_id: str,
    refund_amount: float = None,
    current_user: User = Depends(get_current_user),
    payment_service: PaymentService = Depends(get_payment_service)
):
    """Refund a job payment (admin only or dispute resolution)"""
    try:
        payment = payment_service.process_refund(job_id, refund_amount)
        return {"message": f"Refund of ₦{refund_amount} processed successfully"}
    except ValueError as e:
        raise HTTPException(400, detail=str(e))
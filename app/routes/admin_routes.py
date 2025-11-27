# app/routes/admin_routes.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.dependencies import get_payment_service
from app.repository.Database.category_repo import CategoryRepository
from app.models.entities.serviceCategory import ServiceCategory
import logging
from dotenv import load_dotenv
import os
load_dotenv()

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/admin/categories", tags=["admin"])

# Move to .env later
ADMIN_KEY = os.getenv("ADMIN_KEY")

from app.repository.Database.user_repo import UserRepository
from app.models.entities.user import User
from app.models.Responses.user_responses import UserDetailResponse
from typing import List


def require_admin_key(admin_key: str = Query(..., description="Admin access key")):
    """Validate admin key — REQUIRED IN QUERY"""
    if admin_key != ADMIN_KEY:
        logger.warning(f"ADMIN ACCESS DENIED: Wrong key '{admin_key}'")
        raise HTTPException(status_code=403, detail="Invalid admin key")
    logger.info(f"ADMIN ACCESS GRANTED: Key accepted")
    return True

# === CATEGORY ENDPOINTS (VISIBLE IN SWAGGER) ===
@router.post("/categories")
def create_category(
    name: str,
    description: str = None,
    db: Session = Depends(get_db),
    key = Depends(require_admin_key)
):
    """ADMIN: Create a service category"""
    repo = CategoryRepository(db)
    if repo.get_by_name(name):
        logger.warning(f"Admin duplicate category attempt: {name}")
        raise HTTPException(400, "Category already exists")
    category = repo.create(name=name, description=description)
    logger.info(f"ADMIN: Created category '{name}' (ID: {category.id})")
    return {"id": category.id, "name": category.name}

@router.get("/categories", response_model=List[dict])
def list_categories(db: Session = Depends(get_db), key = Depends(require_admin_key)):
    """ADMIN: List all categories"""
    repo = CategoryRepository(db)
    cats = repo.get_all()
    logger.info(f"ADMIN: Listed {len(cats)} categories")
    return [{"id": c.id, "name": c.name} for c in cats]

# === FULL USER DATA ENDPOINT (VISIBLE, ALL FIELDS) ===
@router.get("/users", response_model=List[UserDetailResponse])
def get_all_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    key = Depends(require_admin_key)
):
    """
    ADMIN ONLY: Get ALL user data
    - Requires admin_key in query
    - Returns EVERY field
    """
    logger.info(f"ADMIN: Fetching ALL user data (skip={skip}, limit={limit})")
    repo = UserRepository(db)
    users = repo.get_all(skip=skip, limit=limit)
    
    if not users:
        logger.info("ADMIN: No users found")
        return []
    
    logger.info(f"ADMIN: Returned FULL data for {len(users)} users")
    return [UserDetailResponse.model_validate(user) for user in users]

# Add to your existing admin_routes.py

from app.service.payment_service import PaymentService
from app.service.dispute_service import DisputeService
from app.repository.Database.payment_repo import PaymentRepository
from app.repository.Database.dispute_repo import DisputeRepository
from typing import List, Optional
from decimal import Decimal

# === PAYMENT MANAGEMENT ===
@router.get("/payments")
def get_all_payments(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    key = Depends(require_admin_key)
):
    """ADMIN: View all payments in the system"""
    repo = PaymentRepository(db)
    payments = repo.get_all(skip=skip, limit=limit)
    
    return [{
        "id": p.id,
        "job_id": p.job_id,
        "amount": p.amount,
        "platform_fee": p.platform_fee,
        "seller_earnings": p.seller_earnings,
        "status": p.status,
        "is_platform_revenue": p.is_platform_revenue,
        "created_at": p.created_at
    } for p in payments]

@router.get("/platform-earnings")
def get_platform_earnings(
    payment_service: PaymentService = Depends(get_payment_service),
    key = Depends(require_admin_key)
):
    """ADMIN: Get total platform earnings (YOUR MONEY 💰)"""
    total_earnings = payment_service.get_platform_earnings()
    
    return {
        "total_platform_earnings": total_earnings,
        "message": f"Platform has earned ₦{total_earnings} total"
    }

@router.post("/payments/{payment_id}/refund")
def admin_refund_payment(
    payment_id: str,
    refund_amount: Optional[float] = None,
    reason: str = "admin_decision",
    db: Session = Depends(get_db),
    key = Depends(require_admin_key)
):
    """ADMIN: Force refund a payment (GOD MODE)"""
    payment_service = PaymentService(db)
    
    try:
        payment = payment_service.process_refund(payment_id, refund_amount)
        return {
            "message": f"Refund of ₦{refund_amount} processed successfully",
            "payment_id": payment.id,
            "reason": reason
        }
    except ValueError as e:
        raise HTTPException(400, detail=str(e))

# === DISPUTE MANAGEMENT ===
@router.get("/disputes")
def get_all_disputes(
    status: Optional[str] = None,  # Filter by status: open, in_progress, resolved
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    key = Depends(require_admin_key)
):
    """ADMIN: View all disputes in the system"""
    repo = DisputeRepository(db)
    
    if status:
        disputes = repo.get_by_status(status, skip, limit)
    else:
        disputes = repo.get_all(skip, limit)
    
    return [{
        "id": d.id,
        "job_id": d.job_id,
        "raised_by": d.raised_by.name,
        "reason": d.reason,
        "status": d.status,
        "created_at": d.created_at,
        "initial_complaint": d.initial_complaint
    } for d in disputes]

@router.get("/disputes/{dispute_id}")
def get_dispute_details(
    dispute_id: str,
    db: Session = Depends(get_db),
    key = Depends(require_admin_key)
):
    """ADMIN: Get full details of a specific dispute"""
    repo = DisputeRepository(db)
    dispute = repo.get_by_id(dispute_id)
    
    if not dispute:
        raise HTTPException(404, "Dispute not found")
    
    return {
        "id": dispute.id,
        "job_id": dispute.job_id,
        "raised_by": {
            "id": dispute.raised_by.id,
            "name": dispute.raised_by.name,
            "phone": dispute.raised_by.phone
        },
        "reason": dispute.reason,
        "status": dispute.status,
        "initial_complaint": dispute.initial_complaint,
        "respondent_response": dispute.respondent_response,
        "admin_notes": dispute.admin_notes,
        "created_at": dispute.created_at,
        "job_details": {
            "buyer": dispute.job.buyer.name,
            "seller": dispute.job.service.seller.name,
            "price_agreed": dispute.job.price_agreed,
            "status": dispute.job.status
        }
    }

@router.post("/disputes/{dispute_id}/resolve")
def resolve_dispute(
    dispute_id: str,
    resolution: str = Query(..., description="Resolution type: full_refund_buyer, partial_refund_buyer, pay_seller_full, dismiss"),
    refund_amount: Optional[float] = None,
    admin_notes: Optional[str] = None,
    db: Session = Depends(get_db),
    key = Depends(require_admin_key)
):
    """ADMIN: Resolve a dispute with final decision (Secret Key Only)"""
    dispute_service = DisputeService(db)
    
    # Validate resolution type
    valid_resolutions = ['full_refund_buyer', 'partial_refund_buyer', 'pay_seller_full', 'dismiss']
    if resolution not in valid_resolutions:
        raise HTTPException(400, f"Invalid resolution. Must be one of: {valid_resolutions}")
    
    # Validate refund amount for partial refund
    if resolution == "partial_refund_buyer" and refund_amount is None:
        raise HTTPException(400, "Refund amount is required for partial refund")
    
    try:
        result = dispute_service.resolve_dispute(
            dispute_id=dispute_id,
            resolution=resolution,
            refund_amount=refund_amount,
            admin_notes=admin_notes,
            resolved_by_admin="System Administrator",  # Use this instead of user ID
            admin_action_type="manual"
        )
        
        return {
            "message": f"Dispute resolved: {resolution}",
            "dispute_id": dispute_id,
            "refund_amount": refund_amount,
            "final_decision": resolution,
            "resolved_by": "System Administrator",
            "trust_adjustments": result.get("trust_adjustments", {})
        }
    except ValueError as e:
        raise HTTPException(400, detail=str(e))

@router.post("/disputes/{dispute_id}/escalate")
def escalate_dispute(
    dispute_id: str,
    admin_notes: str,
    db: Session = Depends(get_db),
    key = Depends(require_admin_key)
):
    """ADMIN: Escalate dispute to final stage"""
    dispute_service = DisputeService(db)
    
    try:
        dispute = dispute_service.escalate_dispute(dispute_id, admin_notes)
        return {"message": "Dispute escalated to final stage", "dispute_id": dispute_id}
    except ValueError as e:
        raise HTTPException(400, detail=str(e))

# === USER FINANCIAL CONTROLS ===
@router.get("/users/{user_id}/financials")
def get_user_financials(
    user_id: str,
    db: Session = Depends(get_db),
    key = Depends(require_admin_key)
):
    """ADMIN: View user's complete financial data"""
    user_repo = UserRepository(db)
    user = user_repo.get_by_id(user_id)
    
    if not user:
        raise HTTPException(404, "User not found")
    
    return {
        "user_id": user.id,
        "name": user.name,
        "total_earnings": user.total_earnings,
        "available_balance": user.available_balance,
        "pending_balance": user.pending_balance,
        "trust_score": user.trust_score,
        "completion_count": user.completion_count
    }

@router.post("/users/{user_id}/adjust-balance")
def adjust_user_balance(
    user_id: str,
    amount: float,
    action: str,  # "add", "subtract"
    reason: str,
    db: Session = Depends(get_db),
    key = Depends(require_admin_key)
):
    """ADMIN: Manually adjust user's balance (GOD MODE - Use carefully!)"""
    user_repo = UserRepository(db)
    user = user_repo.get_by_id(user_id)
    
    if not user:
        raise HTTPException(404, "User not found")
    
    new_balance = user.available_balance + amount if action == "add" else user.available_balance - amount
    
    if new_balance < 0:
        raise HTTPException(400, "Balance cannot be negative")
    
    user_repo.update(user_id, {"available_balance": new_balance})
    
    logger.warning(f"ADMIN MANUAL BALANCE ADJUSTMENT: User {user_id} {action} ₦{amount}. Reason: {reason}")
    
    return {
        "message": f"Balance adjusted: {action} ₦{amount}",
        "new_balance": new_balance,
        "reason": reason
    }
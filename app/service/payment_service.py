import uuid
from app.repository.Database.payment_repo import PaymentRepository
from app.repository.Database.job_repo import JobRepository
from app.repository.Database.user_repo import UserRepository
from app.models.entities.payment import Payment
import logging
from decimal import Decimal

logger = logging.getLogger(__name__)

class PaymentService:
    def __init__(self, db):
        self.payment_repo = PaymentRepository(db)
        self.job_repo = JobRepository(db)
        self.user_repo = UserRepository(db)
        self.platform_fee_percent = Decimal('0.10')  # 10% commission
    
    def create_payment_for_job(self, job_id: str) -> Payment:
        """Create payment record when job is accepted"""
        job = self.job_repo.get_by_id(job_id)
        if not job:
            raise ValueError("Job not found")
        
        total_amount = job.price_agreed
        platform_fee = total_amount * self.platform_fee_percent
        seller_earnings = total_amount - platform_fee
        
        # Create payment record
        payment_data = {
            'job_id': job_id,
            'amount': total_amount,
            'platform_fee': platform_fee,
            'seller_earnings': seller_earnings,
            'status': 'held_in_escrow',
            'gateway_reference': f"mock_py_{job_id}_{uuid.uuid4().hex[:8]}"
        }
        
        payment = self.payment_repo.create(payment_data)
        
        # Update seller's pending balance
        seller = self.user_repo.get_by_id(job.service.seller_id)
        if seller:
            new_pending = seller.pending_balance + total_amount
            self.user_repo.update(seller.id, {"pending_balance": new_pending})
        
        logger.info(f"Payment created for job {job_id}: ₦{total_amount} (Fee: ₦{platform_fee})")
        return payment
    
    def release_payment_to_seller(self, job_id: str) -> Payment:
        """Release escrow funds to seller when job is completed"""
        payment = self.payment_repo.get_by_job_id(job_id)
        if not payment:
            raise ValueError("Payment not found")
        
        if payment.status != 'held_in_escrow':
            raise ValueError("Payment not in escrow")
        
        job = self.job_repo.get_by_id(job_id)
        seller = self.user_repo.get_by_id(job.service.seller_id)
        
        # Move from pending to available balance
        new_pending = seller.pending_balance - payment.amount
        new_available = seller.available_balance + payment.seller_earnings
        new_total = seller.total_earnings + payment.seller_earnings
        
        # Update seller balances
        self.user_repo.update(seller.id, {
            "pending_balance": new_pending,
            "available_balance": new_available,
            "total_earnings": new_total
        })
        
        # Record platform revenue
        platform_payment = {
            'job_id': job_id,
            'amount': payment.platform_fee,
            'platform_fee': Decimal('0'),
            'seller_earnings': Decimal('0'),
            'status': 'released',
            'is_platform_revenue': True,
            'revenue_type': 'service_fee'
        }
        self.payment_repo.create(platform_payment)
        
        # Update platform total earnings (admin user)
        self._update_platform_earnings(payment.platform_fee)
        
        # Mark original payment as released
        from sqlalchemy import func
        payment = self.payment_repo.update(payment.id, {
            "status": "released",
            "released_at": func.now()
        })
        
        logger.info(f"Payment released for job {job_id}: Seller earned ₦{payment.seller_earnings}, Platform earned ₦{payment.platform_fee}")
        return payment
    
    def process_refund(self, job_id: str, refund_amount: Decimal = None) -> Payment:
        """Refund payment (full or partial)"""
        payment = self.payment_repo.get_by_job_id(job_id)
        if not payment:
            raise ValueError("Payment not found")
        
        job = self.job_repo.get_by_id(job_id)
        
        # Default to full refund
        if refund_amount is None:
            refund_amount = payment.amount
        
        # Update seller's pending balance
        seller = self.user_repo.get_by_id(job.service.seller_id)
        if seller:
            new_pending = seller.pending_balance - refund_amount
            self.user_repo.update(seller.id, {"pending_balance": new_pending})
        
        # Update payment status
        payment = self.payment_repo.update(payment.id, {
            "status": "refunded"
        })
        
        logger.info(f"Refund processed for job {job_id}: ₦{refund_amount}")
        return payment
    
    def _update_platform_earnings(self, amount: Decimal):
        """Update platform total earnings (you can track this in admin user)"""
        # In a real system, you might have a separate platform account
        # For now, we'll track it in a special way or just log it
        logger.info(f"Platform revenue increased by: ₦{amount}")
    
    def get_platform_earnings(self) -> Decimal:
        """Get total platform earnings from all service fees"""
        return self.payment_repo.get_total_platform_earnings()
from decimal import Decimal
from sqlalchemy.orm import Session, joinedload
from app.models.entities.payment import Payment
from sqlalchemy import func
import uuid

class PaymentRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, payment_data: dict) -> Payment:
        """Create a new payment record"""
        payment = Payment(
            id=str(uuid.uuid4()),
            job_id=payment_data['job_id'],
            amount=payment_data['amount'],
            platform_fee=payment_data['platform_fee'],
            seller_earnings=payment_data['seller_earnings'],
            status=payment_data.get('status', 'pending'),
            gateway_reference=payment_data.get('gateway_reference'),
            is_platform_revenue=payment_data.get('is_platform_revenue', False),
            revenue_type=payment_data.get('revenue_type')
        )
        
        self.db.add(payment)
        self.db.commit()
        self.db.refresh(payment)
        return payment
    
    def get_by_job_id(self, job_id: str) -> Payment:
        """Get payment for a specific job"""
        return self.db.query(Payment).filter(Payment.job_id == job_id).first()
    
    def get_by_id(self, payment_id: str) -> Payment:
        """Get payment by ID"""
        return self.db.query(Payment).filter(Payment.id == payment_id).first()
    
    def update(self, payment_id: str, update_data: dict) -> Payment:
        """Update payment information"""
        payment = self.get_by_id(payment_id)
        if payment:
            for field, value in update_data.items():
                if hasattr(payment, field) and value is not None:
                    setattr(payment, field, value)
            self.db.commit()
            self.db.refresh(payment)
        return payment
    
    def get_total_platform_earnings(self) -> Decimal:
        """Calculate total platform revenue"""
        result = self.db.query(func.sum(Payment.amount)).filter(
            Payment.is_platform_revenue == True,
            Payment.status == 'released'
        ).scalar()
        return result or Decimal('0')
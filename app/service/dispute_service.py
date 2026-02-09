from app.repository.Database.dispute_repo import DisputeRepository
from app.repository.Database.job_repo import JobRepository
from app.repository.Database.user_repo import UserRepository
from app.service.payment_service import PaymentService
from app.service.badge_service import BadgeService
from app.models.entities.dispute import Dispute
import logging
from decimal import Decimal
from typing import Dict, Any

logger = logging.getLogger(__name__)

class DisputeService:
    def __init__(self, db):
        self.dispute_repo = DisputeRepository(db)
        self.job_repo = JobRepository(db)
        self.user_repo = UserRepository(db)
        self.payment_service = PaymentService(db)
        self.badge_service = BadgeService(db)
    
    # def create_dispute(self, dispute_data: dict) -> Dispute:
    def create_dispute(self, dispute_data: dict) -> Dispute:
        """Create a new dispute with validation - SECURE VERSION"""
        job_id = dispute_data['job_id']
        raised_by_id = dispute_data['raised_by_id']
        
        # Validate job exists
        job = self.job_repo.get_by_id(job_id)
        if not job:
            raise ValueError("Job not found")
        
        # Validate user is part of the job
        if raised_by_id not in [job.buyer_id, job.service.seller_id]:
            raise ValueError("You can only raise disputes for jobs you're involved in")
        
        # 🚨 CRITICAL FIX: Check if payment is already released
        payment = self.payment_repo.get_by_job_id(job_id)
        if payment and payment.status == 'released':
            raise ValueError("Cannot dispute job after payment has been released to seller")
        
        # Check if dispute already exists for this job
        existing_disputes = self.dispute_repo.get_by_job_id(job_id)
        if any(d.status in ['open', 'in_progress'] for d in existing_disputes):
            raise ValueError("There is already an active dispute for this job")
        
        # 🚨 CRITICAL FIX: Only allow disputes BEFORE completion confirmation
        if job.status not in ['accepted', 'in_progress', 'pending_completion']:
            raise ValueError("You can only dispute jobs that are in progress or awaiting completion confirmation")
        
        # Create the dispute
        dispute = self.dispute_repo.create(dispute_data)
        logger.info(f"Dispute created: {dispute.id} for job {job_id} by user {raised_by_id}")
        
        # 🚨 AUTO-PAUSE PAYMENT RELEASE if dispute created during pending_completion
        if job.status == 'pending_completion':
            self.job_repo.update_status(job_id, 'disputed')
            logger.info(f"Job {job_id} paused due to dispute")
        
        return dispute
    
    def add_respondent_response(self, dispute_id: str, respondent_id: str, response: str) -> Dispute:
        """Add response from the other party in the dispute"""
        dispute = self.dispute_repo.get_by_id(dispute_id)
        if not dispute:
            raise ValueError("Dispute not found")
        
        # Validate respondent is the other party in the job
        job = dispute.job
        other_party_id = job.buyer_id if respondent_id == job.service.seller_id else job.service.seller_id
        
        if respondent_id not in [job.buyer_id, job.service.seller_id]:
            raise ValueError("You can only respond to disputes you're involved in")
        
        if respondent_id == dispute.raised_by_id:
            raise ValueError("You cannot respond to your own dispute")
        
        dispute = self.dispute_repo.add_respondent_response(dispute_id, response)
        logger.info(f"Response added to dispute {dispute_id} by user {respondent_id}")
        
        return dispute
    
    def escalate_dispute(self, dispute_id: str, admin_notes: str = None) -> Dispute:
        """Escalate dispute to admin for resolution"""
        dispute = self.dispute_repo.get_by_id(dispute_id)
        if not dispute:
            raise ValueError("Dispute not found")
        
        if dispute.status == 'resolved':
            raise ValueError("This dispute is already resolved")
        
        dispute = self.dispute_repo.escalate_to_admin(dispute_id)
        
        if admin_notes:
            dispute = self.dispute_repo.update(dispute_id, {"admin_notes": admin_notes})
        
        logger.info(f"Dispute {dispute_id} escalated to admin")
        return dispute
    
    def resolve_dispute(self, dispute_id: str, resolution: str, refund_amount: float = None, 
                   admin_notes: str = None, resolved_by_admin: str = None, 
                   admin_action_type: str = "manual") -> Dict[str, any]:
        """Resolve a dispute with appropriate actions - UPDATED for secret key admin"""
        dispute = self.dispute_repo.get_by_id(dispute_id)
        if not dispute:
            raise ValueError("Dispute not found")
        
        if dispute.status == 'resolved':
            raise ValueError("This dispute is already resolved")
        
        job = dispute.job
        if not job:
            raise ValueError("Job not found for this dispute")
        
        buyer_id = job.buyer_id
        seller_id = job.service.seller_id
        
        resolution_data = {
            'final_decision': resolution,
            'refund_amount': refund_amount,
            'resolution_notes': admin_notes,
            'resolved_by_admin': resolved_by_admin,
            'admin_action_type': admin_action_type
            # Note: resolved_by_id is NOT set - keeping it NULL
        }
        
        # Handle different resolution types (same logic as before)
        if resolution == "full_refund_buyer":
            winner_id = buyer_id
            loser_id = seller_id
            refund_amount = job.price_agreed
            self.payment_service.process_refund(job.id, float(refund_amount))
            resolution_data['refund_amount'] = float(refund_amount)
            
        elif resolution == "partial_refund_buyer":
            winner_id = buyer_id  
            loser_id = seller_id
            if refund_amount is None or refund_amount <= 0:
                raise ValueError("Valid refund amount required for partial refund")
            self.payment_service.process_refund(job.id, float(refund_amount))
            resolution_data['refund_amount'] = float(refund_amount)
            
        elif resolution == "pay_seller_full":
            winner_id = seller_id
            loser_id = buyer_id
            if job.status == 'completed':
                self.payment_service.release_payment_to_seller(job.id)
            resolution_data['refund_amount'] = None
            
        elif resolution == "dismiss":
            winner_id = None
            loser_id = None
            resolution_data['refund_amount'] = None
            
        else:
            raise ValueError(f"Unknown resolution type: {resolution}")
        
        # Apply trust score adjustments (same logic)
        loser_trust_deduction = 0
        if loser_id:
            loser_trust_deduction = 20
            loser = self.user_repo.get_by_id(loser_id)
            if loser:
                new_trust = max(0, loser.trust_score - loser_trust_deduction)
                self.user_repo.update(loser_id, {"trust_score": new_trust})
                self.badge_service.update_user_badge(loser_id)
        
        if winner_id:
            winner = self.user_repo.get_by_id(winner_id)
            if winner:
                new_trust = winner.trust_score + 10
                self.user_repo.update(winner_id, {"trust_score": new_trust})
                self.badge_service.update_user_badge(winner_id)
        
        # Update resolution data
        resolution_data.update({
            'winner_id': winner_id,
            'loser_trust_deduction': loser_trust_deduction
        })
        
        # Mark dispute as resolved (this now uses resolved_by_admin instead of resolved_by_id)
        dispute = self.dispute_repo.resolve_dispute(dispute_id, resolution_data)
        
        # Update job status if needed
        if resolution in ["full_refund_buyer", "partial_refund_buyer"]:
            self.job_repo.update_status(job.id, "cancelled")
        
        logger.info(f"Dispute {dispute_id} resolved by {resolved_by_admin}: {resolution}")
        
        return {
            "dispute": dispute,
            "resolution": resolution,
            "refund_processed": resolution_data.get('refund_amount'),
            "resolved_by": resolved_by_admin,
            "trust_adjustments": {
                "winner_bonus": 10 if winner_id else 0,
                "loser_penalty": loser_trust_deduction
            }
        }
    
    def get_dispute_stats(self) -> Dict[str, Any]:
        """Get dispute statistics for admin dashboard"""
        total_disputes = self.dispute_repo.get_all()
        open_disputes = [d for d in total_disputes if d.status in ['open', 'in_progress']]
        resolved_disputes = [d for d in total_disputes if d.status == 'resolved']
        
        resolution_types = {}
        for dispute in resolved_disputes:
            resolution_types[dispute.final_decision] = resolution_types.get(dispute.final_decision, 0) + 1
        
        return {
            "total_disputes": len(total_disputes),
            "open_disputes": len(open_disputes),
            "resolved_disputes": len(resolved_disputes),
            "resolution_breakdown": resolution_types,
            "resolution_rate": len(resolved_disputes) / len(total_disputes) if total_disputes else 0
        }
    
    def auto_escalate_old_disputes(self, days_threshold: int = 3):
        """Automatically escalate disputes that have been open too long"""
        from datetime import datetime, timedelta
        from sqlalchemy import func
        
        threshold_date = datetime.utcnow() - timedelta(days=days_threshold)
        
        old_disputes = (self.db.query(Dispute)
                       .filter(
                           Dispute.status.in_(['open', 'in_progress']),
                           Dispute.created_at < threshold_date
                       )
                       .all())
        
        for dispute in old_disputes:
            self.escalate_dispute(dispute.id, "Auto-escalated: No response within time limit")
            logger.info(f"Auto-escalated dispute {dispute.id} due to age")
        
        return len(old_disputes)
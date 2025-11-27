from sqlalchemy.orm import Session, joinedload
from app.models.entities.dispute import Dispute
from app.models.entities.job import Job
from app.models.entities.service import Service
from app.models.entities.user import User
import uuid
from typing import List, Optional

class DisputeRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, dispute_data: dict) -> Dispute:
        """Create a new dispute"""
        dispute = Dispute(
            id=str(uuid.uuid4()),
            job_id=dispute_data['job_id'],
            raised_by_id=dispute_data['raised_by_id'],
            reason=dispute_data['reason'],
            initial_complaint=dispute_data['initial_complaint'],
            status='open'
        )
        
        self.db.add(dispute)
        self.db.commit()
        self.db.refresh(dispute)
        return self.get_by_id(dispute.id)
    
    def get_by_id(self, dispute_id: str) -> Dispute:
        """Get dispute with all relationships"""
        return (self.db.query(Dispute)
                .options(
                    joinedload(Dispute.raised_by),
                    joinedload(Dispute.resolved_by),
                    joinedload(Dispute.winner),
                    joinedload(Dispute.job).joinedload(Job.buyer),
                    joinedload(Dispute.job).joinedload(Job.service).joinedload(Service.seller)
                )
                .filter(Dispute.id == dispute_id)
                .first())
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[Dispute]:
        """Get all disputes"""
        return (self.db.query(Dispute)
                .options(
                    joinedload(Dispute.raised_by),
                    joinedload(Dispute.job)
                )
                .offset(skip)
                .limit(limit)
                .all())
    
    def get_by_status(self, status: str, skip: int = 0, limit: int = 100) -> List[Dispute]:
        """Get disputes by status"""
        return (self.db.query(Dispute)
                .options(
                    joinedload(Dispute.raised_by),
                    joinedload(Dispute.job)
                )
                .filter(Dispute.status == status)
                .offset(skip)
                .limit(limit)
                .all())
    
    def get_by_job_id(self, job_id: str) -> List[Dispute]:
        """Get all disputes for a job"""
        return (self.db.query(Dispute)
                .options(joinedload(Dispute.raised_by))
                .filter(Dispute.job_id == job_id)
                .all())
    
    def get_by_user(self, user_id: str) -> List[Dispute]:
        """Get all disputes raised by a user"""
        return (self.db.query(Dispute)
                .options(joinedload(Dispute.job))
                .filter(Dispute.raised_by_id == user_id)
                .all())
    
    def update(self, dispute_id: str, update_data: dict) -> Dispute:
        """Update dispute information"""
        dispute = self.get_by_id(dispute_id)
        if dispute:
            for field, value in update_data.items():
                if hasattr(dispute, field) and value is not None:
                    setattr(dispute, field, value)
            self.db.commit()
            self.db.refresh(dispute)
        return dispute
    
    def add_respondent_response(self, dispute_id: str, response: str) -> Dispute:
        """Add response from the other party"""
        return self.update(dispute_id, {
            "respondent_response": response,
            "status": "in_progress"
        })
    
    def escalate_to_admin(self, dispute_id: str) -> Dispute:
        """Escalate dispute to admin attention"""
        from sqlalchemy import func
        return self.update(dispute_id, {
            "resolution_stage": "escalated",
            "escalated_at": func.now(),
            "status": "in_progress"
        })
    
    def resolve_dispute(self, dispute_id: str, resolution_data: dict) -> Dispute:
        """Mark dispute as resolved - FIXED for secret key admin"""
        from sqlalchemy import func
        
        # Prepare update data
        update_data = {
            "status": "resolved",
            "resolved_at": func.now(),
            "final_decision": resolution_data.get('final_decision'),
            "refund_amount": resolution_data.get('refund_amount'),
            "resolution_notes": resolution_data.get('resolution_notes'),
            "winner_id": resolution_data.get('winner_id'),
            "loser_trust_deduction": resolution_data.get('loser_trust_deduction', 0),
            "resolved_by_admin": resolution_data.get('resolved_by_admin', 'System Admin'),  # Use this instead of user ID
            "admin_action_type": resolution_data.get('admin_action_type', 'manual')
        }
        
        # Only set resolved_by_id if provided (keep it NULL for secret key admin)
        if resolution_data.get('resolved_by_id'):
            update_data["resolved_by_id"] = resolution_data.get('resolved_by_id')
        
        return self.update(dispute_id, update_data)
    
    def dismiss_dispute(self, dispute_id: str, admin_notes: str) -> Dispute:
        """Dismiss a dispute without action"""
        from sqlalchemy import func
        return self.update(dispute_id, {
            "status": "dismissed",
            "resolved_at": func.now(),
            "admin_notes": admin_notes,
            "final_decision": "dismissed"
        })
    
    def get_open_disputes_count(self) -> int:
        """Count how many disputes are currently open"""
        return self.db.query(Dispute).filter(Dispute.status.in_(['open', 'in_progress'])).count()
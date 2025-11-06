from sqlalchemy.orm import Session, joinedload
from app.models.entities.vouch import Vouch
from app.models.entities.service import Service
import uuid

class VouchRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, service_id: str, vouch_data: dict) -> Vouch:
        """Create a new vouch"""
        vouch = Vouch(
            id=str(uuid.uuid4()),
            service_id=service_id,
            voucher_user_id=vouch_data.get('voucher_user_id'),
            voucher_phone=vouch_data['voucher_phone'],
            vouch_type=vouch_data['vouch_type'],
            points_given=vouch_data['points_given'],
            comment=vouch_data.get('comment')
        )
        
        self.db.add(vouch)
        self.db.commit()
        self.db.refresh(vouch)
        return self.get_by_id(vouch.id)
    
    def get_by_id(self, vouch_id: str) -> Vouch:
        """Get vouch with relationships"""
        return (self.db.query(Vouch)
                .options(joinedload(Vouch.service), joinedload(Vouch.voucher_user))
                .filter(Vouch.id == vouch_id)
                .first())
    
    def get_by_service(self, service_id: str) -> list[Vouch]:
        """Get all vouches for a service"""
        return (self.db.query(Vouch)
                .options(joinedload(Vouch.voucher_user))
                .filter(Vouch.service_id == service_id)
                .all())
    
    def get_user_vouches_for_service(self, service_id: str, user_id: str) -> list[Vouch]:
        """Check if user already vouched for this service"""
        return (self.db.query(Vouch)
                .filter(
                    Vouch.service_id == service_id,
                    Vouch.voucher_user_id == user_id
                )
                .all())
    
    def get_phone_vouches_for_service(self, service_id: str, phone_number: str) -> list[Vouch]:
        """✅ CRITICAL: Check if phone number already vouched for this service"""
        return (self.db.query(Vouch)
                .filter(
                    Vouch.service_id == service_id,
                    Vouch.voucher_phone == phone_number
                )
                .all())
    
    def get_service_vouch_count(self, service_id: str) -> int:
        """Get total vouch points for a service"""
        result = self.db.query(Vouch).filter(
            Vouch.service_id == service_id,
            Vouch.is_retracted == False
        ).count()
        return result
from app.repository.Database.vouch_repo import VouchRepository
from app.repository.Database.service_repo import ServiceRepository
from app.models.Requests.vouch_requests import VouchCreateRequest
from app.models.Responses.vouch_responses import VouchResponse
import logging

logger = logging.getLogger(__name__)

class VouchService:
    def __init__(self, db):
        self.vouch_repo = VouchRepository(db)
        self.service_repo = ServiceRepository(db)
    
    def create_vouch(self, service_id: str, vouch_data: VouchCreateRequest, user_id: str = None, user_phone: str = None) -> VouchResponse:
        """Create a vouch with automatic type detection and duplicate prevention"""
        # Verify service exists
        service = self.service_repo.get_by_id(service_id)
        if not service:
            raise ValueError("Service not found")
        
        # Determine vouch type and required fields
        if user_id:
            # LOGGED-IN USER: Trusted vouch (50 points)
            points = 50
            vouch_type = "trusted"
            voucher_phone = user_phone
            
            if not user_phone:
                raise ValueError("User phone required for logged-in vouches")
            
            # Check if user already vouched for this service
            existing_user_vouches = self.vouch_repo.get_user_vouches_for_service(service_id, user_id)
            if existing_user_vouches:
                raise ValueError("You have already vouched for this service")
                
        else:
            # NON-LOGGED-IN USER: Quick vouch (10 points)
            points = 10
            vouch_type = "quick"
            
            # For non-logged-in users, phone is required
            if not vouch_data.voucher_phone:
                raise ValueError("Phone number is required for quick vouches")
            
            voucher_phone = vouch_data.voucher_phone
            
            # ✅ CRITICAL FIX: Check if this phone number already vouched for this service
            existing_phone_vouches = self.vouch_repo.get_phone_vouches_for_service(service_id, voucher_phone)
            if existing_phone_vouches:
                raise ValueError("This phone number has already vouched for this service")
        
        # Create vouch data
        vouch_dict = {
            'voucher_user_id': user_id,
            'voucher_phone': voucher_phone,
            'vouch_type': vouch_type,
            'points_given': points,
            'comment': vouch_data.comment
        }
        
        # Create the vouch
        vouch = self.vouch_repo.create(service_id, vouch_dict)
        
        # Update service trust points
        self.service_repo.add_trust_points(service_id, points)
        
        # Check if service should be auto-activated
        updated_service = self.service_repo.get_by_id(service_id)
        if updated_service.trust_points >= 100 and updated_service.status == "draft":
            self.service_repo.activate_service(service_id)
            logger.info(f"Service {service_id} auto-activated with {updated_service.trust_points} trust points")
        
        logger.info(f"Vouch created: {points} points ({vouch_type}) for service {service_id} by phone {voucher_phone}")
        return VouchResponse.model_validate(vouch)
    
    def get_service_vouches(self, service_id: str) -> list[VouchResponse]:
        """Get all vouches for a service"""
        vouches = self.vouch_repo.get_by_service(service_id)
        return [VouchResponse.model_validate(vouch) for vouch in vouches]
    
    def get_service_trust_score(self, service_id: str) -> dict:
        """Get service trust score breakdown"""
        service = self.service_repo.get_by_id(service_id)
        if not service:
            raise ValueError("Service not found")
        
        vouches = self.vouch_repo.get_by_service(service_id)
        
        trusted_vouches = [v for v in vouches if v.vouch_type == "trusted"]
        quick_vouches = [v for v in vouches if v.vouch_type == "quick"]
        
        return {
            "total_points": service.trust_points,
            "trusted_vouches": len(trusted_vouches),
            "quick_vouches": len(quick_vouches),
            "total_vouches": len(vouches),
            "status": service.status,
            "needed_for_activation": max(0, 100 - service.trust_points)
        }
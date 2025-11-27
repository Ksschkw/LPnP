from app.repository.Database.user_repo import UserRepository
import logging

logger = logging.getLogger(__name__)

class BadgeService:
    def __init__(self, db):
        self.user_repo = UserRepository(db)
    
    def calculate_badge_level(self, user) -> str:
        """Calculate user's badge level based on criteria"""
        trust_score = user.trust_score
        nin_verified = user.nin_verified
        completion_count = user.completion_count
        has_paid_badge = user.has_paid_badge
        
        # BADGE LOGIC
        if trust_score >= 1000 and nin_verified and completion_count >= 50:
            return "legend"
        elif nin_verified and trust_score >= 100 and has_paid_badge:
            return "elite" 
        elif nin_verified and trust_score >= 100:
            return "verified"
        elif trust_score >= 100:
            return "trusted"
        else:
            return "newbie"
    
    def update_user_badge(self, user_id: str) -> str:
        """Recalculate and update user's badge level"""
        user = self.user_repo.get_by_id(user_id)
        if not user:
            return None
        
        new_badge = self.calculate_badge_level(user)
        
        # Only update if badge changed
        if user.badge_level != new_badge:
            self.user_repo.update(user_id, {"badge_level": new_badge})
            logger.info(f"User {user_id} badge updated: {user.badge_level} -> {new_badge}")
        
        return new_badge
    
    def purchase_elite_badge(self, user_id: str) -> bool:
        """User pays for Elite badge upgrade"""
        user = self.user_repo.get_by_id(user_id)
        if not user:
            return False
        
        # Requirements for Elite badge
        if user.nin_verified and user.trust_score >= 100:
            from sqlalchemy import func
            update_data = {
                "has_paid_badge": True,
                "badge_purchased_at": func.now()
            }
            self.user_repo.update(user_id, update_data)
            
            # Recalculate badge
            self.update_user_badge(user_id)
            logger.info(f"User {user_id} purchased Elite badge")
            return True
        
        return False
from sqlalchemy.orm import Session, joinedload
from app.models.entities.review import Review
import uuid

class ReviewRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, review_data: dict) -> Review:
        """Create a new review"""
        review = Review(
            id=str(uuid.uuid4()),
            job_id=review_data['job_id'],
            reviewer_id=review_data['reviewer_id'],
            reviewee_id=review_data['reviewee_id'],
            review_type=review_data['review_type'],
            rating=review_data['rating'],
            comment=review_data.get('comment')
        )
        
        self.db.add(review)
        self.db.commit()
        self.db.refresh(review)
        return self.get_by_id(review.id)
    
    def get_by_id(self, review_id: str) -> Review:
        """Get review with relationships"""
        return (self.db.query(Review)
                .options(joinedload(Review.reviewer), joinedload(Review.reviewee))
                .filter(Review.id == review_id)
                .first())
    
    def get_by_user(self, user_id: str) -> list[Review]:
        """Get all reviews for a user"""
        return (self.db.query(Review)
                .options(joinedload(Review.reviewer))
                .filter(Review.reviewee_id == user_id)
                .all())
    
    def get_user_rating(self, user_id: str) -> float:
        """Get average rating for a user"""
        from sqlalchemy import func
        result = self.db.query(func.avg(Review.rating)).filter(
            Review.reviewee_id == user_id,
            Review.is_visible == True
        ).scalar()
        return float(result) if result else 0.0
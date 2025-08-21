"""Experience service for handling work experience operations."""
from sqlalchemy.orm import Session
from app.models.experience import Experience
from app.exceptions import ContentNotFoundError
from typing import List
import logging

logger = logging.getLogger(__name__)


class ExperienceService:
    """Service for managing work experience."""
    
    def get_experiences(self, db: Session) -> List[Experience]:
        """Get all experiences ordered by display order and start date (most recent first)."""
        return db.query(Experience).order_by(
            Experience.display_order, 
            Experience.start_date.desc()
        ).all()

    def get_experience_by_id(self, db: Session, experience_id: int) -> Experience:
        """Get experience by ID."""
        experience = db.query(Experience).filter(Experience.id == experience_id).first()
        if not experience:
            raise ContentNotFoundError("experience", experience_id)
        return experience


# Global service instance
experience_service = ExperienceService()
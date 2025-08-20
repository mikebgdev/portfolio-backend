"""Education service for handling education operations."""
from sqlalchemy.orm import Session
from app.models.education import Education
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


class EducationService:
    """Service for managing education records."""
    
    def get_education_records(self, db: Session) -> List[Education]:
        """Get all education records ordered by display order and start date (most recent first)."""
        return db.query(Education).order_by(
            Education.display_order, 
            Education.start_date.desc()
        ).all()

    def get_education_by_id(self, db: Session, education_id: int) -> Optional[Education]:
        """Get education record by ID."""
        return db.query(Education).filter(Education.id == education_id).first()


# Global service instance
education_service = EducationService()
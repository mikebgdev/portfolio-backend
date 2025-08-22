"""Education service for handling education operations."""

import logging
from typing import List

from sqlalchemy.orm import Session

from app.exceptions import ContentNotFoundError
from app.models.education import Education

logger = logging.getLogger(__name__)


class EducationService:
    """Service for managing education records."""

    def get_education_records(self, db: Session) -> List[Education]:
        """Get all education records ordered by ongoing first (end_date=null), then most recent first."""
        from sqlalchemy import case

        return (
            db.query(Education)
            .order_by(
                Education.display_order,
                case(
                    (Education.end_date.is_(None), 0), else_=1
                ),  # Ongoing first (null = 0, others = 1)
                Education.end_date.desc(),  # Then by most recent end date
                Education.start_date.desc(),  # Finally by most recent start date
            )
            .all()
        )

    def get_education_by_id(self, db: Session, education_id: int) -> Education:
        """Get education record by ID."""
        education = db.query(Education).filter(Education.id == education_id).first()
        if not education:
            raise ContentNotFoundError("education", education_id)
        return education


# Global service instance
education_service = EducationService()

"""Experience service for handling work experience operations."""

import logging
from typing import List

from sqlalchemy.orm import Session

from app.exceptions import ContentNotFoundError
from app.models.experience import Experience

logger = logging.getLogger(__name__)


class ExperienceService:
    """Service for managing work experience."""

    def get_experiences(self, db: Session) -> List[Experience]:
        """Get all experiences ordered by ongoing first (end_date=null), then most recent first."""
        from sqlalchemy import case

        return (
            db.query(Experience)
            .order_by(
                Experience.display_order,
                case(
                    (Experience.end_date.is_(None), 0), else_=1
                ),  # Ongoing first (null = 0, others = 1)
                Experience.end_date.desc(),  # Then by most recent end date
                Experience.start_date.desc(),  # Finally by most recent start date
            )
            .all()
        )

    def get_experience_by_id(self, db: Session, experience_id: int) -> Experience:
        """Get experience by ID."""
        experience = db.query(Experience).filter(Experience.id == experience_id).first()
        if not experience:
            raise ContentNotFoundError("experience", experience_id)
        return experience


# Global service instance
experience_service = ExperienceService()

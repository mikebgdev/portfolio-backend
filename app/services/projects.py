"""Projects service for handling project operations."""
from sqlalchemy.orm import Session
from app.models.projects import Project
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


class ProjectService:
    """Service for managing portfolio projects."""
    
    def get_projects(self, db: Session) -> List[Project]:
        """Get all projects ordered by display order and creation date."""
        return db.query(Project).order_by(
            Project.display_order, 
            Project.created_at.desc()
        ).all()

    def get_project_by_id(self, db: Session, project_id: int) -> Optional[Project]:
        """Get project by ID."""
        return db.query(Project).filter(Project.id == project_id).first()


# Global service instance
project_service = ProjectService()
"""Projects service for handling project operations."""
from sqlalchemy.orm import Session
from app.models.projects import Project
from app.exceptions import ContentNotFoundError
from typing import List
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

    def get_project_by_id(self, db: Session, project_id: int) -> Project:
        """Get project by ID."""
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise ContentNotFoundError("project", project_id)
        return project


# Global service instance
project_service = ProjectService()
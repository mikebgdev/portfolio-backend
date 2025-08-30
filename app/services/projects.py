"""Projects service for handling project operations."""

import logging
from typing import List

from sqlalchemy.orm import Session

from app.exceptions import ContentNotFoundError
from app.models.projects import Project
from app.utils.file_utils import encode_file_to_base64

logger = logging.getLogger(__name__)


class ProjectService:
    """Service for managing portfolio projects."""

    def get_projects(self, db: Session) -> List[Project]:
        """Get all projects ordered by display order and creation date."""
        projects = (
            db.query(Project)
            .order_by(Project.display_order, Project.created_at.desc())
            .all()
        )

        # Add image data for each project
        for project in projects:
            if hasattr(project, "image_file") and project.image_file:
                project.image_data = encode_file_to_base64(str(project.image_file))
            else:
                project.image_data = None

        return projects

    def get_project_by_id(self, db: Session, project_id: int) -> Project:
        """Get project by ID."""
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise ContentNotFoundError("project", project_id)

        # Add image data if image_file exists
        if hasattr(project, "image_file") and project.image_file:
            project.image_data = encode_file_to_base64(str(project.image_file))
        else:
            project.image_data = None

        return project


# Global service instance
project_service = ProjectService()

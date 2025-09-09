"""Projects service for handling project operations."""

import json
import logging
from typing import List

from sqlalchemy.orm import Session, joinedload

from app.exceptions import ContentNotFoundError
from app.models.projects import Project
from app.models.skills import Skill
from app.schemas.projects import ProjectCreate, ProjectUpdate
from app.utils.file_utils import encode_file_to_base64

logger = logging.getLogger(__name__)


class ProjectService:
    """Service for managing portfolio projects."""

    def get_projects(self, db: Session) -> List[Project]:
        """Get all projects ordered by display order and creation date."""
        projects = (
            db.query(Project)
            .options(joinedload(Project.skills))  # Eager load skills
            .order_by(Project.display_order, Project.created_at.desc())
            .all()
        )

        # Add image data and process technologies for each project
        for project in projects:
            self._process_project_data(project)

        return projects

    def get_project_by_id(self, db: Session, project_id: int) -> Project:
        """Get project by ID."""
        project = (
            db.query(Project)
            .options(joinedload(Project.skills))  # Eager load skills
            .filter(Project.id == project_id)
            .first()
        )
        if not project:
            raise ContentNotFoundError("project", project_id)

        self._process_project_data(project)
        return project

    def _process_project_data(self, project: Project) -> None:
        """Process project data - add image data and handle backward compatibility."""
        # Add image data if image_file exists
        if hasattr(project, "image_file") and project.image_file:
            project.image_data = encode_file_to_base64(str(project.image_file))
        else:
            project.image_data = None

        # For backward compatibility, populate technologies from skills
        if hasattr(project, "skills") and project.skills:
            # Convert skills to technologies list for backward compatibility
            project.technologies = [skill.name_en for skill in project.skills]
        elif hasattr(project, "technologies") and isinstance(project.technologies, str):
            # Handle legacy string-based technologies
            try:
                # Try to parse as JSON
                project.technologies = json.loads(project.technologies)
            except (json.JSONDecodeError, TypeError):
                # Handle comma-separated string
                project.technologies = [
                    tech.strip()
                    for tech in project.technologies.split(",")
                    if tech.strip()
                ]
        else:
            project.technologies = []

    def create_project(self, db: Session, project_data: ProjectCreate) -> Project:
        """Create a new project with associated skills."""
        # Convert project data to dict and remove skill_ids for model creation
        project_dict = project_data.dict(exclude={"skill_ids"})

        # Create the project
        project = Project(**project_dict)
        db.add(project)
        db.flush()  # Flush to get project ID

        # Associate skills if provided
        if project_data.skill_ids:
            skills = db.query(Skill).filter(Skill.id.in_(project_data.skill_ids)).all()

            # Verify all skills exist
            found_skill_ids = {skill.id for skill in skills}
            missing_skill_ids = set(project_data.skill_ids) - found_skill_ids
            if missing_skill_ids:
                raise ValueError(f"Skills not found: {list(missing_skill_ids)}")

            # Associate skills with project
            project.skills = skills

        db.commit()
        db.refresh(project)

        # Process project data (add image data, etc.)
        self._process_project_data(project)

        return project

    def update_project(
        self, db: Session, project_id: int, project_data: ProjectUpdate
    ) -> Project:
        """Update an existing project with new data and skills."""
        project = self.get_project_by_id(db, project_id)

        # Update project fields
        update_data = project_data.dict(exclude_unset=True, exclude={"skill_ids"})
        for field, value in update_data.items():
            setattr(project, field, value)

        # Update skills if provided
        if project_data.skill_ids is not None:
            if project_data.skill_ids:
                skills = (
                    db.query(Skill).filter(Skill.id.in_(project_data.skill_ids)).all()
                )

                # Verify all skills exist
                found_skill_ids = {skill.id for skill in skills}
                missing_skill_ids = set(project_data.skill_ids) - found_skill_ids
                if missing_skill_ids:
                    raise ValueError(f"Skills not found: {list(missing_skill_ids)}")

                # Update skills association
                project.skills = skills
            else:
                # Clear all skills if empty list provided
                project.skills = []

        db.commit()
        db.refresh(project)

        # Process project data
        self._process_project_data(project)

        return project

    def delete_project(self, db: Session, project_id: int) -> bool:
        """Delete a project by ID."""
        project = self.get_project_by_id(db, project_id)
        db.delete(project)
        db.commit()
        return True


# Global service instance
project_service = ProjectService()

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.models.content import About, Skill, Project, Experience, Education, Contact
from app.schemas.content import (
    AboutUpdate, SkillCreate, SkillUpdate, ProjectCreate, ProjectUpdate,
    ExperienceCreate, ExperienceUpdate, EducationCreate, EducationUpdate,
    ContactCreate, ContactUpdate
)
from app.exceptions import ContentNotFoundError, DatabaseError, ValidationError
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


class AboutService:
    def get_about(self, db: Session) -> Optional[About]:
        """Get about section content."""
        return db.query(About).first()

    def update_about(self, db: Session, about_data: AboutUpdate) -> About:
        """Update about section content."""
        try:
            about = self.get_about(db)
            if not about:
                # Create new about record if none exists
                about = About()
                db.add(about)

            update_data = about_data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(about, field, value)

            db.commit()
            db.refresh(about)
            return about
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error updating about content: {str(e)}")
            raise DatabaseError("update_about", str(e))


class SkillService:
    def get_skills(self, db: Session, skill_category: Optional[str] = None) -> List[Skill]:
        """Get all skills, optionally filtered by category."""
        query = db.query(Skill)
        if skill_category:
            query = query.filter(Skill.category == skill_category)
        return query.order_by(Skill.display_order, Skill.name).all()

    def get_skill_by_id(self, db: Session, skill_id: int) -> Skill:
        """Get skill by ID."""
        skill = db.query(Skill).filter(Skill.id == skill_id).first()
        if not skill:
            raise ContentNotFoundError("skill", skill_id)
        return skill

    def create_skill(self, db: Session, skill_data: SkillCreate) -> Skill:
        """Create a new skill."""
        try:
            # Validate skill data
            if not skill_data.name or len(skill_data.name.strip()) == 0:
                raise ValidationError("name", skill_data.name, "Skill name cannot be empty")
            
            skill = Skill(**skill_data.model_dump())
            db.add(skill)
            db.commit()
            db.refresh(skill)
            return skill
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error creating skill: {str(e)}")
            raise DatabaseError("create_skill", str(e))

    def update_skill(self, db: Session, skill_id: int, skill_data: SkillUpdate) -> Skill:
        """Update existing skill."""
        skill = self.get_skill_by_id(db, skill_id)
        if not skill:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Skill not found"
            )

        update_data = skill_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(skill, field, value)

        db.commit()
        db.refresh(skill)
        return skill

    def delete_skill(self, db: Session, skill_id: int) -> bool:
        """Delete skill by ID."""
        skill = self.get_skill_by_id(db, skill_id)
        if not skill:
            return False

        db.delete(skill)
        db.commit()
        return True


class ProjectService:
    def get_projects(self, db: Session) -> List[Project]:
        """Get all projects ordered by display order and creation date."""
        return db.query(Project).order_by(Project.display_order, Project.created_at.desc()).all()

    def get_project_by_id(self, db: Session, project_id: int) -> Optional[Project]:
        """Get project by ID."""
        return db.query(Project).filter(Project.id == project_id).first()

    def create_project(self, db: Session, project_data: ProjectCreate) -> Project:
        """Create a new project."""
        project = Project(**project_data.model_dump())
        db.add(project)
        db.commit()
        db.refresh(project)
        return project

    def update_project(self, db: Session, project_id: int, project_data: ProjectUpdate) -> Project:
        """Update existing project."""
        project = self.get_project_by_id(db, project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )

        update_data = project_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(project, field, value)

        db.commit()
        db.refresh(project)
        return project

    def delete_project(self, db: Session, project_id: int) -> bool:
        """Delete project by ID."""
        project = self.get_project_by_id(db, project_id)
        if not project:
            return False

        db.delete(project)
        db.commit()
        return True


class ExperienceService:
    def get_experiences(self, db: Session) -> List[Experience]:
        """Get all experiences ordered by display order and start date (most recent first)."""
        return db.query(Experience).order_by(Experience.display_order, Experience.start_date.desc()).all()

    def get_experience_by_id(self, db: Session, experience_id: int) -> Optional[Experience]:
        """Get experience by ID."""
        return db.query(Experience).filter(Experience.id == experience_id).first()

    def create_experience(self, db: Session, experience_data: ExperienceCreate) -> Experience:
        """Create a new experience."""
        experience = Experience(**experience_data.model_dump())
        db.add(experience)
        db.commit()
        db.refresh(experience)
        return experience

    def update_experience(self, db: Session, experience_id: int, experience_data: ExperienceUpdate) -> Experience:
        """Update existing experience."""
        experience = self.get_experience_by_id(db, experience_id)
        if not experience:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Experience not found"
            )

        update_data = experience_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(experience, field, value)

        db.commit()
        db.refresh(experience)
        return experience

    def delete_experience(self, db: Session, experience_id: int) -> bool:
        """Delete experience by ID."""
        experience = self.get_experience_by_id(db, experience_id)
        if not experience:
            return False

        db.delete(experience)
        db.commit()
        return True


class EducationService:
    def get_education_records(self, db: Session) -> List[Education]:
        """Get all education records ordered by display order and start date (most recent first)."""
        return db.query(Education).order_by(Education.display_order, Education.start_date.desc()).all()

    def get_education_by_id(self, db: Session, education_id: int) -> Optional[Education]:
        """Get education record by ID."""
        return db.query(Education).filter(Education.id == education_id).first()

    def create_education(self, db: Session, education_data: EducationCreate) -> Education:
        """Create a new education record."""
        education = Education(**education_data.model_dump())
        db.add(education)
        db.commit()
        db.refresh(education)
        return education

    def update_education(self, db: Session, education_id: int, education_data: EducationUpdate) -> Education:
        """Update existing education record."""
        education = self.get_education_by_id(db, education_id)
        if not education:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Education record not found"
            )

        update_data = education_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(education, field, value)

        db.commit()
        db.refresh(education)
        return education

    def delete_education(self, db: Session, education_id: int) -> bool:
        """Delete education record by ID."""
        education = self.get_education_by_id(db, education_id)
        if not education:
            return False

        db.delete(education)
        db.commit()
        return True


class ContactService:
    def get_contact(self, db: Session) -> Optional[Contact]:
        """Get contact section content."""
        return db.query(Contact).first()

    def update_contact(self, db: Session, contact_data: ContactUpdate) -> Contact:
        """Update contact section content."""
        contact = self.get_contact(db)
        if not contact:
            # Create new contact record if none exists
            contact_dict = contact_data.model_dump(exclude_unset=True)
            contact = Contact(**contact_dict)
            db.add(contact)
        else:
            update_data = contact_data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(contact, field, value)

        db.commit()
        db.refresh(contact)
        return contact


# Global service instances
about_service = AboutService()
skill_service = SkillService()
project_service = ProjectService()
experience_service = ExperienceService()
education_service = EducationService()
contact_service = ContactService()
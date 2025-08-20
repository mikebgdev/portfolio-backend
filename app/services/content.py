from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.models.content import About, Skill, SkillCategory, Project, Experience, Education, Contact
from app.schemas.content import (
    AboutUpdate, SkillCreate, SkillUpdate, SkillCategoryCreate, SkillCategoryUpdate,
    ProjectCreate, ProjectUpdate, ExperienceCreate, ExperienceUpdate, 
    EducationCreate, EducationUpdate, ContactCreate, ContactUpdate,
    SkillsGroupedResponse, CategoryWithSkillsResponse, SkillNestedResponse
)
from app.exceptions import ContentNotFoundError, DatabaseError, ValidationError
from app.utils.cache import cached, ContentCache, cache_manager
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


class AboutService:
    def get_about(self, db: Session) -> Optional[About]:
        """Get about section content."""
        return db.query(About).first()

    async def update_about(self, db: Session, about_data: AboutUpdate) -> About:
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
            
            # Invalidate HTTP cache for about endpoints
            await self._invalidate_about_cache()
            logger.info("About content updated and cache invalidated")
            
            return about
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error updating about content: {str(e)}")
            raise DatabaseError("update_about", str(e))
    
    async def _invalidate_about_cache(self):
        """Invalidate all cached about endpoints."""
        try:
            # Clear HTTP cache for about endpoints with different query params
            cache_keys = [
                "http_cache:/api/v1/about:",
                "http_cache:/api/v1/about/:",
            ]
            
            for key_pattern in cache_keys:
                # Try to delete common cache variations
                for lang in ["", "lang=en", "lang=es"]:
                    cache_key = f"{key_pattern}{lang}"
                    await cache_manager.delete(cache_key)
            
            logger.info("About cache invalidated successfully")
        except Exception as e:
            logger.warning(f"Failed to invalidate about cache: {str(e)}")
            # Don't raise - cache invalidation failure shouldn't break the update


class SkillCategoryService:
    def get_categories(self, db: Session) -> List[SkillCategory]:
        """Get all active skill categories."""
        return db.query(SkillCategory).filter(SkillCategory.active == True).order_by(SkillCategory.display_order, SkillCategory.label_en).all()

    def get_category_by_id(self, db: Session, category_id: int) -> SkillCategory:
        """Get category by ID."""
        category = db.query(SkillCategory).filter(SkillCategory.id == category_id).first()
        if not category:
            raise ContentNotFoundError("skill_category", category_id)
        return category
    
    def get_category_by_slug(self, db: Session, slug: str) -> SkillCategory:
        """Get category by slug."""
        category = db.query(SkillCategory).filter(SkillCategory.slug == slug).first()
        if not category:
            raise ContentNotFoundError("skill_category", slug)
        return category

    def create_category(self, db: Session, category_data: SkillCategoryCreate) -> SkillCategory:
        """Create a new skill category."""
        try:
            category = SkillCategory(**category_data.model_dump())
            db.add(category)
            db.commit()
            db.refresh(category)
            return category
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error creating skill category: {str(e)}")
            raise DatabaseError("create_skill_category", str(e))

    async def update_category(self, db: Session, category_id: int, category_data: SkillCategoryUpdate) -> SkillCategory:
        """Update existing skill category."""
        category = self.get_category_by_id(db, category_id)

        update_data = category_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(category, field, value)

        db.commit()
        db.refresh(category)
        
        # Invalidate skills cache since categories changed
        await self._invalidate_skills_cache()
        
        return category

    def delete_category(self, db: Session, category_id: int) -> bool:
        """Delete skill category."""
        category = self.get_category_by_id(db, category_id)
        
        # Check if category has skills
        skills_count = db.query(Skill).filter(Skill.category_id == category_id).count()
        if skills_count > 0:
            raise ValidationError("category_id", category_id, f"Cannot delete category with {skills_count} skills")
        
        db.delete(category)
        db.commit()
        return True
    
    async def _invalidate_skills_cache(self):
        """Invalidate skills cache."""
        try:
            cache_patterns = [
                "http_cache:/api/v1/skills:",
                "skills_grouped:",
            ]
            
            for pattern in cache_patterns:
                await cache_manager.delete(pattern)
            
            logger.info("Skills cache invalidated successfully")
        except Exception as e:
            logger.warning(f"Failed to invalidate skills cache: {str(e)}")


class SkillService:
    @cached(ttl=600, key_prefix="skills_grouped")  # Cache for 10 minutes
    async def get_skills_grouped(self, db: Session, language: str = 'en') -> SkillsGroupedResponse:
        """Get skills grouped by categories in the nested structure."""
        categories = db.query(SkillCategory).filter(SkillCategory.active == True).order_by(SkillCategory.display_order).all()
        
        grouped_categories = []
        for category in categories:
            # Get skills for this category
            skills = db.query(Skill).filter(
                Skill.category_id == category.id,
                Skill.active == True
            ).order_by(Skill.display_order, Skill.name_en).all()
            
            # Build skills list
            category_skills = []
            for skill in skills:
                skill_name = skill.name_es if language == 'es' and skill.name_es else skill.name_en
                category_skills.append(SkillNestedResponse(
                    name=skill_name,
                    icon_name=skill.icon_name,
                    color=skill.color
                ))
            
            # Build category response
            category_label = category.label_es if language == 'es' and category.label_es else category.label_en
            grouped_categories.append(CategoryWithSkillsResponse(
                id=category.slug,
                label=category_label,
                icon_name=category.icon_name,
                skills=category_skills
            ))
        
        return SkillsGroupedResponse(categories=grouped_categories)

    def get_skills(self, db: Session, category_id: Optional[int] = None) -> List[Skill]:
        """Get all skills, optionally filtered by category ID."""
        query = db.query(Skill).filter(Skill.active == True)  # Only active skills
        if category_id:
            query = query.filter(Skill.category_id == category_id)
        return query.order_by(Skill.display_order, Skill.name_en).all()

    def get_skill_by_id(self, db: Session, skill_id: int) -> Skill:
        """Get skill by ID."""
        skill = db.query(Skill).filter(Skill.id == skill_id).first()
        if not skill:
            raise ContentNotFoundError("skill", skill_id)
        return skill

    async def create_skill(self, db: Session, skill_data: SkillCreate) -> Skill:
        """Create a new skill."""
        try:
            # Validate skill data
            if not skill_data.name_en or len(skill_data.name_en.strip()) == 0:
                raise ValidationError("name_en", skill_data.name_en, "Skill name (English) cannot be empty")
            
            # Validate category exists
            category = db.query(SkillCategory).filter(SkillCategory.id == skill_data.category_id).first()
            if not category:
                raise ValidationError("category_id", skill_data.category_id, "Category does not exist")
            
            skill = Skill(**skill_data.model_dump())
            db.add(skill)
            db.commit()
            db.refresh(skill)
            
            # Invalidate skills cache
            await self._invalidate_skills_cache()
            
            return skill
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error creating skill: {str(e)}")
            raise DatabaseError("create_skill", str(e))

    async def update_skill(self, db: Session, skill_id: int, skill_data: SkillUpdate) -> Skill:
        """Update existing skill."""
        skill = self.get_skill_by_id(db, skill_id)

        update_data = skill_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(skill, field, value)

        db.commit()
        db.refresh(skill)
        
        # Invalidate skills cache
        await self._invalidate_skills_cache()
        
        return skill

    async def delete_skill(self, db: Session, skill_id: int) -> bool:
        """Delete skill by ID."""
        skill = self.get_skill_by_id(db, skill_id)
        if not skill:
            return False

        db.delete(skill)
        db.commit()
        
        # Invalidate skills cache
        await self._invalidate_skills_cache()
        
        return True
    
    async def _invalidate_skills_cache(self):
        """Invalidate skills cache."""
        try:
            cache_patterns = [
                "http_cache:/api/v1/skills:",
                "skills_grouped:",
            ]
            
            for pattern in cache_patterns:
                await cache_manager.delete(pattern)
            
            logger.info("Skills cache invalidated successfully")
        except Exception as e:
            logger.warning(f"Failed to invalidate skills cache: {str(e)}")


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
skill_category_service = SkillCategoryService()
skill_service = SkillService()
project_service = ProjectService()
experience_service = ExperienceService()
education_service = EducationService()
contact_service = ContactService()
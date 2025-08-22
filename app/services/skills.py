"""Skills service for handling skills and categories operations."""

import logging
from typing import List, Optional

from sqlalchemy.orm import Session

from app.exceptions import ContentNotFoundError
from app.models.skills import Skill, SkillCategory
from app.schemas.skills import (
    CategoryWithSkillsResponse,
    SkillNestedResponse,
    SkillsGroupedResponse,
)
from app.utils.cache import cache_manager, cached

logger = logging.getLogger(__name__)


class SkillCategoryService:
    """Service for managing skill categories."""

    def get_categories(self, db: Session) -> List[SkillCategory]:
        """Get all active skill categories."""
        return (
            db.query(SkillCategory)
            .filter(SkillCategory.active.is_(True))
            .order_by(SkillCategory.display_order, SkillCategory.label_en)
            .all()
        )

    def get_category_by_id(self, db: Session, category_id: int) -> SkillCategory:
        """Get category by ID."""
        category = (
            db.query(SkillCategory).filter(SkillCategory.id == category_id).first()
        )
        if not category:
            raise ContentNotFoundError("skill_category", category_id)
        return category

    def get_category_by_slug(self, db: Session, slug: str) -> SkillCategory:
        """Get category by slug."""
        category = db.query(SkillCategory).filter(SkillCategory.slug == slug).first()
        if not category:
            raise ContentNotFoundError("skill_category", slug)
        return category

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
    """Service for managing individual skills."""

    @cached(ttl=600, key_prefix="skills_grouped")  # Cache for 10 minutes
    async def get_skills_grouped(
        self, db: Session, language: str = "en"
    ) -> SkillsGroupedResponse:
        """Get skills grouped by categories in the nested structure."""
        categories = (
            db.query(SkillCategory)
            .filter(SkillCategory.active.is_(True))
            .order_by(SkillCategory.display_order)
            .all()
        )

        grouped_categories = []
        for category in categories:
            # Get skills for this category
            skills = (
                db.query(Skill)
                .filter(Skill.category_id == category.id, Skill.active.is_(True))
                .order_by(Skill.display_order, Skill.name_en)
                .all()
            )

            # Build skills list
            category_skills = []
            for skill in skills:
                skill_name = (
                    skill.name_es
                    if language == "es" and skill.name_es
                    else skill.name_en
                )
                category_skills.append(
                    SkillNestedResponse(
                        name=skill_name, icon_name=skill.icon_name, color=skill.color
                    )
                )

            # Build category response
            category_label = (
                category.label_es
                if language == "es" and category.label_es
                else category.label_en
            )
            grouped_categories.append(
                CategoryWithSkillsResponse(
                    id=category.slug,
                    label=category_label,
                    icon_name=category.icon_name,
                    skills=category_skills,
                )
            )

        return SkillsGroupedResponse(categories=grouped_categories)

    def get_skills(self, db: Session, category_id: Optional[int] = None) -> List[Skill]:
        """Get all skills, optionally filtered by category ID."""
        query = db.query(Skill).filter(Skill.active.is_(True))
        if category_id:
            query = query.filter(Skill.category_id == category_id)
        return query.order_by(Skill.display_order, Skill.name_en).all()

    def get_skill_by_id(self, db: Session, skill_id: int) -> Skill:
        """Get skill by ID."""
        skill = db.query(Skill).filter(Skill.id == skill_id).first()
        if not skill:
            raise ContentNotFoundError("skill", skill_id)
        return skill

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


# Global service instances
skill_category_service = SkillCategoryService()
skill_service = SkillService()

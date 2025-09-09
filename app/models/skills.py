"""Skills and skill categories models."""

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class SkillCategory(Base):
    """Model for skill categories."""

    __tablename__ = "skill_categories"

    id = Column(Integer, primary_key=True, index=True)

    # Category identifier
    slug = Column(String(100), unique=True, nullable=False, index=True)

    # Multilingual labels
    label_en = Column(String(200), nullable=False)
    label_es = Column(String(200), nullable=True)

    # UI properties
    icon_name = Column(String(100), nullable=False)
    display_order = Column(Integer, default=0)
    active = Column(Boolean, default=True)

    # Relationships
    skills = relationship(
        "Skill", back_populates="skill_category", cascade="all, delete-orphan"
    )

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __str__(self):
        """String representation for admin interface."""
        try:
            return f"{self.label_en} ({self.slug})"
        except Exception:
            return f"SkillCategory {self.id if hasattr(self, 'id') else 'Unknown'}"


class Skill(Base):
    """Model for individual skills."""

    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, index=True)

    # Multilingual skill names
    name_en = Column(String(200), nullable=False)
    name_es = Column(String(200), nullable=True)

    # Category relationship
    category_id = Column(Integer, ForeignKey("skill_categories.id"), nullable=True)
    skill_category = relationship("SkillCategory", back_populates="skills")

    # UI properties
    icon_name = Column(String(100), nullable=False)
    color = Column(String(50), nullable=True)

    # Status and ordering
    display_order = Column(Integer, default=0)
    active = Column(Boolean, default=True)

    # Relationships - importing here to avoid circular imports
    projects = relationship(
        "Project", secondary="project_skills", back_populates="skills"
    )

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __str__(self):
        """String representation for admin interface."""
        try:
            category_label = (
                self.skill_category.label_en if self.skill_category else "No category"
            )
            return f"{self.name_en} ({category_label})"
        except Exception:
            return f"{self.name_en} (Category error)"

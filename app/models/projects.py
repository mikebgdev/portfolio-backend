"""Projects model for portfolio projects."""

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base

# Association table for many-to-many relationship between projects and skills
project_skills = Table(
    "project_skills",
    Base.metadata,
    Column("project_id", Integer, ForeignKey("projects.id"), primary_key=True),
    Column("skill_id", Integer, ForeignKey("skills.id"), primary_key=True),
)


class Project(Base):
    """Model for portfolio projects."""

    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)

    # Multilingual project information
    title_en = Column(String(200), nullable=False)
    title_es = Column(String(200), nullable=True)
    description_en = Column(Text, nullable=False)
    description_es = Column(Text, nullable=True)

    # Visual details
    image_file = Column(String(500), nullable=True)  # File upload path

    # Project links
    source_url = Column(String(500), nullable=True)
    demo_url = Column(String(500), nullable=True)

    # Display settings
    display_order = Column(Integer, default=0)
    activa = Column(Boolean, default=True)

    # Relationships
    skills = relationship("Skill", secondary=project_skills, back_populates="projects")

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __str__(self):
        """String representation for admin interface."""
        return f"{self.title_en}"

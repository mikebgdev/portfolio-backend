"""Projects schemas for API requests and responses."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from .skills import SkillResponse

# Removed ProjectBase, ProjectCreate, and ProjectUpdate schemas as they are no longer needed


class ProjectResponse(BaseModel):
    """Schema for Project API responses."""

    id: int
    # Multilingual fields
    title_en: str
    title_es: Optional[str] = None
    description_en: str
    description_es: Optional[str] = None

    # Non-translatable fields
    image_file: Optional[str] = None
    source_url: Optional[str] = None
    demo_url: Optional[str] = None
    display_order: int
    activa: bool
    created_at: datetime

    # Skills information
    skills: List[SkillResponse] = Field(
        default_factory=list, description="Skills used in this project"
    )

    # Localization
    language: Optional[str] = "en"

    # File data (populated by service layer)
    image_data: Optional[Dict[str, Any]] = Field(
        None, description="Project image as Base64 data URL"
    )

    class Config:
        from_attributes = True

    @property
    def title(self) -> str:
        """Return project title in requested language (fallback to English)."""
        return (
            self.title_es if self.language == "es" and self.title_es else self.title_en
        )

    @property
    def description(self) -> str:
        """Return project description in requested language (fallback to English)."""
        return (
            self.description_es
            if self.language == "es" and self.description_es
            else self.description_en
        )

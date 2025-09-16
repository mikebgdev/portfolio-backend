"""Skills schemas for API requests and responses."""

import re
from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field, validator

from app.utils.iconify import (
    format_hex_color,
    get_icon_tooltip_info,
    validate_hex_color,
)


class SkillCategoryBase(BaseModel):
    """Base schema for SkillCategory with common fields."""

    slug: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Category slug (unique identifier)",
    )
    label_en: str = Field(
        ..., min_length=1, max_length=100, description="Category label in English"
    )
    label_es: Optional[str] = Field(
        None, max_length=100, description="Category label in Spanish"
    )
    icon_name: str = Field(
        ..., min_length=1, max_length=50, description="Icon name for frontend"
    )
    display_order: Optional[int] = Field(0, ge=0, le=1000, description="Display order")
    active: Optional[bool] = Field(True, description="Whether category is active")

    @validator("slug")
    def validate_slug(cls, v):
        if not v or not v.strip():
            raise ValueError("Slug cannot be empty")
        if not re.match(r"^[a-z0-9_]+$", v.strip().lower()):
            raise ValueError(
                "Slug can only contain lowercase letters, numbers, and underscores"
            )
        return v.strip().lower()


class SkillCategoryResponse(SkillCategoryBase):
    """Schema for SkillCategory API responses."""

    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    language: Optional[str] = "en"

    class Config:
        from_attributes = True

    @property
    def label(self) -> str:
        """Return category label in requested language (fallback to English)."""
        return (
            self.label_es if self.language == "es" and self.label_es else self.label_en
        )


class SkillBase(BaseModel):
    """Base schema for Skill with common fields."""

    name_en: str = Field(
        ..., min_length=1, max_length=100, description="Skill name in English"
    )
    name_es: Optional[str] = Field(
        None, max_length=100, description="Skill name in Spanish"
    )
    category_id: int = Field(..., gt=0, description="Category ID")
    icon_name: str = Field(
        ..., min_length=1, max_length=50, description="Icon name for frontend"
    )
    color: Optional[str] = Field(None, max_length=50, description="CSS color class")
    display_order: Optional[int] = Field(
        0, ge=0, le=1000, description="Display order within category"
    )
    active: Optional[bool] = Field(True, description="Whether skill is active")

    @validator("color")
    def validate_color(cls, v):
        if v:
            if not v.strip():
                return None

            stripped_v = v.strip()

            # Check if it's a hex color
            if stripped_v.startswith("#"):
                if not validate_hex_color(stripped_v):
                    raise ValueError(
                        "Invalid hex color format. Use format like #FF0000 or #F00"
                    )
                return format_hex_color(stripped_v)

            # Check if it's a Tailwind CSS class or valid CSS color name
            if not re.match(r"^(text-\w+(-\d+)?|\w+)$", stripped_v):
                raise ValueError(
                    "Invalid color format. Use hex colors (#FF0000), Tailwind classes "
                    "(text-blue-500), or CSS color names"
                )

        return v.strip() if v else None


class SkillResponse(SkillBase):
    """Schema for Skill API responses."""

    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    language: Optional[str] = "en"

    class Config:
        from_attributes = True

    @property
    def name(self) -> str:
        """Return skill name in requested language (fallback to English)."""
        return self.name_es if self.language == "es" and self.name_es else self.name_en

    @property
    def icon_tooltip(self) -> Dict:
        """Get icon and color tooltip information."""
        return get_icon_tooltip_info(self.icon_name, self.color, "skill")


# Nested Skills Response Schemas (for the grouped structure)
class SkillNestedResponse(BaseModel):
    """Simplified skill response for nested structure."""

    name: str
    icon_name: str
    color: Optional[str] = None

    class Config:
        from_attributes = True


class CategoryWithSkillsResponse(BaseModel):
    """Category with nested skills for the grouped endpoint response."""

    id: str  # This will be the slug
    label: str
    icon_name: str
    skills: List[SkillNestedResponse]

    class Config:
        from_attributes = True


class SkillsGroupedResponse(BaseModel):
    """Main response schema for grouped skills endpoint."""

    categories: List[CategoryWithSkillsResponse]

"""Projects schemas for API requests and responses."""

import re
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, validator


class ProjectBase(BaseModel):
    """Base schema for Project with common fields."""

    # Multilingual fields
    title_en: str = Field(
        ..., min_length=1, max_length=200, description="Project title in English"
    )
    title_es: Optional[str] = Field(
        None, max_length=200, description="Project title in Spanish"
    )
    description_en: str = Field(
        ...,
        min_length=10,
        max_length=2000,
        description="Project description in English",
    )
    description_es: Optional[str] = Field(
        None, max_length=2000, description="Project description in Spanish"
    )

    # Non-translatable fields
    image_file: Optional[str] = Field(None, description="Project image file path")
    technologies: List[str] = Field(
        ...,
        min_length=1,
        description="Technologies used as list",
    )
    source_url: Optional[str] = Field(None, description="Source code URL")
    demo_url: Optional[str] = Field(None, description="Live demo URL")
    display_order: Optional[int] = Field(0, ge=0, le=1000, description="Display order")
    activa: Optional[bool] = Field(True, description="Whether project is active")

    @validator("source_url", "demo_url")
    def validate_urls(cls, v):
        if v and not v.startswith(("http://", "https://")):
            raise ValueError("URL must start with http:// or https://")
        return v

    @validator("image_file")
    def validate_image_file(cls, v):
        if v and not v.startswith("/uploads/"):
            raise ValueError("Image file must be an uploaded file path")
        return v

    @validator("technologies")
    def validate_technologies(cls, v):
        if isinstance(v, str):
            # Handle JSON string from database
            try:
                import json

                techs = json.loads(v)
            except json.JSONDecodeError:
                # Handle comma-separated string
                techs = [tech.strip() for tech in v.split(",") if tech.strip()]
        elif isinstance(v, list):
            techs = [str(tech).strip() for tech in v if str(tech).strip()]
        else:
            raise ValueError("Technologies must be a list or string")

        if not techs:
            raise ValueError("At least one technology must be specified")
        return techs

    @validator("title_en", "title_es")
    def validate_titles(cls, v):
        if v:
            v = v.strip()
            if not v:
                raise ValueError("Title cannot be empty or only whitespace")
            suspicious_patterns = ["<", ">", "script", "javascript:"]
            for pattern in suspicious_patterns:
                if pattern.lower() in v.lower():
                    raise ValueError(f"Title contains invalid characters: {pattern}")
        return v

    @validator("description_en", "description_es")
    def validate_descriptions(cls, v):
        if v:
            v = re.sub(r"\s+", " ", v.strip())
            suspicious_patterns = ["<script", "javascript:", "onclick=", "onerror="]
            for pattern in suspicious_patterns:
                if pattern.lower() in v.lower():
                    raise ValueError(
                        f"Description contains potentially unsafe elements: {pattern}"
                    )
        return v


class ProjectResponse(ProjectBase):
    """Schema for Project API responses."""

    id: int
    created_at: datetime
    language: Optional[str] = "en"
    available_languages: List[str] = ["en", "es"]

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

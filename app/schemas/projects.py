"""Projects schemas for API requests and responses."""

import re
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, validator

from .skills import SkillResponse


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
    skill_ids: List[int] = Field(
        ...,
        min_length=1,
        description="Skill IDs used in this project",
    )
    # Keep technologies for backward compatibility during migration
    technologies: Optional[List[str]] = Field(
        None,
        description="Technologies used as list (deprecated, use skill_ids)",
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

    @validator("skill_ids")
    def validate_skill_ids(cls, v):
        if not v:
            raise ValueError("At least one skill must be specified")

        # Ensure all values are integers
        try:
            skill_ids = [int(skill_id) for skill_id in v]
        except (ValueError, TypeError):
            raise ValueError("All skill IDs must be valid integers")

        if any(skill_id <= 0 for skill_id in skill_ids):
            raise ValueError("All skill IDs must be positive integers")

        # Remove duplicates while preserving order
        seen = set()
        unique_skills = []
        for skill_id in skill_ids:
            if skill_id not in seen:
                seen.add(skill_id)
                unique_skills.append(skill_id)

        return unique_skills

    @validator("technologies")
    def validate_technologies(cls, v):
        # Optional validation for backward compatibility
        if v is None:
            return v

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


class ProjectCreate(BaseModel):
    """Schema for creating new projects."""

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
    skill_ids: List[int] = Field(
        ...,
        min_length=1,
        description="Skill IDs used in this project",
    )
    source_url: Optional[str] = Field(None, description="Source code URL")
    demo_url: Optional[str] = Field(None, description="Live demo URL")
    display_order: Optional[int] = Field(0, ge=0, le=1000, description="Display order")
    activa: Optional[bool] = Field(True, description="Whether project is active")

    # Apply the same validators from ProjectBase
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

    @validator("skill_ids")
    def validate_skill_ids(cls, v):
        if not v:
            raise ValueError("At least one skill must be specified")

        # Ensure all values are integers
        try:
            skill_ids = [int(skill_id) for skill_id in v]
        except (ValueError, TypeError):
            raise ValueError("All skill IDs must be valid integers")

        if any(skill_id <= 0 for skill_id in skill_ids):
            raise ValueError("All skill IDs must be positive integers")

        # Remove duplicates while preserving order
        seen = set()
        unique_skills = []
        for skill_id in skill_ids:
            if skill_id not in seen:
                seen.add(skill_id)
                unique_skills.append(skill_id)

        return unique_skills

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


class ProjectUpdate(BaseModel):
    """Schema for updating existing projects."""

    # All fields optional for partial updates
    title_en: Optional[str] = Field(
        None, min_length=1, max_length=200, description="Project title in English"
    )
    title_es: Optional[str] = Field(
        None, max_length=200, description="Project title in Spanish"
    )
    description_en: Optional[str] = Field(
        None,
        min_length=10,
        max_length=2000,
        description="Project description in English",
    )
    description_es: Optional[str] = Field(
        None, max_length=2000, description="Project description in Spanish"
    )

    image_file: Optional[str] = Field(None, description="Project image file path")
    skill_ids: Optional[List[int]] = Field(
        None,
        description="Skill IDs used in this project",
    )
    source_url: Optional[str] = Field(None, description="Source code URL")
    demo_url: Optional[str] = Field(None, description="Live demo URL")
    display_order: Optional[int] = Field(
        None, ge=0, le=1000, description="Display order"
    )
    activa: Optional[bool] = Field(None, description="Whether project is active")

    # Apply the same validators (but handle optional fields)
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

    @validator("skill_ids")
    def validate_skill_ids(cls, v):
        if v is not None:  # Only validate if provided
            if not v:
                raise ValueError("At least one skill must be specified")

            # Ensure all values are integers
            try:
                skill_ids = [int(skill_id) for skill_id in v]
            except (ValueError, TypeError):
                raise ValueError("All skill IDs must be valid integers")

            if any(skill_id <= 0 for skill_id in skill_ids):
                raise ValueError("All skill IDs must be positive integers")

            # Remove duplicates while preserving order
            seen = set()
            unique_skills = []
            for skill_id in skill_ids:
                if skill_id not in seen:
                    seen.add(skill_id)
                    unique_skills.append(skill_id)

            return unique_skills
        return v

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

    # Skills information (replaces technologies)
    skills: List[SkillResponse] = Field(
        default_factory=list, description="Skills used in this project"
    )
    # Keep technologies for backward compatibility
    technologies: Optional[List[str]] = Field(
        None, description="Technologies used as list (deprecated, use skills)"
    )

    # Localization and metadata
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

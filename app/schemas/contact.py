"""Contact schemas for API requests and responses."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ContactBase(BaseModel):
    """Base schema for Contact with common fields."""

    email: str = Field(..., description="Email address")
    linkedin_url: Optional[str] = Field(None, description="LinkedIn profile URL")
    github_url: Optional[str] = Field(None, description="GitHub profile URL")
    contact_form_enabled: Optional[bool] = Field(
        True, description="Enable contact form"
    )

    # Multilingual contact messages
    contact_message_en: Optional[str] = Field(
        None, description="Contact message in English"
    )
    contact_message_es: Optional[str] = Field(
        None, description="Contact message in Spanish"
    )

    # CV file
    cv_file: Optional[str] = Field(None, description="CV file path")


class ContactResponse(ContactBase):
    """Schema for Contact API responses."""

    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    language: Optional[str] = "en"
    available_languages: List[str] = ["en", "es"]

    # File data (populated by service layer)
    cv_data: Optional[Dict[str, Any]] = Field(
        None, description="CV file as Base64 data URL"
    )

    class Config:
        from_attributes = True

    @property
    def contact_message(self) -> Optional[str]:
        """Return contact message in requested language (fallback to English)."""
        if self.language == "es" and self.contact_message_es:
            return self.contact_message_es
        return self.contact_message_en

"""Contact schemas for API requests and responses."""

import re
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


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


# Contact Message schemas for the send message endpoint
class ContactMessageRequest(BaseModel):
    """Schema for contact message requests."""

    name: str = Field(..., min_length=1, max_length=255, description="Sender's name")
    email: str = Field(..., description="Sender's email address")
    subject: Optional[str] = Field(
        None, max_length=500, description="Message subject"
    )
    message: str = Field(
        ..., min_length=1, max_length=5000, description="Message content"
    )
    phone: Optional[str] = Field(
        None, max_length=50, description="Optional phone number"
    )

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Validate email format."""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, v):
            raise ValueError("Invalid email format")
        return v.lower().strip()

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate and clean name."""
        return v.strip()

    @field_validator("message")
    @classmethod
    def validate_message(cls, v: str) -> str:
        """Validate and clean message."""
        return v.strip()

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        """Validate and clean phone number."""
        if v:
            # Remove common phone formatting characters
            cleaned = re.sub(r'[^\d+\-\(\)\s]', '', v.strip())
            return cleaned if cleaned else None
        return v


class ContactMessageResponse(BaseModel):
    """Schema for contact message responses."""

    success: bool = Field(..., description="Whether the message was sent successfully")
    message: str = Field(..., description="Response message")
    id: Optional[str] = Field(None, description="Message ID (optional)")

    class Config:
        from_attributes = True

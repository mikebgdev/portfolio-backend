"""Experience schemas for API requests and responses."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_serializer


class ExperienceBase(BaseModel):
    """Base schema for Experience with common fields."""

    company: str = Field(..., description="Company name")
    location: Optional[str] = Field(None, description="Work location")

    # Multilingual fields
    position_en: str = Field(..., description="Position in English")
    position_es: Optional[str] = Field(None, description="Position in Spanish")
    description_en: str = Field(..., description="Job description in English")
    description_es: Optional[str] = Field(
        None, description="Job description in Spanish"
    )

    # Date fields
    start_date: datetime = Field(..., description="Start date")
    end_date: Optional[datetime] = Field(
        None, description="End date (null for current)"
    )

    # Display settings
    display_order: Optional[int] = Field(0, description="Display order")
    activo: Optional[bool] = Field(True, description="Whether experience is active")


class ExperienceResponse(ExperienceBase):
    """Schema for Experience API responses."""

    id: int
    created_at: datetime
    language: Optional[str] = "en"

    class Config:
        from_attributes = True

    @field_serializer("start_date", "end_date")
    def serialize_date(self, value: Optional[datetime]) -> Optional[str]:
        """Serialize dates in YYYY/MM/DD format."""
        if value is None:
            return None
        return value.strftime("%Y/%m/%d")

    @property
    def position(self) -> str:
        """Return position in requested language (fallback to English)."""
        return (
            self.position_es
            if self.language == "es" and self.position_es
            else self.position_en
        )

    @property
    def description(self) -> str:
        """Return description in requested language (fallback to English)."""
        return (
            self.description_es
            if self.language == "es" and self.description_es
            else self.description_en
        )

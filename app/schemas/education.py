"""Education schemas for API requests and responses."""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class EducationBase(BaseModel):
    """Base schema for Education with common fields."""
    institution: str = Field(..., description="Institution name")
    location: Optional[str] = Field(None, description="Institution location")
    
    # Multilingual fields
    degree_en: str = Field(..., description="Degree in English")
    degree_es: Optional[str] = Field(None, description="Degree in Spanish")
    
    # Date fields
    start_date: datetime = Field(..., description="Start date")
    end_date: Optional[datetime] = Field(None, description="End date (null for ongoing)")
    
    # Display settings
    display_order: Optional[int] = Field(0, description="Display order")
    activo: Optional[bool] = Field(True, description="Whether education is active")


class EducationResponse(EducationBase):
    """Schema for Education API responses."""
    id: int
    created_at: datetime
    language: Optional[str] = 'en'
    available_languages: List[str] = ['en', 'es']

    class Config:
        from_attributes = True
        
    @property
    def degree(self) -> str:
        """Return degree in requested language (fallback to English)."""
        return self.degree_es if self.language == 'es' and self.degree_es else self.degree_en
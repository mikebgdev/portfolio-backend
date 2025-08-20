"""About schemas for API requests and responses."""
from pydantic import BaseModel, validator, Field
from typing import Optional, List
from datetime import datetime, date
import re


class AboutBase(BaseModel):
    """Base schema for About with common fields."""
    name: str = Field(..., min_length=1, max_length=100, description="First name")
    last_name: str = Field(..., min_length=1, max_length=100, description="Last name")
    birth_date: Optional[date] = Field(None, description="Birth date")
    email: str = Field(..., description="Email address")
    location: str = Field(..., min_length=1, max_length=200, description="Location")
    photo_url: Optional[str] = Field(None, description="Photo URL")
    
    # Multilingual fields
    bio_en: str = Field(..., min_length=10, max_length=5000, description="Biography in English")
    bio_es: Optional[str] = Field(None, max_length=5000, description="Biography in Spanish")
    hero_description_en: Optional[str] = Field(None, max_length=500, description="Hero description in English")
    hero_description_es: Optional[str] = Field(None, max_length=500, description="Hero description in Spanish")
    job_title_en: Optional[str] = Field(None, max_length=200, description="Job title in English")
    job_title_es: Optional[str] = Field(None, max_length=200, description="Job title in Spanish")
    nationality_en: str = Field(..., min_length=1, max_length=100, description="Nationality in English")
    nationality_es: Optional[str] = Field(None, max_length=100, description="Nationality in Spanish")

    @validator('email')
    def validate_email(cls, v):
        email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        if not email_pattern.match(v):
            raise ValueError('Invalid email format')
        return v.lower()

    @validator('photo_url')
    def validate_photo_url(cls, v):
        if v and not v.startswith(('http://', 'https://')):
            raise ValueError('Photo URL must start with http:// or https://')
        return v

    @validator('name', 'last_name', 'location', 'nationality_en', 'nationality_es')
    def validate_text_fields(cls, v):
        if v and not v.strip():
            raise ValueError('Field cannot be empty or only whitespace')
        return v.strip() if v else v

    @validator('bio_en', 'bio_es', 'hero_description_en', 'hero_description_es', 'job_title_en', 'job_title_es')
    def validate_content_fields(cls, v):
        if v:
            v = re.sub(r'\s+', ' ', v.strip())
            suspicious_patterns = ['<script', 'javascript:', 'onclick=', 'onerror=']
            for pattern in suspicious_patterns:
                if pattern.lower() in v.lower():
                    raise ValueError(f'Content contains potentially unsafe elements: {pattern}')
        return v


class AboutResponse(AboutBase):
    """Schema for About API responses."""
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    language: Optional[str] = 'en'
    available_languages: List[str] = ['en', 'es']

    class Config:
        from_attributes = True
        
    @property
    def bio(self) -> str:
        """Return bio in requested language (fallback to English)."""
        return self.bio_es if self.language == 'es' and self.bio_es else self.bio_en
    
    @property 
    def nationality(self) -> str:
        """Return nationality in requested language (fallback to English)."""
        return self.nationality_es if self.language == 'es' and self.nationality_es else self.nationality_en
        
    @property
    def hero_description(self) -> Optional[str]:
        """Return hero description in requested language (fallback to English)."""
        if self.language == 'es' and self.hero_description_es:
            return self.hero_description_es
        return self.hero_description_en
        
    @property
    def job_title(self) -> Optional[str]:
        """Return job title in requested language (fallback to English)."""
        if self.language == 'es' and self.job_title_es:
            return self.job_title_es
        return self.job_title_en
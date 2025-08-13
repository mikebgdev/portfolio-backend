from pydantic import BaseModel, HttpUrl, validator, Field
from typing import Optional, List
from datetime import datetime
import re


# Note: Translation schemas removed as we now use direct multilingual fields (_en, _es)


# About Schemas
class AboutBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="First name")
    last_name: str = Field(..., min_length=1, max_length=100, description="Last name")
    birth_month: Optional[int] = Field(None, ge=1, le=12, description="Birth month (1-12)")
    birth_year: Optional[int] = Field(None, ge=1900, le=2100, description="Birth year")
    email: str = Field(..., description="Email address")
    location: str = Field(..., min_length=1, max_length=200, description="Location")
    photo_url: Optional[str] = Field(None, description="Photo URL")
    # Multilingual fields - English required, Spanish optional
    bio_en: str = Field(..., min_length=10, max_length=5000, description="Biography in English")
    bio_es: Optional[str] = Field(None, max_length=5000, description="Biography in Spanish")
    extra_content_en: Optional[str] = Field(None, max_length=2000, description="Extra content in English")
    extra_content_es: Optional[str] = Field(None, max_length=2000, description="Extra content in Spanish")
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

    @validator('bio_en', 'bio_es', 'extra_content_en', 'extra_content_es')
    def validate_content_fields(cls, v):
        if v:
            # Remove excessive whitespace
            v = re.sub(r'\s+', ' ', v.strip())
            # Check for suspicious content
            suspicious_patterns = ['<script', 'javascript:', 'onclick=', 'onerror=']
            for pattern in suspicious_patterns:
                if pattern.lower() in v.lower():
                    raise ValueError(f'Content contains potentially unsafe elements: {pattern}')
        return v


class AboutCreate(AboutBase):
    pass


class AboutUpdate(BaseModel):
    name: Optional[str] = None
    last_name: Optional[str] = None
    birth_month: Optional[int] = None
    birth_year: Optional[int] = None
    email: Optional[str] = None
    location: Optional[str] = None
    photo_url: Optional[str] = None
    # Multilingual fields
    bio_en: Optional[str] = None
    bio_es: Optional[str] = None
    extra_content_en: Optional[str] = None
    extra_content_es: Optional[str] = None
    nationality_en: Optional[str] = None
    nationality_es: Optional[str] = None


class AboutResponse(AboutBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    # Language context for API consumers
    language: Optional[str] = 'en'
    available_languages: List[str] = ['en', 'es']

    class Config:
        from_attributes = True
        
    # Computed properties for language-specific responses
    @property
    def bio(self) -> str:
        """Return bio in requested language (fallback to English)"""
        return self.bio_es if self.language == 'es' and self.bio_es else self.bio_en
    
    @property 
    def nationality(self) -> str:
        """Return nationality in requested language (fallback to English)"""
        return self.nationality_es if self.language == 'es' and self.nationality_es else self.nationality_en
        
    @property
    def extra_content(self) -> Optional[str]:
        """Return extra content in requested language (fallback to English)"""
        if self.language == 'es' and self.extra_content_es:
            return self.extra_content_es
        return self.extra_content_en


# Skill Schemas
class SkillBase(BaseModel):
    # Skill name (no translation needed)
    name: str
    category: str  # 'web_development', 'infrastructure', 'tools', 'learning', 'interpersonal'
    is_in_progress: Optional[bool] = False
    display_order: Optional[int] = 0
    activa: Optional[bool] = True


class SkillCreate(SkillBase):
    pass


class SkillUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    is_in_progress: Optional[bool] = None
    display_order: Optional[int] = None
    activa: Optional[bool] = None


class SkillResponse(SkillBase):
    id: int
    created_at: datetime
    language: Optional[str] = 'en'
    available_languages: List[str] = ['en', 'es']

    class Config:
        from_attributes = True


# Project Schemas
class ProjectBase(BaseModel):
    # Multilingual fields
    title_en: str = Field(..., min_length=1, max_length=200, description="Project title in English")
    title_es: Optional[str] = Field(None, max_length=200, description="Project title in Spanish")
    description_en: str = Field(..., min_length=10, max_length=2000, description="Project description in English")
    description_es: Optional[str] = Field(None, max_length=2000, description="Project description in Spanish")
    # Non-translatable fields
    image_url: Optional[str] = Field(None, description="Project image URL")
    technologies: str = Field(..., min_length=1, max_length=500, description="Technologies used (comma-separated)")
    source_url: Optional[str] = Field(None, description="Source code URL")
    demo_url: Optional[str] = Field(None, description="Live demo URL")
    display_order: Optional[int] = Field(0, ge=0, le=1000, description="Display order")
    activa: Optional[bool] = Field(True, description="Whether project is active")

    @validator('image_url', 'source_url', 'demo_url')
    def validate_urls(cls, v):
        if v and not v.startswith(('http://', 'https://')):
            raise ValueError('URL must start with http:// or https://')
        return v

    @validator('technologies')
    def validate_technologies(cls, v):
        if not v or not v.strip():
            raise ValueError('Technologies cannot be empty')
        # Clean up technologies list
        techs = [tech.strip() for tech in v.split(',') if tech.strip()]
        if not techs:
            raise ValueError('At least one technology must be specified')
        return ', '.join(techs)

    @validator('title_en', 'title_es')
    def validate_titles(cls, v):
        if v:
            v = v.strip()
            if not v:
                raise ValueError('Title cannot be empty or only whitespace')
            # Check for suspicious content
            suspicious_patterns = ['<', '>', 'script', 'javascript:']
            for pattern in suspicious_patterns:
                if pattern.lower() in v.lower():
                    raise ValueError(f'Title contains invalid characters: {pattern}')
        return v

    @validator('description_en', 'description_es')
    def validate_descriptions(cls, v):
        if v:
            v = re.sub(r'\s+', ' ', v.strip())
            # Check for suspicious content
            suspicious_patterns = ['<script', 'javascript:', 'onclick=', 'onerror=']
            for pattern in suspicious_patterns:
                if pattern.lower() in v.lower():
                    raise ValueError(f'Description contains potentially unsafe elements: {pattern}')
        return v


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    title_en: Optional[str] = None
    title_es: Optional[str] = None
    description_en: Optional[str] = None
    description_es: Optional[str] = None
    image_url: Optional[str] = None
    technologies: Optional[str] = None
    source_url: Optional[str] = None
    demo_url: Optional[str] = None
    display_order: Optional[int] = None
    activa: Optional[bool] = None


class ProjectResponse(ProjectBase):
    id: int
    created_at: datetime
    language: Optional[str] = 'en'
    available_languages: List[str] = ['en', 'es']

    class Config:
        from_attributes = True
        
    @property
    def title(self) -> str:
        """Return project title in requested language (fallback to English)"""
        return self.title_es if self.language == 'es' and self.title_es else self.title_en
        
    @property
    def description(self) -> str:
        """Return project description in requested language (fallback to English)"""
        return self.description_es if self.language == 'es' and self.description_es else self.description_en


# Experience Schemas
class ExperienceBase(BaseModel):
    company: str
    # Multilingual fields
    position_en: str
    position_es: Optional[str] = None
    description_en: str
    description_es: Optional[str] = None
    # Non-translatable fields
    start_date: datetime
    end_date: Optional[datetime] = None
    location: Optional[str] = None
    display_order: Optional[int] = 0
    activo: Optional[bool] = True


class ExperienceCreate(ExperienceBase):
    pass


class ExperienceUpdate(BaseModel):
    company: Optional[str] = None
    position_en: Optional[str] = None
    position_es: Optional[str] = None
    description_en: Optional[str] = None
    description_es: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    location: Optional[str] = None
    display_order: Optional[int] = None
    activo: Optional[bool] = None


class ExperienceResponse(ExperienceBase):
    id: int
    created_at: datetime
    language: Optional[str] = 'en'
    available_languages: List[str] = ['en', 'es']

    class Config:
        from_attributes = True
        
    @property
    def position(self) -> str:
        """Return position in requested language (fallback to English)"""
        return self.position_es if self.language == 'es' and self.position_es else self.position_en
        
    @property
    def description(self) -> str:
        """Return description in requested language (fallback to English)"""
        return self.description_es if self.language == 'es' and self.description_es else self.description_en


# Education Schemas
class EducationBase(BaseModel):
    institution: str
    # Multilingual fields
    degree_en: str
    degree_es: Optional[str] = None
    field_of_study_en: Optional[str] = None
    field_of_study_es: Optional[str] = None
    description_en: Optional[str] = None
    description_es: Optional[str] = None
    # Non-translatable fields
    start_date: datetime
    end_date: Optional[datetime] = None
    location: Optional[str] = None
    display_order: Optional[int] = 0
    activo: Optional[bool] = True


class EducationCreate(EducationBase):
    pass


class EducationUpdate(BaseModel):
    institution: Optional[str] = None
    degree_en: Optional[str] = None
    degree_es: Optional[str] = None
    field_of_study_en: Optional[str] = None
    field_of_study_es: Optional[str] = None
    description_en: Optional[str] = None
    description_es: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    location: Optional[str] = None
    display_order: Optional[int] = None
    activo: Optional[bool] = None


class EducationResponse(EducationBase):
    id: int
    created_at: datetime
    language: Optional[str] = 'en'
    available_languages: List[str] = ['en', 'es']

    class Config:
        from_attributes = True
        
    @property
    def degree(self) -> str:
        """Return degree in requested language (fallback to English)"""
        return self.degree_es if self.language == 'es' and self.degree_es else self.degree_en
        
    @property
    def field_of_study(self) -> Optional[str]:
        """Return field of study in requested language (fallback to English)"""
        if self.language == 'es' and self.field_of_study_es:
            return self.field_of_study_es
        return self.field_of_study_en
        
    @property
    def description(self) -> Optional[str]:
        """Return description in requested language (fallback to English)"""
        if self.language == 'es' and self.description_es:
            return self.description_es
        return self.description_en


# Contact Schemas
class ContactBase(BaseModel):
    email: str
    phone: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    twitter_url: Optional[str] = None
    instagram_url: Optional[str] = None
    contact_form_enabled: Optional[bool] = True
    # Multilingual contact message
    contact_message_en: Optional[str] = None
    contact_message_es: Optional[str] = None
    # CV file
    cv_file_url: Optional[str] = None


class ContactCreate(ContactBase):
    pass


class ContactUpdate(BaseModel):
    email: Optional[str] = None
    phone: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    twitter_url: Optional[str] = None
    instagram_url: Optional[str] = None
    contact_form_enabled: Optional[bool] = None
    contact_message_en: Optional[str] = None
    contact_message_es: Optional[str] = None
    cv_file_url: Optional[str] = None


class ContactResponse(ContactBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    language: Optional[str] = 'en'
    available_languages: List[str] = ['en', 'es']

    class Config:
        from_attributes = True
        
    @property
    def contact_message(self) -> Optional[str]:
        """Return contact message in requested language (fallback to English)"""
        if self.language == 'es' and self.contact_message_es:
            return self.contact_message_es
        return self.contact_message_en
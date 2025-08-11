from pydantic import BaseModel, HttpUrl
from typing import Optional, List
from datetime import datetime


# Note: Translation schemas removed as we now use direct multilingual fields (_en, _es)


# About Schemas
class AboutBase(BaseModel):
    name: str
    last_name: str
    birth_month: Optional[int] = None
    birth_year: Optional[int] = None
    email: str
    location: str
    photo_url: Optional[str] = None
    # Multilingual fields - English required, Spanish optional
    bio_en: str
    bio_es: Optional[str] = None
    extra_content_en: Optional[str] = None
    extra_content_es: Optional[str] = None
    nationality_en: str
    nationality_es: Optional[str] = None


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

    class Config:
        from_attributes = True


# Project Schemas
class ProjectBase(BaseModel):
    # Multilingual fields
    title_en: str
    title_es: Optional[str] = None
    description_en: str
    description_es: Optional[str] = None
    # Non-translatable fields
    image_url: Optional[str] = None
    technologies: str
    source_url: Optional[str] = None
    demo_url: Optional[str] = None
    display_order: Optional[int] = 0
    activa: Optional[bool] = True


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
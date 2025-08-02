from pydantic import BaseModel, HttpUrl
from typing import Optional, List
from datetime import datetime


# About Schemas
class AboutBase(BaseModel):
    content: str
    photo_url: Optional[HttpUrl] = None


class AboutCreate(AboutBase):
    pass


class AboutUpdate(BaseModel):
    content: Optional[str] = None
    photo_url: Optional[HttpUrl] = None


class AboutResponse(AboutBase):
    id: int
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Skill Schemas
class SkillBase(BaseModel):
    name: str
    type: str  # 'technical' or 'interpersonal'
    level: Optional[int] = 1


class SkillCreate(SkillBase):
    pass


class SkillUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    level: Optional[int] = None


class SkillResponse(SkillBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Project Schemas
class ProjectBase(BaseModel):
    name: str
    description: str
    github_url: HttpUrl
    demo_url: Optional[HttpUrl] = None
    technologies: Optional[str] = None  # JSON string
    image_url: Optional[HttpUrl] = None


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    github_url: Optional[HttpUrl] = None
    demo_url: Optional[HttpUrl] = None
    technologies: Optional[str] = None
    image_url: Optional[HttpUrl] = None


class ProjectResponse(ProjectBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Experience Schemas
class ExperienceBase(BaseModel):
    company: str
    position: str
    description: Optional[str] = None
    start_date: datetime
    end_date: Optional[datetime] = None
    location: Optional[str] = None


class ExperienceCreate(ExperienceBase):
    pass


class ExperienceUpdate(BaseModel):
    company: Optional[str] = None
    position: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    location: Optional[str] = None


class ExperienceResponse(ExperienceBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Education Schemas
class EducationBase(BaseModel):
    institution: str
    degree: str
    field_of_study: Optional[str] = None
    description: Optional[str] = None
    start_date: datetime
    end_date: Optional[datetime] = None
    location: Optional[str] = None
    gpa: Optional[str] = None


class EducationCreate(EducationBase):
    pass


class EducationUpdate(BaseModel):
    institution: Optional[str] = None
    degree: Optional[str] = None
    field_of_study: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    location: Optional[str] = None
    gpa: Optional[str] = None


class EducationResponse(EducationBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class About(Base):
    __tablename__ = "about"

    id = Column(Integer, primary_key=True, index=True)
    
    # Personal Information
    name = Column(String(100), nullable=False)  # Nombre
    last_name = Column(String(100), nullable=False)  # Apellidos
    birth_date = Column(Date, nullable=True)  # Fecha de nacimiento (unificado mes y año)
    email = Column(String(255), nullable=False)  # Email
    location = Column(String(200), nullable=False)  # Ubicación
    photo_url = Column(String(500), nullable=True)  # Foto
    
    # Biography content - Direct translation approach (English + Spanish)
    bio_en = Column(Text, nullable=False)  # English bio
    bio_es = Column(Text, nullable=True)   # Spanish bio
    
    # Hero section description - For homepage hero section
    hero_description_en = Column(Text, nullable=True)  # English hero description
    hero_description_es = Column(Text, nullable=True)  # Spanish hero description
    
    # Job title - Current position
    job_title_en = Column(String(200), nullable=True)  # English job title
    job_title_es = Column(String(200), nullable=True)  # Spanish job title
    
    # Nationality (nacionalidad)
    nationality_en = Column(String(100), nullable=False, server_default='Spanish')  # English nationality
    nationality_es = Column(String(100), nullable=True, server_default='Español')   # Spanish nationality
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    


class SkillCategory(Base):
    __tablename__ = "skill_categories"

    id = Column(Integer, primary_key=True, index=True)
    
    # Category identifier (unique slug)
    slug = Column(String(100), unique=True, nullable=False, index=True)  # e.g., 'web', 'tools'
    
    # Translatable fields - Direct translation approach
    label_en = Column(String(200), nullable=False)  # English category name
    label_es = Column(String(200), nullable=True)   # Spanish category name
    
    # UI properties
    icon_name = Column(String(100), nullable=False)  # Icon name for frontend (e.g., 'Globe', 'Wrench')
    display_order = Column(Integer, default=0)  # For ordering categories
    active = Column(Boolean, default=True)  # Active/inactive category
    
    # Relationship to skills
    skills = relationship("Skill", back_populates="skill_category", cascade="all, delete-orphan")
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __str__(self):
        """String representation for admin interface"""
        return f"{self.label_en} ({self.slug})"


class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, index=True)
    
    # Translatable skill name - Direct translation approach
    name_en = Column(String(200), nullable=False)  # English skill name
    name_es = Column(String(200), nullable=True)   # Spanish skill name
    
    # Foreign key to skill category
    category_id = Column(Integer, ForeignKey("skill_categories.id"), nullable=True)  # Temporarily nullable for testing
    skill_category = relationship("SkillCategory", back_populates="skills")
    
    # UI properties
    icon_name = Column(String(100), nullable=False)  # Icon name for frontend (e.g., 'Code', 'Server')
    color = Column(String(50), nullable=True)  # CSS color class (e.g., 'text-cyan-500')
    
    # Status and ordering
    display_order = Column(Integer, default=0)  # For ordering within category
    active = Column(Boolean, default=True)  # Active/inactive skill
    
    # Removed custom __init__ as it can cause issues with SQLAdmin forms
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    
    # Project info - Direct translation approach
    title_en = Column(String(200), nullable=False)  # English title
    title_es = Column(String(200), nullable=True)   # Spanish title
    description_en = Column(Text, nullable=False)  # English description  
    description_es = Column(Text, nullable=True)   # Spanish description
    
    # Visual (no translation needed)
    image_url = Column(String(500), nullable=True)  # Project image
    
    # Technology stack (no translation needed)
    technologies = Column(Text, nullable=False)  # Comma-separated or JSON
    
    # Links (no translation needed)
    source_url = Column(String(500), nullable=True)  # Source code link
    demo_url = Column(String(500), nullable=True)  # Demo link
    
    # Display (no translation needed)
    display_order = Column(Integer, default=0)  # For ordering projects
    activa = Column(Boolean, default=True)  # Para filtrar en el frontend
    
    # Removed custom __init__ as it can cause issues with SQLAdmin forms
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    


class Experience(Base):
    __tablename__ = "experience"

    id = Column(Integer, primary_key=True, index=True)
    company = Column(String(200), nullable=False)  # Company name - No translation needed
    
    # Translatable fields - Direct translation approach
    position_en = Column(String(200), nullable=False)  # English job title
    position_es = Column(String(200), nullable=True)   # Spanish job title
    description_en = Column(Text, nullable=False)  # English job responsibilities
    description_es = Column(Text, nullable=True)   # Spanish job responsibilities
    
    # Dates (no translation needed)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True)  # NULL for current position
    
    # Location and ordering (no translation needed)
    location = Column(String(200), nullable=True)
    display_order = Column(Integer, default=0)  # For ordering experiences
    activo = Column(Boolean, default=True)  # Para filtrar en el frontend
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    


class Education(Base):
    __tablename__ = "education"

    id = Column(Integer, primary_key=True, index=True)
    institution = Column(String(200), nullable=False)  # Institution name - No translation needed
    
    # Translatable fields - Direct translation approach
    degree_en = Column(String(200), nullable=False)  # English degree/course title
    degree_es = Column(String(200), nullable=True)   # Spanish degree/course title
    field_of_study_en = Column(String(200), nullable=True)  # English field of study
    field_of_study_es = Column(String(200), nullable=True)  # Spanish field of study
    description_en = Column(Text, nullable=True)  # English description
    description_es = Column(Text, nullable=True)  # Spanish description
    
    # Dates (no translation needed)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True)  # NULL for ongoing
    
    # Additional info and ordering (no translation needed)
    location = Column(String(200), nullable=True)
    display_order = Column(Integer, default=0)  # For ordering education entries
    activo = Column(Boolean, default=True)  # Para filtrar en el frontend
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    


class Contact(Base):
    __tablename__ = "contact"

    id = Column(Integer, primary_key=True, index=True)
    
    # Contact Methods (no translation needed)
    email = Column(String(255), nullable=False)  # Primary contact email
    phone = Column(String(50), nullable=True)  # Phone number
    
    # Social Media Links (no translation needed)
    linkedin_url = Column(String(500), nullable=True)  # LinkedIn profile
    github_url = Column(String(500), nullable=True)  # GitHub profile
    twitter_url = Column(String(500), nullable=True)  # Twitter profile
    instagram_url = Column(String(500), nullable=True)  # Instagram profile
    
    # Contact Form Settings (no translation needed)
    contact_form_enabled = Column(Boolean, default=True)  # Enable/disable contact form
    
    # Translatable content - Direct translation approach
    contact_message_en = Column(Text, nullable=True)  # English contact message
    contact_message_es = Column(Text, nullable=True)  # Spanish contact message
    
    # CV/Resume file
    cv_file_url = Column(String(500), nullable=True)  # URL to CV file
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    

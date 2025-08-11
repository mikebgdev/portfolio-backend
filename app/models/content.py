from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class About(Base):
    __tablename__ = "about"

    id = Column(Integer, primary_key=True, index=True)
    
    # Personal Information
    name = Column(String, nullable=False)  # Nombre
    last_name = Column(String, nullable=False)  # Apellidos
    birth_month = Column(Integer, nullable=True)  # Mes de nacimiento (1-12)
    birth_year = Column(Integer, nullable=True)  # Año de nacimiento
    email = Column(String, nullable=False)  # Email
    location = Column(String, nullable=False)  # Ubicación
    photo_url = Column(String, nullable=True)  # Foto
    
    # Content fields - Direct translation approach (English + Spanish)
    # Bio/Description (biografía o contenido/descripción)
    bio_en = Column(Text, nullable=False)  # English bio
    bio_es = Column(Text, nullable=True)   # Spanish bio
    
    # Extra content (contenido extra opcional)
    extra_content_en = Column(Text, nullable=True)  # English extra content
    extra_content_es = Column(Text, nullable=True)  # Spanish extra content
    
    # Nationality (nacionalidad)
    nationality_en = Column(String, nullable=False, server_default='Spanish')  # English nationality
    nationality_es = Column(String, nullable=True, server_default='Español')   # Spanish nationality
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    


class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, index=True)
    
    # Skill name (no translation needed)
    name = Column(String, nullable=False)  # Skill name
    
    # Categories from mikebgdev.com (no translation needed)
    category = Column(String, nullable=False)  # 'web_development', 'infrastructure', 'tools', 'learning', 'interpersonal'
    
    def __init__(self, **kwargs):
        # Ensure default values are set immediately
        if 'is_in_progress' not in kwargs:
            kwargs['is_in_progress'] = False
        if 'display_order' not in kwargs:
            kwargs['display_order'] = 0
        if 'activa' not in kwargs:
            kwargs['activa'] = True
        super().__init__(**kwargs)
    
    # Status and ordering (no translation needed)
    is_in_progress = Column(Boolean, default=False)  # For "Learning/In Progress" skills
    display_order = Column(Integer, default=0)  # For ordering within category
    activa = Column(Boolean, default=True)  # Para filtrar en el frontend
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    
    # Project info - Direct translation approach
    title_en = Column(String, nullable=False)  # English title
    title_es = Column(String, nullable=True)   # Spanish title
    description_en = Column(Text, nullable=False)  # English description  
    description_es = Column(Text, nullable=True)   # Spanish description
    
    # Visual (no translation needed)
    image_url = Column(String, nullable=True)  # Project image
    
    # Technology stack (no translation needed)
    technologies = Column(Text, nullable=False)  # Comma-separated or JSON
    
    # Links (no translation needed)
    source_url = Column(String, nullable=True)  # Source code link
    demo_url = Column(String, nullable=True)  # Demo link
    
    # Display (no translation needed)
    display_order = Column(Integer, default=0)  # For ordering projects
    activa = Column(Boolean, default=True)  # Para filtrar en el frontend
    
    def __init__(self, **kwargs):
        # Ensure default values are set immediately
        if 'display_order' not in kwargs:
            kwargs['display_order'] = 0
        if 'activa' not in kwargs:
            kwargs['activa'] = True
        super().__init__(**kwargs)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    


class Experience(Base):
    __tablename__ = "experience"

    id = Column(Integer, primary_key=True, index=True)
    company = Column(String, nullable=False)  # Company name - No translation needed
    
    # Translatable fields - Direct translation approach
    position_en = Column(String, nullable=False)  # English job title
    position_es = Column(String, nullable=True)   # Spanish job title
    description_en = Column(Text, nullable=False)  # English job responsibilities
    description_es = Column(Text, nullable=True)   # Spanish job responsibilities
    
    # Dates (no translation needed)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True)  # NULL for current position
    
    # Location and ordering (no translation needed)
    location = Column(String, nullable=True)
    display_order = Column(Integer, default=0)  # For ordering experiences
    activo = Column(Boolean, default=True)  # Para filtrar en el frontend
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    


class Education(Base):
    __tablename__ = "education"

    id = Column(Integer, primary_key=True, index=True)
    institution = Column(String, nullable=False)  # Institution name - No translation needed
    
    # Translatable fields - Direct translation approach
    degree_en = Column(String, nullable=False)  # English degree/course title
    degree_es = Column(String, nullable=True)   # Spanish degree/course title
    field_of_study_en = Column(String, nullable=True)  # English field of study
    field_of_study_es = Column(String, nullable=True)  # Spanish field of study
    description_en = Column(Text, nullable=True)  # English description
    description_es = Column(Text, nullable=True)  # Spanish description
    
    # Dates (no translation needed)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True)  # NULL for ongoing
    
    # Additional info and ordering (no translation needed)
    location = Column(String, nullable=True)
    display_order = Column(Integer, default=0)  # For ordering education entries
    activo = Column(Boolean, default=True)  # Para filtrar en el frontend
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    


class Contact(Base):
    __tablename__ = "contact"

    id = Column(Integer, primary_key=True, index=True)
    
    # Contact Methods (no translation needed)
    email = Column(String, nullable=False)  # Primary contact email
    phone = Column(String, nullable=True)  # Phone number
    
    # Social Media Links (no translation needed)
    linkedin_url = Column(String, nullable=True)  # LinkedIn profile
    github_url = Column(String, nullable=True)  # GitHub profile
    twitter_url = Column(String, nullable=True)  # Twitter profile
    instagram_url = Column(String, nullable=True)  # Instagram profile
    
    # Contact Form Settings (no translation needed)
    contact_form_enabled = Column(Boolean, default=True)  # Enable/disable contact form
    
    # Translatable content - Direct translation approach
    contact_message_en = Column(Text, nullable=True)  # English contact message
    contact_message_es = Column(Text, nullable=True)  # Spanish contact message
    
    # CV/Resume file
    cv_file_url = Column(String, nullable=True)  # URL to CV file
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    

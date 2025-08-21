"""About model for personal information."""
from sqlalchemy import Column, Integer, String, Text, DateTime, Date
from sqlalchemy.sql import func
from app.database import Base


class About(Base):
    """Model for personal information and biography."""
    __tablename__ = "about"

    id = Column(Integer, primary_key=True, index=True)
    
    # Personal Information
    name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    birth_date = Column(Date, nullable=True)
    email = Column(String(255), nullable=False)
    location = Column(String(200), nullable=False)
    photo_url = Column(String(500), nullable=True)  # Keep as backup
    photo_file = Column(String(500), nullable=True)  # File upload path
    
    # Multilingual Biography
    bio_en = Column(Text, nullable=False)
    bio_es = Column(Text, nullable=True)
    
    # Hero Section
    hero_description_en = Column(Text, nullable=True)
    hero_description_es = Column(Text, nullable=True)
    
    # Job Title
    job_title_en = Column(String(200), nullable=True)
    job_title_es = Column(String(200), nullable=True)
    
    # Nationality
    nationality_en = Column(String(100), nullable=False, server_default='Spanish')
    nationality_es = Column(String(100), nullable=True, server_default='Español')
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __str__(self):
        """String representation for admin interface."""
        return f"{self.name} {self.last_name}"
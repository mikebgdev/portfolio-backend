"""Projects model for portfolio projects."""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.sql import func
from app.database import Base


class Project(Base):
    """Model for portfolio projects."""
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    
    # Multilingual project information
    title_en = Column(String(200), nullable=False)
    title_es = Column(String(200), nullable=True)
    description_en = Column(Text, nullable=False)
    description_es = Column(Text, nullable=True)
    
    # Visual and technical details
    image_url = Column(String(500), nullable=True)
    technologies = Column(Text, nullable=False)  # Comma-separated or JSON
    
    # Project links
    source_url = Column(String(500), nullable=True)
    demo_url = Column(String(500), nullable=True)
    
    # Display settings
    display_order = Column(Integer, default=0)
    activa = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __str__(self):
        """String representation for admin interface."""
        return f"{self.title_en}"
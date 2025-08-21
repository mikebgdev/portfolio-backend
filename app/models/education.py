"""Education model for educational background."""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.sql import func
from app.database import Base


class Education(Base):
    """Model for education entries."""
    __tablename__ = "education"

    id = Column(Integer, primary_key=True, index=True)
    
    # Institution information
    institution = Column(String(200), nullable=False)
    location = Column(String(200), nullable=True)
    
    # Multilingual degree information
    degree_en = Column(String(200), nullable=False)
    degree_es = Column(String(200), nullable=True)
    
    # Date range
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True)  # NULL for ongoing
    
    # Display settings
    display_order = Column(Integer, default=0)
    activo = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __str__(self):
        """String representation for admin interface."""
        return f"{self.degree_en} at {self.institution}"
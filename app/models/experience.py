"""Experience model for work experience."""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.sql import func
from app.database import Base


class Experience(Base):
    """Model for work experience entries."""
    __tablename__ = "experience"

    id = Column(Integer, primary_key=True, index=True)
    
    # Company information
    company = Column(String(200), nullable=False)
    location = Column(String(200), nullable=True)
    
    # Multilingual position information
    position_en = Column(String(200), nullable=False)
    position_es = Column(String(200), nullable=True)
    description_en = Column(Text, nullable=False)
    description_es = Column(Text, nullable=True)
    
    # Date range
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True)  # NULL for current position
    
    # Display settings
    display_order = Column(Integer, default=0)
    activo = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __str__(self):
        """String representation for admin interface."""
        return f"{self.position_en} at {self.company}"
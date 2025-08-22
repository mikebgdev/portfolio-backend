"""Contact model for contact information and social media."""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.sql import func
from app.database import Base


class Contact(Base):
    """Model for contact information and social media links."""
    __tablename__ = "contact"

    id = Column(Integer, primary_key=True, index=True)
    
    # Contact Methods
    email = Column(String(255), nullable=False)
    
    # Social Media Links
    linkedin_url = Column(String(500), nullable=True)
    github_url = Column(String(500), nullable=True)
    
    # Contact Form Settings
    contact_form_enabled = Column(Boolean, default=True)
    
    # Multilingual Contact Messages
    contact_message_en = Column(Text, nullable=True)
    contact_message_es = Column(Text, nullable=True)
    
    # CV/Resume
    cv_file = Column(String(500), nullable=True)  # File upload path
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __str__(self):
        """String representation for admin interface."""
        return f"Contact Info - {self.email}"
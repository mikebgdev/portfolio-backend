"""Contact service for handling contact information operations."""
from sqlalchemy.orm import Session
from app.models.contact import Contact
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class ContactService:
    """Service for managing Contact information."""
    
    def get_contact(self, db: Session) -> Optional[Contact]:
        """Get contact section content."""
        return db.query(Contact).first()


# Global service instance
contact_service = ContactService()
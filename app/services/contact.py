"""Contact service for handling contact information operations."""
from sqlalchemy.orm import Session
from app.models.contact import Contact
from app.utils.file_utils import encode_file_to_base64
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class ContactService:
    """Service for managing Contact information."""
    
    def get_contact(self, db: Session) -> Optional[Contact]:
        """Get contact section content."""
        contact = db.query(Contact).first()
        if contact:
            # Add CV data if cv_file exists
            if hasattr(contact, 'cv_file') and contact.cv_file:
                contact.cv_data = encode_file_to_base64(contact.cv_file)
            else:
                contact.cv_data = None
        return contact


# Global service instance
contact_service = ContactService()
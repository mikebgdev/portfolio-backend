"""Contact service for handling contact information operations."""
from sqlalchemy.orm import Session

from app.models.contact import Contact
from app.services.base import SingletonService


class ContactService(SingletonService[Contact]):
    """Service for managing contact information."""
    
    def __init__(self):
        super().__init__(Contact)
    
    def get_contact(self, db: Session) -> Contact:
        """Get contact information."""
        return self.get_or_404(db)


# Global service instance
contact_service = ContactService()
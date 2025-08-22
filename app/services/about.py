"""About service for handling personal information operations."""
from sqlalchemy.orm import Session

from app.models.about import About
from app.services.base import SingletonService


class AboutService(SingletonService[About]):
    """Service for managing About/personal information."""
    
    def __init__(self):
        super().__init__(About)
    
    def get_about(self, db: Session) -> About:
        """Get about section content."""
        return self.get_or_404(db)


# Global service instance
about_service = AboutService()
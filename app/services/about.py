"""About service for handling personal information operations."""
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.models.about import About
from app.exceptions import DatabaseError
from app.utils.cache import cache_manager
from app.utils.file_utils import encode_file_to_base64
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class AboutService:
    """Service for managing About/personal information."""
    
    def get_about(self, db: Session) -> Optional[About]:
        """Get about section content."""
        about = db.query(About).first()
        if about:
            # Add photo data if photo_file exists
            if hasattr(about, 'photo_file') and about.photo_file:
                about.photo_data = encode_file_to_base64(about.photo_file)
            else:
                about.photo_data = None
        return about

    async def _invalidate_about_cache(self):
        """Invalidate all cached about endpoints."""
        try:
            cache_keys = [
                "http_cache:/api/v1/about:",
                "http_cache:/api/v1/about/:",
            ]
            
            for key_pattern in cache_keys:
                for lang in ["", "lang=en", "lang=es"]:
                    cache_key = f"{key_pattern}{lang}"
                    await cache_manager.delete(cache_key)
            
            logger.info("About cache invalidated successfully")
        except Exception as e:
            logger.warning(f"Failed to invalidate about cache: {str(e)}")


# Global service instance
about_service = AboutService()
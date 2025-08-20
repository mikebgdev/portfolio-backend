"""About service for handling personal information operations."""
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.models.about import About
from app.exceptions import DatabaseError
from app.utils.cache import cache_manager
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class AboutService:
    """Service for managing About/personal information."""
    
    def get_about(self, db: Session) -> Optional[About]:
        """Get about section content."""
        return db.query(About).first()

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
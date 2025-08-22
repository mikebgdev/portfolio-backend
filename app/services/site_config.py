"""
Site Configuration service for Portfolio Backend API.
"""

import logging
from typing import Optional

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.exceptions import ContentNotFoundError, DatabaseError, ValidationError
from app.models.site_config import SiteConfig
from app.schemas.site_config import SiteConfigCreate, SiteConfigUpdate
from app.utils.cache import ContentCache, cached
from app.utils.file_utils import encode_file_to_base64

logger = logging.getLogger(__name__)


class SiteConfigService:
    def get_site_config(self, db: Session) -> Optional[SiteConfig]:
        """Get site configuration (there should be only one record)."""
        site_config = db.query(SiteConfig).first()
        if site_config:
            # Add file data if files exist
            if hasattr(site_config, "favicon_file") and site_config.favicon_file:
                site_config.favicon_data = encode_file_to_base64(
                    site_config.favicon_file
                )
            else:
                site_config.favicon_data = None

            if hasattr(site_config, "og_image_file") and site_config.og_image_file:
                site_config.og_image_data = encode_file_to_base64(
                    site_config.og_image_file
                )
            else:
                site_config.og_image_data = None

            if (
                hasattr(site_config, "twitter_image_file")
                and site_config.twitter_image_file
            ):
                site_config.twitter_image_data = encode_file_to_base64(
                    site_config.twitter_image_file
                )
            else:
                site_config.twitter_image_data = None

        return site_config

    def create_site_config(
        self, db: Session, site_config_data: SiteConfigCreate
    ) -> SiteConfig:
        """Create site configuration."""
        try:
            # Ensure only one site config exists
            existing = db.query(SiteConfig).first()
            if existing:
                raise ValidationError(
                    "Site configuration already exists. Use update instead."
                )

            site_config = SiteConfig(**site_config_data.dict())
            db.add(site_config)
            db.commit()
            db.refresh(site_config)

            # Clear any cached site config
            ContentCache.invalidate_content_cache("site_config")

            logger.info(f"Site configuration created: {site_config.site_title}")
            return site_config

        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error creating site config: {str(e)}")
            raise DatabaseError(f"Database error: {str(e)}")

    def update_site_config(
        self, db: Session, site_config_data: SiteConfigUpdate
    ) -> SiteConfig:
        """Update site configuration."""
        try:
            site_config = db.query(SiteConfig).first()
            if not site_config:
                raise ContentNotFoundError("site_config", 0)

            # Update fields that are provided
            update_data = site_config_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(site_config, field, value)

            db.commit()
            db.refresh(site_config)

            # Clear cached site config
            ContentCache.invalidate_content_cache("site_config")

            logger.info(f"Site configuration updated: {site_config.site_title}")
            return site_config

        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error updating site config: {str(e)}")
            raise DatabaseError(f"Database error: {str(e)}")

    def delete_site_config(self, db: Session) -> None:
        """Delete site configuration."""
        try:
            site_config = db.query(SiteConfig).first()
            if not site_config:
                raise ContentNotFoundError("site_config", 0)

            db.delete(site_config)
            db.commit()

            # Clear cached site config
            ContentCache.invalidate_content_cache("site_config")

            logger.info("Site configuration deleted")

        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error deleting site config: {str(e)}")
            raise DatabaseError(f"Database error: {str(e)}")

    @cached(ttl=3600, key_prefix="site_config")  # Cache for 1 hour
    async def get_cached_site_config(self, db: Session) -> Optional[SiteConfig]:
        """Get cached site configuration."""
        return self.get_site_config(db)


# Global service instance
site_config_service = SiteConfigService()

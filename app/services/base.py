"""Base service class for common service patterns."""

import logging
from abc import ABC
from typing import Generic, List, Optional, Type, TypeVar

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database import Base
from app.exceptions import ContentNotFoundError, DatabaseError
from app.utils.cache import cache_manager
from app.utils.file_utils import encode_file_to_base64

T = TypeVar("T", bound=Base)

logger = logging.getLogger(__name__)


class BaseService(Generic[T], ABC):
    """Base service class with common CRUD operations and caching."""

    def __init__(self, model: Type[T]):
        self.model = model
        self.model_name = model.__name__.lower()

    def get_by_id(self, db: Session, id: int) -> Optional[T]:
        """Get a record by ID."""
        try:
            return db.query(self.model).filter(self.model.id == id).first()
        except SQLAlchemyError as e:
            logger.error(f"Database error in {self.model_name} get_by_id: {str(e)}")
            raise DatabaseError(f"Failed to fetch {self.model_name}")

    def get_all_active(self, db: Session) -> List[T]:
        """Get all active records, ordered appropriately."""
        try:
            query = db.query(self.model)

            # Add active filter if model has active field
            if hasattr(self.model, "activo"):
                query = query.filter(self.model.activo.is_(True))
            elif hasattr(self.model, "activa"):
                query = query.filter(self.model.activa.is_(True))

            # Add ordering
            query = self._apply_default_ordering(query)

            return query.all()
        except SQLAlchemyError as e:
            logger.error(
                f"Database error in {self.model_name} get_all_active: {str(e)}"
            )
            raise DatabaseError(f"Failed to fetch {self.model_name} records")

    def get_first(self, db: Session) -> Optional[T]:
        """Get the first record (for singleton models like About, Contact)."""
        try:
            return db.query(self.model).first()
        except SQLAlchemyError as e:
            logger.error(f"Database error in {self.model_name} get_first: {str(e)}")
            raise DatabaseError(f"Failed to fetch {self.model_name}")

    def _apply_default_ordering(self, query):
        """Apply default ordering to query. Override in subclasses."""
        # Try display_order first
        if hasattr(self.model, "display_order"):
            query = query.order_by(self.model.display_order)

        # For date-based models, prioritize ongoing (null end_date) then recent
        if hasattr(self.model, "end_date") and hasattr(self.model, "start_date"):
            query = query.order_by(
                self.model.end_date.is_(None).desc(),  # Ongoing first
                self.model.end_date.desc().nullslast(),  # Most recent end_date
                self.model.start_date.desc(),  # Most recent start_date as tiebreaker
            )
        elif hasattr(self.model, "created_at"):
            query = query.order_by(self.model.created_at.desc())

        return query

    def add_file_data(self, record: T, file_fields: List[str] = None) -> T:
        """Add Base64 file data to record for specified file fields."""
        if not record:
            return record

        # Auto-detect file fields if not specified
        if file_fields is None:
            file_fields = [
                attr
                for attr in dir(record)
                if attr.endswith("_file") and not attr.startswith("_")
            ]

        for field in file_fields:
            if hasattr(record, field):
                file_path = getattr(record, field)
                if file_path:
                    data_field = field.replace("_file", "_data")
                    setattr(record, data_field, encode_file_to_base64(file_path))
                else:
                    data_field = field.replace("_file", "_data")
                    setattr(record, data_field, None)

        return record

    async def invalidate_cache_pattern(self, pattern: str):
        """Invalidate cache entries matching a pattern."""
        try:
            cache_keys = [
                f"http_cache:/api/v1/{pattern}:",
                f"http_cache:/api/v1/{pattern}/:",
            ]

            for key_pattern in cache_keys:
                for lang in ["", "lang=en", "lang=es"]:
                    cache_key = f"{key_pattern}{lang}"
                    await cache_manager.delete(cache_key)

            logger.info(f"{self.model_name} cache invalidated successfully")
        except Exception as e:
            logger.warning(f"Failed to invalidate {self.model_name} cache: {str(e)}")


class SingletonService(BaseService[T]):
    """Service for singleton models (About, Contact, SiteConfig)."""

    def get(self, db: Session) -> Optional[T]:
        """Get the singleton record."""
        record = self.get_first(db)
        if record:
            self.add_file_data(record)
        return record

    def get_or_404(self, db: Session) -> T:
        """Get the singleton record or raise 404."""
        record = self.get(db)
        if not record:
            raise ContentNotFoundError(self.model_name, 0)
        return record


class CollectionService(BaseService[T]):
    """Service for collection models (Projects, Experience, Education, Skills)."""

    def get_all(self, db: Session) -> List[T]:
        """Get all active records with file data."""
        records = self.get_all_active(db)
        return [self.add_file_data(record) for record in records]

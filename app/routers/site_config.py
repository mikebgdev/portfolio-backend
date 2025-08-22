"""
Site Configuration router for Portfolio Backend API.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.deps.auth import get_db
from app.exceptions import ContentNotFoundError, DatabaseError, ValidationError
from app.schemas.site_config import SiteConfigResponse
from app.services.site_config import site_config_service

router = APIRouter(prefix="/site-config", tags=["site-config"])


@router.get("/", response_model=SiteConfigResponse)
async def get_site_config(db: Session = Depends(get_db)):
    """Get site configuration (public endpoint)."""
    try:
        site_config = await site_config_service.get_cached_site_config(db)
        if not site_config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Site configuration not found",
            )
        return site_config
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving site configuration: {str(e)}",
        )

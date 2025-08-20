"""
Site Configuration router for Portfolio Backend API.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.deps.auth import get_db, get_current_admin_user
from app.models.user import User
from app.services.site_config import site_config_service
from app.schemas.site_config import SiteConfigResponse, SiteConfigCreate, SiteConfigUpdate
from app.exceptions import ContentNotFoundError, DatabaseError, ValidationError

router = APIRouter(prefix="/site-config", tags=["site-config"])


@router.get("/", response_model=SiteConfigResponse)
async def get_site_config(db: Session = Depends(get_db)):
    """Get site configuration (public endpoint)."""
    try:
        site_config = await site_config_service.get_cached_site_config(db)
        if not site_config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Site configuration not found"
            )
        return site_config
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving site configuration: {str(e)}"
        )


@router.post("/", response_model=SiteConfigResponse, status_code=status.HTTP_201_CREATED)
async def create_site_config(
    site_config_data: SiteConfigCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Create site configuration (admin only)."""
    try:
        return site_config_service.create_site_config(db, site_config_data)
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except DatabaseError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put("/", response_model=SiteConfigResponse)
async def update_site_config(
    site_config_data: SiteConfigUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Update site configuration (admin only)."""
    try:
        return site_config_service.update_site_config(db, site_config_data)
    except ContentNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Site configuration not found"
        )
    except DatabaseError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_site_config(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Delete site configuration (admin only)."""
    try:
        site_config_service.delete_site_config(db)
    except ContentNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Site configuration not found"
        )
    except DatabaseError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
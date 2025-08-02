from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.deps.auth import get_db, get_current_admin_user
from app.schemas.content import AboutResponse, AboutUpdate
from app.services.content import about_service
from app.models.user import User

router = APIRouter(prefix="/about", tags=["about"])


@router.get("/", response_model=AboutResponse)
async def get_about(db: Session = Depends(get_db)):
    """Get about section content."""
    about = about_service.get_about(db)
    if not about:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="About content not found"
        )
    return AboutResponse.model_validate(about)


@router.put("/", response_model=AboutResponse)
async def update_about(
    about_data: AboutUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Update about section content (admin only)."""
    updated_about = about_service.update_about(db, about_data)
    return AboutResponse.model_validate(updated_about)
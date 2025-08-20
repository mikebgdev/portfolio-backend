from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.deps.auth import get_db
from app.schemas.about import AboutResponse
from app.services.about import about_service
from app.config import settings

router = APIRouter(prefix="/about", tags=["about"])

@router.get("/", response_model=AboutResponse)
async def get_about(
    db: Session = Depends(get_db),
    lang: Optional[str] = Query(default=settings.default_language, description="Language code (en, es)")
):
    """Get about section content with optional language parameter."""
    # Validate language
    if lang not in settings.supported_languages:
        lang = settings.default_language
    
    # Get the first about record (assuming single about record)
    about = about_service.get_about(db)
    if not about:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="About content not found"
        )
    
    # Create response with language context
    response = AboutResponse.model_validate(about)
    response.language = lang  # Set requested language for computed properties
    
    return response


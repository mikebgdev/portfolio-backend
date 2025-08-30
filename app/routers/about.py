from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.config import settings
from app.deps.auth import get_db
from app.schemas.about import AboutResponse
from app.services.about import about_service
from app.utils.validation import validate_language

router = APIRouter(prefix="/about", tags=["about"])


@router.get("/", response_model=AboutResponse)
async def get_about(
    db: Session = Depends(get_db),
    lang: Optional[str] = Query(
        default=settings.default_language, description="Language code (en, es)"
    ),
):
    """Get about section content with optional language parameter."""
    # Validate language
    lang = validate_language(lang)

    # Get the about record
    about = about_service.get_about(db)

    # Create response with language context
    response = AboutResponse.model_validate(about)
    response.language = lang  # Set requested language for computed properties

    return response

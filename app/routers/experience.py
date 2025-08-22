from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.config import settings
from app.deps.auth import get_db
from app.schemas.experience import ExperienceResponse
from app.services.experience import experience_service
from app.utils.validation import validate_language

router = APIRouter(prefix="/experience", tags=["experience"])


@router.get("/", response_model=List[ExperienceResponse])
async def get_experiences(
    db: Session = Depends(get_db),
    lang: Optional[str] = Query(
        default=settings.default_language, description="Language code (en, es)"
    ),
):
    """Get all work experiences with multilingual support."""
    # Validate language
    lang = validate_language(lang)

    experiences = experience_service.get_experiences(db)

    # Create response with language context
    experience_responses = []
    for experience in experiences:
        response = ExperienceResponse.model_validate(experience)
        response.language = lang  # Set requested language for computed properties
        experience_responses.append(response)

    return experience_responses

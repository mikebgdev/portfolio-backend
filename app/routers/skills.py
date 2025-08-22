from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.config import settings
from app.deps.auth import get_db
from app.schemas.skills import SkillsGroupedResponse
from app.services.skills import skill_service
from app.utils.validation import validate_language

router = APIRouter(prefix="/skills", tags=["skills"])


@router.get("/", response_model=SkillsGroupedResponse)
async def get_skills_grouped(
    lang: Optional[str] = Query(
        default=settings.default_language, description="Language code (en, es)"
    ),
    db: Session = Depends(get_db),
):
    """Get skills grouped by categories with multilingual support."""
    # Validate language
    lang = validate_language(lang)

    # Get grouped skills from service
    return await skill_service.get_skills_grouped(db, lang)

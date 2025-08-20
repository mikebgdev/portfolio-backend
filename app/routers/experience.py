from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.deps.auth import get_db
from app.schemas.experience import ExperienceResponse
from app.services.experience import experience_service
from app.config import settings

router = APIRouter(prefix="/experience", tags=["experience"])

@router.get("/", response_model=List[ExperienceResponse])
async def get_experiences(
    db: Session = Depends(get_db),
    lang: Optional[str] = Query(default=settings.default_language, description="Language code (en, es)")
):
    """Get all work experiences with multilingual support."""
    # Validate language
    if lang not in settings.supported_languages:
        lang = settings.default_language
    
    experiences = experience_service.get_experiences(db)
    
    # Create response with language context
    experience_responses = []
    for experience in experiences:
        response = ExperienceResponse.model_validate(experience)
        response.language = lang  # Set requested language for computed properties
        experience_responses.append(response)
    
    return experience_responses

@router.get("/{experience_id}", response_model=ExperienceResponse)
async def get_experience(
    experience_id: int, 
    db: Session = Depends(get_db),
    lang: Optional[str] = Query(default=settings.default_language, description="Language code (en, es)")
):
    """Get specific experience by ID with multilingual support."""
    # Validate language
    if lang not in settings.supported_languages:
        lang = settings.default_language
        
    experience = experience_service.get_experience_by_id(db, experience_id)
    if not experience:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Experience not found"
        )
    
    response = ExperienceResponse.model_validate(experience)
    response.language = lang  # Set requested language for computed properties
    return response


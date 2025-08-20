from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.deps.auth import get_db
from app.schemas.education import EducationResponse
from app.services.education import education_service
from app.config import settings

router = APIRouter(prefix="/education", tags=["education"])

@router.get("/", response_model=List[EducationResponse])
async def get_education_records(
    db: Session = Depends(get_db),
    lang: Optional[str] = Query(default=settings.default_language, description="Language code (en, es)")
):
    """Get all education records with multilingual support."""
    # Validate language
    if lang not in settings.supported_languages:
        lang = settings.default_language
    
    education_records = education_service.get_education_records(db)
    
    # Create response with language context
    education_responses = []
    for education in education_records:
        response = EducationResponse.model_validate(education)
        response.language = lang  # Set requested language for computed properties
        education_responses.append(response)
    
    return education_responses

@router.get("/{education_id}", response_model=EducationResponse)
async def get_education(
    education_id: int, 
    db: Session = Depends(get_db),
    lang: Optional[str] = Query(default=settings.default_language, description="Language code (en, es)")
):
    """Get specific education record by ID with multilingual support."""
    # Validate language
    if lang not in settings.supported_languages:
        lang = settings.default_language
        
    education = education_service.get_education_by_id(db, education_id)
    if not education:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Education record not found"
        )
    
    response = EducationResponse.model_validate(education)
    response.language = lang  # Set requested language for computed properties
    return response


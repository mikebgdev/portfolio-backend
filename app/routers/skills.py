from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.deps.auth import get_db
from app.schemas.skills import (
    SkillResponse, 
    SkillCategoryResponse,
    SkillsGroupedResponse
)
from app.services.skills import skill_service, skill_category_service
from app.config import settings

router = APIRouter(prefix="/skills", tags=["skills"])

@router.get("/", response_model=SkillsGroupedResponse)
async def get_skills_grouped(
    lang: Optional[str] = Query(default=settings.default_language, description="Language code (en, es)"),
    db: Session = Depends(get_db)
):
    """Get skills grouped by categories with multilingual support."""
    # Validate language
    if lang not in settings.supported_languages:
        lang = settings.default_language
    
    # Get grouped skills from service
    return await skill_service.get_skills_grouped(db, lang)

# Category endpoints
@router.get("/categories/", response_model=List[SkillCategoryResponse])
async def get_categories(
    lang: Optional[str] = Query(default=settings.default_language, description="Language code (en, es)"),
    db: Session = Depends(get_db)
):
    """Get all skill categories."""
    # Validate language
    if lang not in settings.supported_languages:
        lang = settings.default_language
    
    categories = skill_category_service.get_categories(db)
    
    # Create response with language context
    category_responses = []
    for category in categories:
        response = SkillCategoryResponse.model_validate(category)
        response.language = lang
        category_responses.append(response)
    
    return category_responses

@router.get("/list/", response_model=List[SkillResponse])
async def get_skills_list(
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    lang: Optional[str] = Query(default=settings.default_language, description="Language code (en, es)"),
    db: Session = Depends(get_db)
):
    """Get all skills as a flat list, optionally filtered by category."""
    # Validate language
    if lang not in settings.supported_languages:
        lang = settings.default_language
    
    # Get skills from service
    skills = skill_service.get_skills(db, category_id)
    
    # Create response with language context
    skill_responses = []
    for skill in skills:
        response = SkillResponse.model_validate(skill)
        response.language = lang
        skill_responses.append(response)
    
    return skill_responses

@router.get("/{skill_id}", response_model=SkillResponse)
async def get_skill(
    skill_id: int, 
    db: Session = Depends(get_db),
    lang: Optional[str] = Query(default=settings.default_language, description="Language code (en, es)")
):
    """Get specific skill by ID."""
    # Validate language
    if lang not in settings.supported_languages:
        lang = settings.default_language
        
    # Service will raise ContentNotFoundError if skill doesn't exist
    skill = skill_service.get_skill_by_id(db, skill_id)
    
    response = SkillResponse.model_validate(skill)
    response.language = lang  # Set requested language for computed properties
    return response


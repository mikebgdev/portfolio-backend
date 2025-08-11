from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.deps.auth import get_db, get_current_admin_user
from app.schemas.content import SkillResponse, SkillCreate, SkillUpdate
from app.services.content import skill_service
from app.models.user import User
from app.config import settings

router = APIRouter(prefix="/skills", tags=["skills"])


@router.get("/", response_model=List[SkillResponse])
async def get_skills(
    category: Optional[str] = Query(None, description="Filter by category: 'web_development', 'infrastructure', 'tools', 'learning', 'interpersonal'"),
    lang: Optional[str] = Query(default=settings.default_language, description="Language code (en, es)"),
    db: Session = Depends(get_db)
):
    """Get all skills, optionally filtered by type with multilingual support."""
    # Validate language
    if lang not in settings.supported_languages:
        lang = settings.default_language
    
    # Get skills from service
    skills = skill_service.get_skills(db, category)
    
    # Create response with language context
    skill_responses = []
    for skill in skills:
        response = SkillResponse.model_validate(skill)
        response.language = lang  # Set requested language for computed properties
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
        
    skill = skill_service.get_skill_by_id(db, skill_id)
    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill not found"
        )
    
    response = SkillResponse.model_validate(skill)
    response.language = lang  # Set requested language for computed properties
    return response


@router.post("/", response_model=SkillResponse, status_code=status.HTTP_201_CREATED)
async def create_skill(
    skill_data: SkillCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Create new skill (admin only)."""
    skill = skill_service.create_skill(db, skill_data)
    return SkillResponse.model_validate(skill)


@router.put("/{skill_id}", response_model=SkillResponse)
async def update_skill(
    skill_id: int,
    skill_data: SkillUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Update existing skill (admin only)."""
    skill = skill_service.update_skill(db, skill_id, skill_data)
    return SkillResponse.model_validate(skill)


@router.delete("/{skill_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_skill(
    skill_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Delete skill (admin only)."""
    success = skill_service.delete_skill(db, skill_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill not found"
        )
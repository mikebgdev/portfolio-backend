from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.deps.auth import get_db, get_current_admin_user
from app.schemas.content import (
    SkillResponse, SkillCreate, SkillUpdate, 
    SkillCategoryResponse, SkillCategoryCreate, SkillCategoryUpdate,
    SkillsGroupedResponse
)
from app.services.content import skill_service, skill_category_service
from app.models.user import User
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


@router.post("/categories/", response_model=SkillCategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    category_data: SkillCategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Create new skill category (admin only)."""
    category = skill_category_service.create_category(db, category_data)
    return SkillCategoryResponse.model_validate(category)


@router.put("/categories/{category_id}", response_model=SkillCategoryResponse)
async def update_category(
    category_id: int,
    category_data: SkillCategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Update existing skill category (admin only)."""
    category = await skill_category_service.update_category(db, category_id, category_data)
    return SkillCategoryResponse.model_validate(category)


@router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Delete skill category (admin only)."""
    success = skill_category_service.delete_category(db, category_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )


# Individual skill endpoints
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


@router.post("/", response_model=SkillResponse, status_code=status.HTTP_201_CREATED)
async def create_skill(
    skill_data: SkillCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Create new skill (admin only)."""
    skill = await skill_service.create_skill(db, skill_data)
    return SkillResponse.model_validate(skill)


@router.put("/{skill_id}", response_model=SkillResponse)
async def update_skill(
    skill_id: int,
    skill_data: SkillUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Update existing skill (admin only)."""
    skill = await skill_service.update_skill(db, skill_id, skill_data)
    return SkillResponse.model_validate(skill)


@router.delete("/{skill_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_skill(
    skill_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Delete skill (admin only)."""
    success = await skill_service.delete_skill(db, skill_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill not found"
        )
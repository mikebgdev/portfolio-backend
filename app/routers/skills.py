from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.deps.auth import get_db, get_current_admin_user
from app.schemas.content import SkillResponse, SkillCreate, SkillUpdate
from app.services.content import skill_service
from app.models.user import User

router = APIRouter(prefix="/skills", tags=["skills"])


@router.get("/", response_model=List[SkillResponse])
async def get_skills(
    skill_type: Optional[str] = Query(None, description="Filter by skill type: 'technical' or 'interpersonal'"),
    db: Session = Depends(get_db)
):
    """Get all skills, optionally filtered by type."""
    skills = skill_service.get_skills(db, skill_type)
    return [SkillResponse.model_validate(skill) for skill in skills]


@router.get("/{skill_id}", response_model=SkillResponse)
async def get_skill(skill_id: int, db: Session = Depends(get_db)):
    """Get specific skill by ID."""
    skill = skill_service.get_skill_by_id(db, skill_id)
    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill not found"
        )
    return SkillResponse.model_validate(skill)


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
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.deps.auth import get_db, get_current_admin_user
from app.schemas.content import ExperienceResponse, ExperienceCreate, ExperienceUpdate
from app.services.content import experience_service
from app.models.user import User

router = APIRouter(prefix="/experience", tags=["experience"])


@router.get("/", response_model=List[ExperienceResponse])
async def get_experiences(db: Session = Depends(get_db)):
    """Get all work experiences."""
    experiences = experience_service.get_experiences(db)
    return [ExperienceResponse.model_validate(exp) for exp in experiences]


@router.get("/{experience_id}", response_model=ExperienceResponse)
async def get_experience(experience_id: int, db: Session = Depends(get_db)):
    """Get specific experience by ID."""
    experience = experience_service.get_experience_by_id(db, experience_id)
    if not experience:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Experience not found"
        )
    return ExperienceResponse.model_validate(experience)


@router.post("/", response_model=ExperienceResponse, status_code=status.HTTP_201_CREATED)
async def create_experience(
    experience_data: ExperienceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Create new experience (admin only)."""
    experience = experience_service.create_experience(db, experience_data)
    return ExperienceResponse.model_validate(experience)


@router.put("/{experience_id}", response_model=ExperienceResponse)
async def update_experience(
    experience_id: int,
    experience_data: ExperienceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Update existing experience (admin only)."""
    experience = experience_service.update_experience(db, experience_id, experience_data)
    return ExperienceResponse.model_validate(experience)


@router.delete("/{experience_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_experience(
    experience_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Delete experience (admin only)."""
    success = experience_service.delete_experience(db, experience_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Experience not found"
        )
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.deps.auth import get_db, get_current_admin_user
from app.schemas.content import EducationResponse, EducationCreate, EducationUpdate
from app.services.content import education_service
from app.models.user import User

router = APIRouter(prefix="/education", tags=["education"])


@router.get("/", response_model=List[EducationResponse])
async def get_education_records(db: Session = Depends(get_db)):
    """Get all education records."""
    education_records = education_service.get_education_records(db)
    return [EducationResponse.model_validate(edu) for edu in education_records]


@router.get("/{education_id}", response_model=EducationResponse)
async def get_education(education_id: int, db: Session = Depends(get_db)):
    """Get specific education record by ID."""
    education = education_service.get_education_by_id(db, education_id)
    if not education:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Education record not found"
        )
    return EducationResponse.model_validate(education)


@router.post("/", response_model=EducationResponse, status_code=status.HTTP_201_CREATED)
async def create_education(
    education_data: EducationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Create new education record (admin only)."""
    education = education_service.create_education(db, education_data)
    return EducationResponse.model_validate(education)


@router.put("/{education_id}", response_model=EducationResponse)
async def update_education(
    education_id: int,
    education_data: EducationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Update existing education record (admin only)."""
    education = education_service.update_education(db, education_id, education_data)
    return EducationResponse.model_validate(education)


@router.delete("/{education_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_education(
    education_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Delete education record (admin only)."""
    success = education_service.delete_education(db, education_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Education record not found"
        )
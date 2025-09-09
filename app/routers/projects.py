from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.config import settings
from app.deps.auth import get_db
from app.schemas.projects import ProjectCreate, ProjectResponse, ProjectUpdate
from app.services.projects import project_service
from app.utils.validation import build_response_with_language, validate_language

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("/", response_model=List[ProjectResponse])
async def get_projects(
    db: Session = Depends(get_db),
    lang: Optional[str] = Query(
        default=settings.default_language, description="Language code (en, es)"
    ),
):
    """Get all projects with multilingual support."""
    # Validate language
    lang = validate_language(lang)

    projects = project_service.get_projects(db)

    # Create response with language context
    return build_response_with_language(projects, ProjectResponse, lang)


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    lang: Optional[str] = Query(
        default=settings.default_language, description="Language code (en, es)"
    ),
):
    """Get a specific project by ID with multilingual support."""
    # Validate language
    lang = validate_language(lang)

    try:
        project = project_service.get_project_by_id(db, project_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Project not found")

    # Create response with language context
    return build_response_with_language([project], ProjectResponse, lang)[0]


@router.post("/", response_model=ProjectResponse)
async def create_project(
    project_data: ProjectCreate,
    db: Session = Depends(get_db),
    lang: Optional[str] = Query(
        default=settings.default_language, description="Language code (en, es)"
    ),
):
    """Create a new project with associated skills."""
    # Validate language
    lang = validate_language(lang)

    try:
        project = project_service.create_project(db, project_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Create response with language context
    return build_response_with_language([project], ProjectResponse, lang)[0]


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    project_data: ProjectUpdate,
    db: Session = Depends(get_db),
    lang: Optional[str] = Query(
        default=settings.default_language, description="Language code (en, es)"
    ),
):
    """Update an existing project with new data and skills."""
    # Validate language
    lang = validate_language(lang)

    try:
        project = project_service.update_project(db, project_id, project_data)
    except ValueError as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=str(e))
        else:
            raise HTTPException(status_code=400, detail=str(e))

    # Create response with language context
    return build_response_with_language([project], ProjectResponse, lang)[0]


@router.delete("/{project_id}")
async def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
):
    """Delete a project by ID."""
    try:
        success = project_service.delete_project(db, project_id)
        return {"success": success, "message": "Project deleted successfully"}
    except ValueError:
        raise HTTPException(status_code=404, detail="Project not found")

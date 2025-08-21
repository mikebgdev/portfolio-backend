from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.deps.auth import get_db
from app.schemas.projects import ProjectResponse
from app.services.projects import project_service
from app.config import settings
from app.utils.validation import validate_language, build_response_with_language

router = APIRouter(prefix="/projects", tags=["projects"])

@router.get("/", response_model=List[ProjectResponse])
async def get_projects(
    db: Session = Depends(get_db),
    lang: Optional[str] = Query(default=settings.default_language, description="Language code (en, es)")
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
    lang: Optional[str] = Query(default=settings.default_language, description="Language code (en, es)")
):
    """Get specific project by ID with multilingual support."""
    # Validate language
    lang = validate_language(lang)
        
    # Service will raise ContentNotFoundError if project doesn't exist
    project = project_service.get_project_by_id(db, project_id)
    
    return build_response_with_language(project, ProjectResponse, lang)


from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.deps.auth import get_db
from app.schemas.projects import ProjectResponse
from app.services.projects import project_service
from app.config import settings

router = APIRouter(prefix="/projects", tags=["projects"])

@router.get("/", response_model=List[ProjectResponse])
async def get_projects(
    db: Session = Depends(get_db),
    lang: Optional[str] = Query(default=settings.default_language, description="Language code (en, es)")
):
    """Get all projects with multilingual support."""
    # Validate language
    if lang not in settings.supported_languages:
        lang = settings.default_language
    
    projects = project_service.get_projects(db)
    
    # Create response with language context
    project_responses = []
    for project in projects:
        response = ProjectResponse.model_validate(project)
        response.language = lang  # Set requested language for computed properties
        project_responses.append(response)
    
    return project_responses

@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int, 
    db: Session = Depends(get_db),
    lang: Optional[str] = Query(default=settings.default_language, description="Language code (en, es)")
):
    """Get specific project by ID with multilingual support."""
    # Validate language
    if lang not in settings.supported_languages:
        lang = settings.default_language
        
    project = project_service.get_project_by_id(db, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    response = ProjectResponse.model_validate(project)
    response.language = lang  # Set requested language for computed properties
    return response


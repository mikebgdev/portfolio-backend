from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.deps.auth import get_db
from app.schemas.contact import ContactResponse
from app.services.contact import contact_service
from app.config import settings

router = APIRouter(prefix="/contact", tags=["contact"])

@router.get("/", response_model=ContactResponse)
async def get_contact(
    db: Session = Depends(get_db),
    lang: Optional[str] = Query(default=settings.default_language, description="Language code (en, es)")
):
    """Get contact section content with optional language parameter."""
    # Validate language
    if lang not in settings.supported_languages:
        lang = settings.default_language
    
    # Get the first contact record (assuming single contact record)
    contact = contact_service.get_contact(db)
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact content not found"
        )
    
    # Create response with language context
    response = ContactResponse.model_validate(contact)
    response.language = lang  # Set requested language for computed properties
    
    return response


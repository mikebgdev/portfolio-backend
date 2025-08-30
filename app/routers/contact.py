from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.config import settings
from app.deps.auth import get_db
from app.schemas.contact import ContactResponse
from app.services.contact import contact_service
from app.utils.validation import validate_language

router = APIRouter(prefix="/contact", tags=["contact"])


@router.get("/", response_model=ContactResponse)
async def get_contact(
    db: Session = Depends(get_db),
    lang: Optional[str] = Query(
        default=settings.default_language, description="Language code (en, es)"
    ),
):
    """Get contact section content with optional language parameter."""
    # Validate language
    lang = validate_language(lang)

    # Get the contact record
    contact = contact_service.get_contact(db)

    # Create response with language context
    response = ContactResponse.model_validate(contact)
    response.language = lang  # Set requested language for computed properties

    return response

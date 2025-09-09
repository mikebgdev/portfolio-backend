from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.config import settings
from app.deps.auth import get_db
from app.schemas.contact import (
    ContactMessageRequest,
    ContactMessageResponse,
    ContactResponse,
)
from app.services.contact import contact_service
from app.services.contact_message import contact_message_service
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


@router.post(
    "/send/", response_model=ContactMessageResponse, status_code=status.HTTP_201_CREATED
)
async def send_contact_message(
    message_data: ContactMessageRequest,
    db: Session = Depends(get_db),
    lang: Optional[str] = Query(
        default=settings.default_language, description="Language code (en, es)"
    ),
):
    """Send a contact message through the contact form."""
    try:
        # Check if contact form is enabled
        contact_info = contact_service.get_contact(db)
        if contact_info and not contact_info.contact_form_enabled:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Contact form is currently disabled",
            )

        # Validate language
        lang = validate_language(lang)

        # Create the contact message
        response = await contact_message_service.create_contact_message(
            db, message_data, lang
        )

        return response

    except HTTPException:
        # Re-raise HTTP exceptions to preserve status codes
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error sending contact message: {str(e)}",
        )

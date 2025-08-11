from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from app.deps.auth import get_db, get_current_admin_user
# from app.schemas.content import TranslationResponse, TranslationCreate, TranslationUpdate  # Disabled - using direct multilingual fields
from app.services.translation_service import TranslationService, SUPPORTED_LANGUAGES
from app.models.user import User

# Note: This translation router is deprecated as we now use direct multilingual fields (_en, _es)
# instead of a separate translations table

router = APIRouter(prefix="/translations", tags=["translations"])


@router.get("/stats", response_model=Dict[str, Any])
async def get_translation_stats(db: Session = Depends(get_db)):
    """Get translation statistics for the system."""
    translation_service = TranslationService(db)
    return translation_service.get_translation_stats()


@router.get("/languages", response_model=Dict[str, str])
async def get_supported_languages():
    """Get list of supported languages."""
    return SUPPORTED_LANGUAGES


@router.get("/{content_type}/{content_id}", response_model=List[TranslationResponse])
async def get_translations_for_content(
    content_type: str,
    content_id: int,
    db: Session = Depends(get_db)
):
    """Get all translations for a specific content item."""
    from app.models.translations import ContentTranslation
    
    translations = db.query(ContentTranslation).filter(
        ContentTranslation.content_type == content_type,
        ContentTranslation.content_id == content_id
    ).all()
    
    return [TranslationResponse.model_validate(t) for t in translations]


@router.post("/", response_model=TranslationResponse, status_code=status.HTTP_201_CREATED)
async def create_translation(
    translation_data: TranslationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Create a new translation (admin only)."""
    translation_service = TranslationService(db)
    
    # Validate and create translation
    success = translation_service.set_translation(
        content_type=translation_data.content_type,
        content_id=translation_data.content_id,
        field_name=translation_data.field_name,
        language=translation_data.language_code,
        translated_text=translation_data.translated_text
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create translation. Check content type, language, and field validity."
        )
    
    # Return the created translation
    from app.models.translations import ContentTranslation
    translation = db.query(ContentTranslation).filter(
        ContentTranslation.content_type == translation_data.content_type,
        ContentTranslation.content_id == translation_data.content_id,
        ContentTranslation.field_name == translation_data.field_name,
        ContentTranslation.language_code == translation_data.language_code
    ).first()
    
    return TranslationResponse.model_validate(translation)


@router.put("/{translation_id}", response_model=TranslationResponse)
async def update_translation(
    translation_id: int,
    translation_data: TranslationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Update an existing translation (admin only)."""
    from app.models.translations import ContentTranslation
    
    translation = db.query(ContentTranslation).filter(
        ContentTranslation.id == translation_id
    ).first()
    
    if not translation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Translation not found"
        )
    
    # Update the translation
    translation.translated_text = translation_data.translated_text
    
    try:
        db.commit()
        db.refresh(translation)
        return TranslationResponse.model_validate(translation)
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update translation"
        )


@router.delete("/{translation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_translation(
    translation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Delete a translation (admin only)."""
    from app.models.translations import ContentTranslation
    
    translation = db.query(ContentTranslation).filter(
        ContentTranslation.id == translation_id
    ).first()
    
    if not translation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Translation not found"
        )
    
    try:
        db.delete(translation)
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete translation"
        )


@router.get("/available-languages/{content_type}/{content_id}", response_model=List[str])
async def get_available_languages_for_content(
    content_type: str,
    content_id: int,
    db: Session = Depends(get_db)
):
    """Get available languages for specific content."""
    translation_service = TranslationService(db)
    return translation_service.get_available_languages(content_type, content_id)
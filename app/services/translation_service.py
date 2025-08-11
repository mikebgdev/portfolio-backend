from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
from app.models.translations import ContentTranslation
from app.models.content import About, Skill, Project, Experience, Education, Contact

# Supported languages
SUPPORTED_LANGUAGES = {
    'en': 'English',
    'es': 'Español'
}
DEFAULT_LANGUAGE = 'en'

# Map of content types to their translatable fields (based on mikebgdev.com analysis)
TRANSLATABLE_FIELDS = {
    'about': ['nationality', 'bio', 'personal_statement'],  # Updated for new About structure
    'skill': ['name'],  # Skill names can be translated
    'project': ['title', 'description'],  # Updated: title instead of name
    'experience': ['position', 'description'],  # Job title and description
    'education': ['degree', 'field_of_study', 'description'],  # Educational details
    'contact': ['contact_message']  # Contact section message
}


class TranslationService:
    """Service to handle multilingual content translation operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_translated_content(self, content_type: str, content_id: int, language: str = DEFAULT_LANGUAGE) -> Optional[Dict[str, Any]]:
        """
        Get content with translations applied for the specified language.
        
        Args:
            content_type: Type of content ('about', 'skill', 'project', etc.)
            content_id: ID of the content item
            language: Language code ('en', 'es')
            
        Returns:
            Dictionary with original content and translations applied
        """
        # Validate language
        if language not in SUPPORTED_LANGUAGES:
            language = DEFAULT_LANGUAGE
        
        # Get the base content based on content type
        model_map = {
            'about': About,
            'skill': Skill,
            'project': Project,
            'experience': Experience,
            'education': Education,
            'contact': Contact
        }
        
        if content_type not in model_map:
            return None
            
        # Get the original content
        original_content = self.db.query(model_map[content_type]).filter(
            model_map[content_type].id == content_id
        ).first()
        
        if not original_content:
            return None
        
        # Convert to dict
        content_dict = {
            column.name: getattr(original_content, column.name)
            for column in original_content.__table__.columns
        }
        
        # Add metadata
        content_dict['language'] = language
        content_dict['available_languages'] = self.get_available_languages(content_type, content_id)
        
        # If requesting English (default), return as is
        if language == DEFAULT_LANGUAGE:
            return content_dict
        
        # Get translations for the requested language
        translations = self.db.query(ContentTranslation).filter(
            ContentTranslation.content_type == content_type,
            ContentTranslation.content_id == content_id,
            ContentTranslation.language_code == language
        ).all()
        
        # Apply translations
        translation_map = {trans.field_name: trans.translated_text for trans in translations}
        
        for field_name in TRANSLATABLE_FIELDS.get(content_type, []):
            if field_name in translation_map:
                content_dict[field_name] = translation_map[field_name]
        
        return content_dict
    
    def get_all_translated_content(self, content_type: str, language: str = DEFAULT_LANGUAGE) -> List[Dict[str, Any]]:
        """
        Get all content items of a specific type with translations applied.
        
        Args:
            content_type: Type of content ('about', 'skill', 'project', etc.)
            language: Language code ('en', 'es')
            
        Returns:
            List of dictionaries with content and translations applied
        """
        # Get model class
        model_map = {
            'about': About,
            'skill': Skill,
            'project': Project,
            'experience': Experience,
            'education': Education,
            'contact': Contact
        }
        
        if content_type not in model_map:
            return []
        
        # Get all content items
        content_items = self.db.query(model_map[content_type]).all()
        
        # Apply translations to each item
        translated_items = []
        for item in content_items:
            translated_item = self.get_translated_content(content_type, item.id, language)
            if translated_item:
                translated_items.append(translated_item)
        
        return translated_items
    
    def set_translation(self, content_type: str, content_id: int, field_name: str, language: str, translated_text: str) -> bool:
        """
        Set or update a translation for a specific content field.
        
        Args:
            content_type: Type of content ('about', 'skill', 'project', etc.)
            content_id: ID of the content item
            field_name: Name of the field being translated
            language: Language code ('en', 'es')
            translated_text: The translated text
            
        Returns:
            True if successful, False otherwise
        """
        # Validate inputs
        if language not in SUPPORTED_LANGUAGES:
            return False
            
        if content_type not in TRANSLATABLE_FIELDS:
            return False
            
        if field_name not in TRANSLATABLE_FIELDS[content_type]:
            return False
        
        # Don't allow setting translation for default language
        if language == DEFAULT_LANGUAGE:
            return False
        
        # Check if translation already exists
        existing_translation = self.db.query(ContentTranslation).filter(
            ContentTranslation.content_type == content_type,
            ContentTranslation.content_id == content_id,
            ContentTranslation.field_name == field_name,
            ContentTranslation.language_code == language
        ).first()
        
        if existing_translation:
            # Update existing translation
            existing_translation.translated_text = translated_text
        else:
            # Create new translation
            new_translation = ContentTranslation(
                content_type=content_type,
                content_id=content_id,
                field_name=field_name,
                language_code=language,
                translated_text=translated_text
            )
            self.db.add(new_translation)
        
        try:
            self.db.commit()
            return True
        except Exception:
            self.db.rollback()
            return False
    
    def get_available_languages(self, content_type: str, content_id: int) -> List[str]:
        """
        Get list of available languages for a specific content item.
        
        Args:
            content_type: Type of content
            content_id: ID of the content item
            
        Returns:
            List of available language codes
        """
        languages = set([DEFAULT_LANGUAGE])  # Always include default language
        
        # Get all languages that have translations for this content
        translations = self.db.query(ContentTranslation.language_code).filter(
            ContentTranslation.content_type == content_type,
            ContentTranslation.content_id == content_id
        ).distinct().all()
        
        for translation in translations:
            languages.add(translation.language_code)
        
        return sorted(list(languages))
    
    def delete_translation(self, content_type: str, content_id: int, field_name: str, language: str) -> bool:
        """
        Delete a specific translation.
        
        Args:
            content_type: Type of content
            content_id: ID of the content item
            field_name: Name of the field
            language: Language code
            
        Returns:
            True if successful, False otherwise
        """
        if language == DEFAULT_LANGUAGE:
            return False  # Can't delete default language content
        
        translation = self.db.query(ContentTranslation).filter(
            ContentTranslation.content_type == content_type,
            ContentTranslation.content_id == content_id,
            ContentTranslation.field_name == field_name,
            ContentTranslation.language_code == language
        ).first()
        
        if translation:
            try:
                self.db.delete(translation)
                self.db.commit()
                return True
            except Exception:
                self.db.rollback()
                return False
        
        return False
    
    def get_translation_stats(self) -> Dict[str, Any]:
        """
        Get statistics about translations in the system.
        
        Returns:
            Dictionary with translation statistics
        """
        stats = {
            'total_translations': self.db.query(ContentTranslation).count(),
            'languages': list(SUPPORTED_LANGUAGES.keys()),
            'content_types': list(TRANSLATABLE_FIELDS.keys()),
            'by_language': {},
            'by_content_type': {}
        }
        
        # Count by language
        for lang in SUPPORTED_LANGUAGES.keys():
            if lang == DEFAULT_LANGUAGE:
                # For default language, count original content items
                total = 0
                for content_type in TRANSLATABLE_FIELDS.keys():
                    model_map = {
                        'about': About,
                        'skill': Skill,
                        'project': Project,
                        'experience': Experience,
                        'education': Education,
                        'contact': Contact
                    }
                    if content_type in model_map:
                        count = self.db.query(model_map[content_type]).count()
                        total += count * len(TRANSLATABLE_FIELDS[content_type])
                stats['by_language'][lang] = total
            else:
                count = self.db.query(ContentTranslation).filter(
                    ContentTranslation.language_code == lang
                ).count()
                stats['by_language'][lang] = count
        
        # Count by content type
        for content_type in TRANSLATABLE_FIELDS.keys():
            count = self.db.query(ContentTranslation).filter(
                ContentTranslation.content_type == content_type
            ).count()
            stats['by_content_type'][content_type] = count
        
        return stats
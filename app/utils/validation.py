"""Validation utilities for common application patterns."""

from typing import List, Optional, TypeVar, Union

from pydantic import BaseModel

from app.config import settings

T = TypeVar("T", bound=BaseModel)


def validate_language(lang: Optional[str]) -> str:
    """
    Validate and normalize language parameter.

    Args:
        lang: Language code to validate

    Returns:
        Valid language code (defaults to settings.default_language if invalid)
    """
    if lang and lang in settings.supported_languages:
        return lang
    return settings.default_language


def get_multilingual_text(text_en: str, text_es: Optional[str], language: str) -> str:
    """
    Get text in specified language with fallback to English.

    Args:
        text_en: English text
        text_es: Spanish text (optional)
        language: Requested language code

    Returns:
        Text in requested language or English fallback
    """
    if language == "es" and text_es:
        return text_es
    return text_en


def build_response_with_language(
    model_data: Union[object, List[object]], response_class: type[T], language: str
) -> Union[T, List[T]]:
    """
    Build response object(s) with language context.

    Args:
        model_data: Database model object or list of objects
        response_class: Pydantic response class
        language: Language code to set

    Returns:
        Response object or list of response objects with language set
    """
    if isinstance(model_data, list):
        responses = []
        for item in model_data:
            response = response_class.model_validate(item)
            response.language = language
            responses.append(response)
        return responses
    else:
        response = response_class.model_validate(model_data)
        response.language = language
        return response

"""Iconify utilities API endpoints for icon and color management."""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Query

from app.utils.iconify import (
    get_icon_tooltip_info,
    get_popular_icons_by_category,
    search_icons,
    validate_hex_color,
    format_hex_color,
    get_suggested_color,
    normalize_icon_name
)

router = APIRouter(prefix="/iconify", tags=["iconify"])


@router.get("/tooltip", response_model=Dict)
async def get_icon_tooltip(
    icon_name: Optional[str] = Query(None, description="Icon name to get tooltip info for"),
    color: Optional[str] = Query(None, description="Color value to validate (hex format)"),
    context: Optional[str] = Query("default", description="Context for fallback suggestions (skill, social, etc.)")
):
    """
    Get tooltip information for icon and color validation.
    
    Provides:
    - Icon name normalization
    - Color validation and formatting
    - Suggested colors for popular technologies
    - Fallback icon recommendations
    - Best practice recommendations
    """
    return get_icon_tooltip_info(icon_name, color, context)


@router.get("/search", response_model=List[Dict[str, str]])
async def search_icon_suggestions(
    q: str = Query(..., description="Search query for icon names"),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of results")
):
    """
    Search for icon suggestions based on query.
    
    Returns matching icons with recommended colors.
    """
    return search_icons(q, limit)


@router.get("/categories", response_model=Dict[str, List[Dict[str, str]]])
async def get_icon_categories():
    """
    Get popular icons organized by categories.
    
    Useful for showing available icons in admin interfaces.
    """
    return get_popular_icons_by_category()


@router.get("/validate-color", response_model=Dict[str, Any])
async def validate_color(
    color: str = Query(..., description="Color value to validate")
):
    """
    Validate and format a color value.
    
    Returns validation status and formatted color.
    """
    is_valid = validate_hex_color(color)
    formatted = format_hex_color(color) if is_valid else None
    
    return {
        "original_color": color,
        "is_valid": is_valid,
        "formatted_color": formatted,
        "message": "Valid hex color" if is_valid else "Invalid color format. Use hex format like #FF0000 or #F00"
    }


@router.get("/suggest-color", response_model=Dict[str, Any])
async def suggest_color_for_icon(
    icon_name: str = Query(..., description="Icon name to get color suggestion for")
):
    """
    Get color suggestion for a specific icon.
    
    Based on popular technology color mappings.
    """
    normalized_name = normalize_icon_name(icon_name)
    suggested_color = get_suggested_color(normalized_name)
    
    return {
        "original_name": icon_name,
        "normalized_name": normalized_name,
        "suggested_color": suggested_color,
        "has_suggestion": bool(suggested_color),
        "message": f"Suggested color: {suggested_color}" if suggested_color else "No color suggestion available for this icon"
    }


@router.get("/normalize-icon", response_model=Dict[str, str])
async def normalize_icon(
    icon_name: str = Query(..., description="Icon name to normalize")
):
    """
    Normalize an icon name for consistency.
    
    Handles variations like 'arch-linux' -> 'archlinux'
    """
    normalized = normalize_icon_name(icon_name)
    
    return {
        "original_name": icon_name,
        "normalized_name": normalized,
        "message": f"'{icon_name}' normalized to '{normalized}'" if normalized != icon_name.lower() else "Icon name already normalized"
    }
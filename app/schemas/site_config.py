"""
Site Configuration schemas for Portfolio Backend API.
"""

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class SiteConfigBase(BaseModel):
    """Base schema for site configuration."""

    site_title: str = Field(
        ..., min_length=1, max_length=200, description="Website title"
    )
    brand_name: str = Field(..., min_length=1, max_length=100, description="Brand name")
    meta_description: Optional[str] = Field(
        None, max_length=500, description="Meta description for SEO"
    )
    meta_keywords: Optional[str] = Field(
        None, max_length=300, description="Meta keywords for SEO"
    )

    # File uploads
    favicon_file: Optional[str] = Field(None, description="Favicon file path")

    # Open Graph metadata for social sharing
    og_title: Optional[str] = Field(
        None, max_length=200, description="Open Graph title for social sharing"
    )
    og_description: Optional[str] = Field(
        None, max_length=500, description="Open Graph description for social sharing"
    )
    og_image_file: Optional[str] = Field(None, description="Open Graph image file path")
    og_url: Optional[str] = Field(
        None, max_length=300, description="Canonical URL for Open Graph"
    )
    og_type: Optional[str] = Field(
        "website", max_length=50, description="Open Graph type (website, profile, etc.)"
    )

    # Twitter Card metadata
    twitter_card: Optional[str] = Field(
        "summary_large_image", max_length=50, description="Twitter card type"
    )
    twitter_title: Optional[str] = Field(
        None, max_length=200, description="Twitter card title"
    )
    twitter_description: Optional[str] = Field(
        None, max_length=500, description="Twitter card description"
    )
    twitter_image_file: Optional[str] = Field(
        None, description="Twitter card image file path"
    )


class SiteConfigCreate(SiteConfigBase):
    """Schema for creating site configuration."""

    pass


class SiteConfigUpdate(BaseModel):
    """Schema for updating site configuration."""

    site_title: Optional[str] = Field(None, min_length=1, max_length=200)
    brand_name: Optional[str] = Field(None, min_length=1, max_length=100)
    meta_description: Optional[str] = Field(None, max_length=500)
    meta_keywords: Optional[str] = Field(None, max_length=300)

    # File uploads
    favicon_file: Optional[str] = Field(None)

    # Open Graph metadata for social sharing
    og_title: Optional[str] = Field(None, max_length=200)
    og_description: Optional[str] = Field(None, max_length=500)
    og_image_file: Optional[str] = Field(None)
    og_url: Optional[str] = Field(None, max_length=300)
    og_type: Optional[str] = Field(None, max_length=50)

    # Twitter Card metadata
    twitter_card: Optional[str] = Field(None, max_length=50)
    twitter_title: Optional[str] = Field(None, max_length=200)
    twitter_description: Optional[str] = Field(None, max_length=500)
    twitter_image_file: Optional[str] = Field(None)


class SiteConfigResponse(SiteConfigBase):
    """Schema for site configuration response."""

    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # File data (populated by service layer)
    favicon_data: Optional[Dict[str, Any]] = Field(
        None, description="Favicon file as Base64 data URL"
    )
    og_image_data: Optional[Dict[str, Any]] = Field(
        None, description="OG image file as Base64 data URL"
    )
    twitter_image_data: Optional[Dict[str, Any]] = Field(
        None, description="Twitter image file as Base64 data URL"
    )

    class Config:
        from_attributes = True

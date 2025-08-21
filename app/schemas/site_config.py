"""
Site Configuration schemas for Portfolio Backend API.
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class SiteConfigBase(BaseModel):
    """Base schema for site configuration."""
    site_title: str = Field(..., min_length=1, max_length=200, description="Website title")
    brand_name: str = Field(..., min_length=1, max_length=100, description="Brand name")
    meta_description: Optional[str] = Field(None, max_length=500, description="Meta description for SEO")
    meta_keywords: Optional[str] = Field(None, max_length=300, description="Meta keywords for SEO")
    
    # Open Graph metadata for social sharing
    og_title: Optional[str] = Field(None, max_length=200, description="Open Graph title for social sharing")
    og_description: Optional[str] = Field(None, max_length=500, description="Open Graph description for social sharing")
    og_image: Optional[str] = Field(None, max_length=500, description="Open Graph image URL for social sharing")
    og_url: Optional[str] = Field(None, max_length=300, description="Canonical URL for Open Graph")
    og_type: Optional[str] = Field("website", max_length=50, description="Open Graph type (website, profile, etc.)")
    
    # Twitter Card metadata
    twitter_card: Optional[str] = Field("summary_large_image", max_length=50, description="Twitter card type")
    twitter_site: Optional[str] = Field(None, max_length=100, description="Twitter @username for website")
    twitter_creator: Optional[str] = Field(None, max_length=100, description="Twitter @username for creator")
    twitter_title: Optional[str] = Field(None, max_length=200, description="Twitter card title")
    twitter_description: Optional[str] = Field(None, max_length=500, description="Twitter card description")
    twitter_image: Optional[str] = Field(None, max_length=500, description="Twitter card image URL")


class SiteConfigCreate(SiteConfigBase):
    """Schema for creating site configuration."""
    pass


class SiteConfigUpdate(BaseModel):
    """Schema for updating site configuration."""
    site_title: Optional[str] = Field(None, min_length=1, max_length=200)
    brand_name: Optional[str] = Field(None, min_length=1, max_length=100)
    meta_description: Optional[str] = Field(None, max_length=500)
    meta_keywords: Optional[str] = Field(None, max_length=300)
    
    # Open Graph metadata for social sharing
    og_title: Optional[str] = Field(None, max_length=200)
    og_description: Optional[str] = Field(None, max_length=500)
    og_image: Optional[str] = Field(None, max_length=500)
    og_url: Optional[str] = Field(None, max_length=300)
    og_type: Optional[str] = Field(None, max_length=50)
    
    # Twitter Card metadata
    twitter_card: Optional[str] = Field(None, max_length=50)
    twitter_site: Optional[str] = Field(None, max_length=100)
    twitter_creator: Optional[str] = Field(None, max_length=100)
    twitter_title: Optional[str] = Field(None, max_length=200)
    twitter_description: Optional[str] = Field(None, max_length=500)
    twitter_image: Optional[str] = Field(None, max_length=500)


class SiteConfigResponse(SiteConfigBase):
    """Schema for site configuration response."""
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
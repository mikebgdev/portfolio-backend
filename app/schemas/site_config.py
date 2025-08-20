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


class SiteConfigCreate(SiteConfigBase):
    """Schema for creating site configuration."""
    pass


class SiteConfigUpdate(BaseModel):
    """Schema for updating site configuration."""
    site_title: Optional[str] = Field(None, min_length=1, max_length=200)
    brand_name: Optional[str] = Field(None, min_length=1, max_length=100)
    meta_description: Optional[str] = Field(None, max_length=500)
    meta_keywords: Optional[str] = Field(None, max_length=300)


class SiteConfigResponse(SiteConfigBase):
    """Schema for site configuration response."""
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
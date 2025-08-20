"""
Site Configuration model for Portfolio Backend API.
"""
from sqlalchemy import Column, Integer, String, DateTime, func
from app.database import Base


class SiteConfig(Base):
    """Site configuration settings."""
    
    __tablename__ = "site_config"
    
    id = Column(Integer, primary_key=True, index=True)
    site_title = Column(String(200), nullable=False, index=True)
    brand_name = Column(String(100), nullable=False)
    meta_description = Column(String(500), nullable=True)
    meta_keywords = Column(String(300), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<SiteConfig(site_title='{self.site_title}', brand_name='{self.brand_name}')>"
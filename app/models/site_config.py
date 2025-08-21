"""
Site Configuration model for Portfolio Backend API.
"""
from sqlalchemy import Column, Integer, String, DateTime, func, Text
from app.database import Base


class SiteConfig(Base):
    """Site configuration settings with social media metadata."""
    
    __tablename__ = "site_config"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Basic site information
    site_title = Column(String(200), nullable=False, index=True, info={"label": "Título del Sitio"})
    brand_name = Column(String(100), nullable=False, info={"label": "Nombre de la Marca"})
    meta_description = Column(String(500), nullable=True, info={"label": "Meta Descripción"})
    meta_keywords = Column(String(300), nullable=True, info={"label": "Meta Keywords"})
    
    # Open Graph metadata for social sharing
    og_title = Column(String(200), nullable=True, comment="Open Graph title for social sharing", info={"label": "Título OG"})
    og_description = Column(String(500), nullable=True, comment="Open Graph description for social sharing", info={"label": "Descripción OG"})
    og_image = Column(String(500), nullable=True, comment="Open Graph image URL for social sharing", info={"label": "Imagen OG (URL)"})
    og_url = Column(String(300), nullable=True, comment="Canonical URL for Open Graph", info={"label": "URL Canónica"})
    og_type = Column(String(50), nullable=True, default="website", comment="Open Graph type (website, profile, etc.)", info={"label": "Tipo OG"})
    
    # Twitter Card metadata
    twitter_card = Column(String(50), nullable=True, default="summary_large_image", comment="Twitter card type", info={"label": "Tipo de Twitter Card"})
    twitter_site = Column(String(100), nullable=True, comment="Twitter @username for website", info={"label": "Twitter del Sitio (@username)"})
    twitter_creator = Column(String(100), nullable=True, comment="Twitter @username for creator", info={"label": "Twitter del Creador (@username)"})
    twitter_title = Column(String(200), nullable=True, comment="Twitter card title", info={"label": "Título Twitter"})
    twitter_description = Column(String(500), nullable=True, comment="Twitter card description", info={"label": "Descripción Twitter"})
    twitter_image = Column(String(500), nullable=True, comment="Twitter card image URL", info={"label": "Imagen Twitter (URL)"})
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), info={"label": "Fecha de Creación"})
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), info={"label": "Última Actualización"})
    
    def __repr__(self):
        return f"<SiteConfig(site_title='{self.site_title}', brand_name='{self.brand_name}')>"
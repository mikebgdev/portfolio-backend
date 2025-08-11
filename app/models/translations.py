from sqlalchemy import Column, Integer, String, Text, DateTime, Index
from sqlalchemy.sql import func
from app.database import Base


class ContentTranslation(Base):
    """
    Table to store translations for all content types.
    
    This table supports the multilingual functionality by storing translations
    for text fields across different content types (about, skills, projects, etc.)
    """
    __tablename__ = "content_translations"

    id = Column(Integer, primary_key=True, index=True)
    content_type = Column(String(50), nullable=False)    # 'about', 'skill', 'project', 'experience', 'education'
    content_id = Column(Integer, nullable=False)         # ID of the original content record
    language_code = Column(String(5), nullable=False, default='en')  # 'en', 'es'
    field_name = Column(String(100), nullable=False)     # 'content', 'name', 'description', etc.
    translated_text = Column(Text, nullable=False)       # The actual translated content
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Indexes for efficient querying
    __table_args__ = (
        Index('idx_content_language', 'content_type', 'content_id', 'language_code'),
        Index('idx_content_field', 'content_type', 'content_id', 'field_name'),
        Index('idx_language_type', 'language_code', 'content_type'),
    )

    def __repr__(self):
        return f"<ContentTranslation({self.content_type}:{self.content_id}, {self.language_code}, {self.field_name})>"
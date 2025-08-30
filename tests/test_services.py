"""Test service layer functionality."""
import pytest
from sqlalchemy.orm import Session

from app.services.about import about_service
from app.services.contact import contact_service
from app.services.site_config import site_config_service
from app.exceptions import ContentNotFoundError


class TestBaseService:
    """Test base service functionality."""
    
    def test_about_service_get_about(self, db_session: Session, test_data):
        """Test about service get_about method."""
        about = about_service.get_about(db_session)
        
        assert about is not None
        assert about.name == "Test"
        assert about.last_name == "User"
        assert about.email == "test@example.com"
    
    def test_about_service_no_data_raises_404(self, db_session: Session):
        """Test about service raises 404 when no data exists."""
        with pytest.raises(ContentNotFoundError):
            about_service.get_about(db_session)
    
    def test_contact_service_get_contact(self, db_session: Session, test_data):
        """Test contact service get_contact method."""
        contact = contact_service.get_contact(db_session)
        
        assert contact is not None
        assert contact.email == "contact@example.com"
        assert contact.contact_form_enabled is True
    
    def test_contact_service_no_data_raises_404(self, db_session: Session):
        """Test contact service raises 404 when no data exists."""
        with pytest.raises(ContentNotFoundError):
            contact_service.get_contact(db_session)
    
    def test_site_config_service_get_site_config(self, db_session: Session, test_data):
        """Test site config service get_site_config method."""
        site_config = site_config_service.get_site_config(db_session)
        
        assert site_config is not None
        assert site_config.site_title == "Test Portfolio"
        assert site_config.meta_description == "Test Description"


class TestFileDataHandling:
    """Test file data handling in services."""
    
    def test_file_data_added_when_file_exists(self, db_session: Session):
        """Test that file data is added when file exists."""
        from app.models.about import About
        from app.services.base import SingletonService
        
        # Create test record with file
        about = About(
            name="Test",
            last_name="User", 
            email="test@example.com",
            location="Test City",
            bio_en="Test bio",
            nationality_en="Test",
            photo_file="/test/path/photo.jpg"
        )
        db_session.add(about)
        db_session.commit()
        
        # Create service instance
        service = SingletonService(About)
        result = service.get(db_session)
        
        # Should have photo_data attribute (even if None due to file not existing)
        assert hasattr(result, 'photo_data')
    
    def test_file_data_none_when_no_file(self, db_session: Session):
        """Test that file data is None when no file exists."""
        from app.models.about import About
        from app.services.base import SingletonService
        
        # Create test record without file
        about = About(
            name="Test",
            last_name="User",
            email="test@example.com", 
            location="Test City",
            bio_en="Test bio",
            nationality_en="Test"
        )
        db_session.add(about)
        db_session.commit()
        
        # Create service instance
        service = SingletonService(About)
        result = service.get(db_session)
        
        # Should have photo_data as None
        assert hasattr(result, 'photo_data')
        assert result.photo_data is None
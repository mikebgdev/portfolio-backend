import pytest
from unittest.mock import MagicMock
from sqlalchemy.orm import Session

from app.services.user import user_service
from app.services.content import about_service, skill_service, project_service
from app.models.user import User
from app.models.content import About, Skill, Project
from app.schemas.user import UserCreate
from app.schemas.content import AboutUpdate, SkillCreate, SkillUpdate


class TestUserService:
    """Test cases for UserService."""

    def test_get_user_by_email(self, db, test_user):
        """Test getting user by email."""
        user = user_service.get_user_by_email(db, test_user.email)
        assert user is not None
        assert user.email == test_user.email

    def test_get_user_by_email_not_found(self, db):
        """Test getting non-existent user by email."""
        user = user_service.get_user_by_email(db, "nonexistent@example.com")
        assert user is None

    def test_create_user(self, db):
        """Test creating a new user."""
        user_data = UserCreate(
            email="new@example.com",
            name="New User",
            role="admin"
        )
        user = user_service.create_user(db, user_data)
        
        assert user.id is not None
        assert user.email == "new@example.com"
        assert user.name == "New User"
        assert user.role == "admin"
        assert user.is_active is True

    def test_create_user_from_oauth(self, db):
        """Test creating user from OAuth data."""
        user = user_service.create_user_from_oauth(
            db, "oauth@example.com", "OAuth User"
        )
        
        assert user.email == "oauth@example.com"
        assert user.name == "OAuth User"
        assert user.role == "admin"
        assert user.is_active is True


class TestAboutService:
    """Test cases for AboutService."""

    def test_get_about_exists(self, db, sample_about_data):
        """Test getting existing about content."""
        # Create about record
        about = About(**sample_about_data)
        db.add(about)
        db.commit()
        
        result = about_service.get_about(db)
        assert result is not None
        assert result.content == sample_about_data["content"]

    def test_get_about_not_exists(self, db):
        """Test getting about content when none exists."""
        result = about_service.get_about(db)
        assert result is None

    def test_update_about_existing(self, db, sample_about_data):
        """Test updating existing about content."""
        # Create initial about record
        about = About(**sample_about_data)
        db.add(about)
        db.commit()
        
        # Update data
        from app.schemas.content import AboutUpdate
        update_data = AboutUpdate(content="Updated content")
        
        result = about_service.update_about(db, update_data)
        assert result.content == "Updated content"
        assert result.photo_url == sample_about_data["photo_url"]

    def test_update_about_create_new(self, db):
        """Test updating about content when none exists (creates new)."""
        from app.schemas.content import AboutUpdate
        update_data = AboutUpdate(content="New content")
        
        result = about_service.update_about(db, update_data)
        assert result.content == "New content"
        assert result.id is not None


class TestSkillService:
    """Test cases for SkillService."""

    def test_get_skills(self, db, sample_skill_data):
        """Test getting all skills."""
        # Create test skills
        skill1 = Skill(**sample_skill_data)
        skill2_data = sample_skill_data.copy()
        skill2_data["name"] = "JavaScript"
        skill2_data["level"] = 3
        skill2 = Skill(**skill2_data)
        
        db.add_all([skill1, skill2])
        db.commit()
        
        skills = skill_service.get_skills(db)
        assert len(skills) == 2
        # Should be ordered by level desc, then name
        assert skills[0].level >= skills[1].level

    def test_get_skills_filtered_by_type(self, db, sample_skill_data):
        """Test getting skills filtered by type."""
        # Create skills of different types
        tech_skill = Skill(**sample_skill_data)
        interpersonal_data = sample_skill_data.copy()
        interpersonal_data["name"] = "Communication"
        interpersonal_data["type"] = "interpersonal"
        interpersonal_skill = Skill(**interpersonal_data)
        
        db.add_all([tech_skill, interpersonal_skill])
        db.commit()
        
        tech_skills = skill_service.get_skills(db, skill_type="technical")
        assert len(tech_skills) == 1
        assert tech_skills[0].type == "technical"
        
        interpersonal_skills = skill_service.get_skills(db, skill_type="interpersonal")
        assert len(interpersonal_skills) == 1
        assert interpersonal_skills[0].type == "interpersonal"

    def test_create_skill(self, db, sample_skill_data):
        """Test creating a new skill."""
        skill_create = SkillCreate(**sample_skill_data)
        skill = skill_service.create_skill(db, skill_create)
        
        assert skill.id is not None
        assert skill.name == sample_skill_data["name"]
        assert skill.type == sample_skill_data["type"]
        assert skill.level == sample_skill_data["level"]

    def test_update_skill(self, db, sample_skill_data):
        """Test updating an existing skill."""
        # Create skill
        skill = Skill(**sample_skill_data)
        db.add(skill)
        db.commit()
        
        # Update skill
        update_data = SkillUpdate(name="Updated Python", level=4)
        updated_skill = skill_service.update_skill(db, skill.id, update_data)
        
        assert updated_skill.name == "Updated Python"
        assert updated_skill.level == 4
        assert updated_skill.type == sample_skill_data["type"]  # Unchanged

    def test_update_skill_not_found(self, db):
        """Test updating non-existent skill."""
        update_data = SkillUpdate(name="Updated")
        
        with pytest.raises(Exception) as exc_info:
            skill_service.update_skill(db, 999, update_data)
        
        assert exc_info.value.status_code == 404

    def test_delete_skill(self, db, sample_skill_data):
        """Test deleting a skill."""
        # Create skill
        skill = Skill(**sample_skill_data)
        db.add(skill)
        db.commit()
        skill_id = skill.id
        
        # Delete skill
        success = skill_service.delete_skill(db, skill_id)
        assert success is True
        
        # Verify deletion
        deleted_skill = db.query(Skill).filter(Skill.id == skill_id).first()
        assert deleted_skill is None

    def test_delete_skill_not_found(self, db):
        """Test deleting non-existent skill."""
        success = skill_service.delete_skill(db, 999)
        assert success is False
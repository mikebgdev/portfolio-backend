import pytest
from datetime import datetime
from sqlalchemy.exc import IntegrityError

from app.models.user import User
from app.models.content import About, Skill, Project, Experience, Education


class TestUserModel:
    """Test cases for User model."""

    def test_create_user(self, db):
        """Test creating a user with all fields."""
        user = User(
            email="test@example.com",
            name="Test User",
            role="admin",
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.name == "Test User"
        assert user.role == "admin"
        assert user.is_active is True
        assert user.created_at is not None

    def test_user_email_unique_constraint(self, db):
        """Test that email must be unique."""
        user1 = User(email="test@example.com", name="User 1")
        user2 = User(email="test@example.com", name="User 2")
        
        db.add(user1)
        db.commit()
        
        db.add(user2)
        with pytest.raises(IntegrityError):
            db.commit()

    def test_user_default_values(self, db):
        """Test default values for user fields."""
        user = User(email="test@example.com", name="Test User")
        db.add(user)
        db.commit()
        db.refresh(user)
        
        assert user.role == "admin"  # Default role
        assert user.is_active is True  # Default active state
        assert user.created_at is not None
        assert user.updated_at is None  # No update yet


class TestAboutModel:
    """Test cases for About model."""

    def test_create_about(self, db):
        """Test creating about content."""
        about = About(
            content="This is about me",
            photo_url="https://example.com/photo.jpg"
        )
        db.add(about)
        db.commit()
        db.refresh(about)
        
        assert about.id is not None
        assert about.content == "This is about me"
        assert about.photo_url == "https://example.com/photo.jpg"

    def test_about_content_required(self, db):
        """Test that content is required."""
        about = About(photo_url="https://example.com/photo.jpg")
        db.add(about)
        
        with pytest.raises(IntegrityError):
            db.commit()

    def test_about_photo_url_optional(self, db):
        """Test that photo_url is optional."""
        about = About(content="Content without photo")
        db.add(about)
        db.commit()
        db.refresh(about)
        
        assert about.photo_url is None


class TestSkillModel:
    """Test cases for Skill model."""

    def test_create_skill(self, db):
        """Test creating a skill."""
        skill = Skill(
            name="Python",
            type="technical",
            level=5
        )
        db.add(skill)
        db.commit()
        db.refresh(skill)
        
        assert skill.id is not None
        assert skill.name == "Python"
        assert skill.type == "technical"
        assert skill.level == 5
        assert skill.created_at is not None

    def test_skill_default_level(self, db):
        """Test default level for skills."""
        skill = Skill(name="JavaScript", type="technical")
        db.add(skill)
        db.commit()
        db.refresh(skill)
        
        assert skill.level == 1  # Default level

    def test_skill_required_fields(self, db):
        """Test that name and type are required."""
        skill = Skill(level=3)  # Missing name and type
        db.add(skill)
        
        with pytest.raises(IntegrityError):
            db.commit()


class TestProjectModel:
    """Test cases for Project model."""

    def test_create_project(self, db):
        """Test creating a project."""
        project = Project(
            name="Test Project",
            description="A test project",
            github_url="https://github.com/test/project",
            demo_url="https://demo.example.com",
            technologies='["Python", "FastAPI"]',
            image_url="https://example.com/image.jpg"
        )
        db.add(project)
        db.commit()
        db.refresh(project)
        
        assert project.id is not None
        assert project.name == "Test Project"
        assert project.github_url == "https://github.com/test/project"
        assert project.created_at is not None

    def test_project_required_fields(self, db):
        """Test that name, description, and github_url are required."""
        project = Project(demo_url="https://demo.example.com")
        db.add(project)
        
        with pytest.raises(IntegrityError):
            db.commit()

    def test_project_optional_fields(self, db):
        """Test that some fields are optional."""
        project = Project(
            name="Minimal Project",
            description="A minimal project",
            github_url="https://github.com/test/minimal"
        )
        db.add(project)
        db.commit()
        db.refresh(project)
        
        assert project.demo_url is None
        assert project.technologies is None
        assert project.image_url is None


class TestExperienceModel:
    """Test cases for Experience model."""

    def test_create_experience(self, db):
        """Test creating an experience record."""
        experience = Experience(
            company="Test Company",
            position="Developer",
            description="Developed software",
            start_date=datetime(2023, 1, 1),
            end_date=datetime(2023, 12, 31),
            location="Remote"
        )
        db.add(experience)
        db.commit()
        db.refresh(experience)
        
        assert experience.id is not None
        assert experience.company == "Test Company"
        assert experience.start_date == datetime(2023, 1, 1)

    def test_experience_current_position(self, db):
        """Test creating current position (end_date is None)."""
        experience = Experience(
            company="Current Company",
            position="Senior Developer",
            start_date=datetime(2023, 1, 1)
        )
        db.add(experience)
        db.commit()
        db.refresh(experience)
        
        assert experience.end_date is None  # Current position

    def test_experience_required_fields(self, db):
        """Test that company, position, and start_date are required."""
        experience = Experience(description="Some description")
        db.add(experience)
        
        with pytest.raises(IntegrityError):
            db.commit()


class TestEducationModel:
    """Test cases for Education model."""

    def test_create_education(self, db):
        """Test creating an education record."""
        education = Education(
            institution="Test University",
            degree="Bachelor of Science",
            field_of_study="Computer Science",
            start_date=datetime(2019, 9, 1),
            end_date=datetime(2023, 6, 30),
            gpa="3.8"
        )
        db.add(education)
        db.commit()
        db.refresh(education)
        
        assert education.id is not None
        assert education.institution == "Test University"
        assert education.degree == "Bachelor of Science"

    def test_education_ongoing(self, db):
        """Test creating ongoing education (end_date is None)."""
        education = Education(
            institution="Current University",
            degree="Master of Science",
            start_date=datetime(2023, 9, 1)
        )
        db.add(education)
        db.commit()
        db.refresh(education)
        
        assert education.end_date is None  # Ongoing education

    def test_education_optional_fields(self, db):
        """Test that some fields are optional."""
        education = Education(
            institution="Minimal University",
            degree="Some Degree",
            start_date=datetime(2020, 1, 1)
        )
        db.add(education)
        db.commit()
        db.refresh(education)
        
        assert education.field_of_study is None
        assert education.description is None
        assert education.location is None
        assert education.gpa is None
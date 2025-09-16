"""Test configuration and fixtures."""
import pytest
from datetime import date
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base
from app.deps.auth import get_db


# Test database URL - in-memory SQLite
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

# Create test engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# Create test session
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


# Override the dependency
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function")
def db_session():
    """Create test database tables and provide a database session."""
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create session
    session = TestingSessionLocal()
    
    try:
        yield session
    finally:
        session.close()
        # Drop all tables after test
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture(scope="function")
def test_data(db_session):
    """Create test data."""
    from app.models.about import About
    from app.models.contact import Contact
    from app.models.site_config import SiteConfig
    from app.models.projects import Project
    from app.models.skills import Skill, SkillCategory
    from app.models.experience import Experience
    from app.models.education import Education
    
    # Create test about record
    about = About(
        name="Test",
        last_name="User",
        email="test@example.com",
        location="Test City",
        bio_en="Test bio in English",
        bio_es="Test bio in Spanish",
        nationality_en="Test Nationality",
        nationality_es="Test Nacionalidad"
    )
    db_session.add(about)
    
    # Create test contact record
    contact = Contact(
        email="contact@example.com",
        linkedin_url="https://linkedin.com/in/test",
        github_url="https://github.com/test",
        contact_form_enabled=True,
        contact_message_en="Contact us in English",
        contact_message_es="Contáctanos en Español"
    )
    db_session.add(contact)
    
    # Create test site config
    site_config = SiteConfig(
        site_title="Test Portfolio",
        brand_name="Test Brand",
        meta_description="Test Description",
        og_title="Test OG Title",
        og_description="Test OG Description",
        og_url="https://test.com",
        og_type="website",
        twitter_card="summary",
        twitter_title="Test Twitter Title",
        twitter_description="Test Twitter Description"
    )
    db_session.add(site_config)
    
    # Create test skill category
    skill_category = SkillCategory(
        slug="test",
        label_en="Test Category",
        label_es="Categoría de Prueba",
        icon_name="TestIcon",
        display_order=1,
        active=True
    )
    db_session.add(skill_category)
    db_session.flush()  # Flush to get the ID
    
    # Create test skill
    skill = Skill(
        name_en="Test Skill",
        name_es="Habilidad de Prueba",
        category_id=skill_category.id,
        icon_name="TestSkillIcon",
        color="#FF0000",
        active=True
    )
    db_session.add(skill)
    
    # Create test project
    project = Project(
        title_en="Test Project",
        title_es="Proyecto de Prueba",
        description_en="Test project description",
        description_es="Descripción del proyecto de prueba",
        source_url="https://github.com/test/project",
        demo_url="https://test-project.com",
        display_order=1,
        activa=True
    )
    db_session.add(project)
    db_session.flush()  # Flush to get the project ID
    
    # Associate the project with the skill
    project.skills.append(skill)
    
    # Create test experience
    experience = Experience(
        company="Test Company",
        location="Test City",
        position_en="Test Position",
        position_es="Posición de Prueba",
        description_en="Test experience description",
        description_es="Descripción de experiencia de prueba",
        start_date=date(2022, 1, 1),
        end_date=date(2023, 1, 1),
        display_order=1,
        activo=True
    )
    db_session.add(experience)
    
    # Create test education
    education = Education(
        institution="Test University",
        location="Test City",
        degree_en="Test Degree",
        degree_es="Título de Prueba",
        start_date=date(2020, 1, 1),
        end_date=date(2022, 1, 1),
        display_order=1,
        activo=True
    )
    db_session.add(education)
    
    db_session.commit()
    
    return {
        "about": about,
        "contact": contact,
        "site_config": site_config,
        "skill_category": skill_category,
        "skill": skill,
        "project": project,
        "experience": experience,
        "education": education
    }
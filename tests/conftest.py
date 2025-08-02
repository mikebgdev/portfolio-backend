import pytest
import asyncio
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db
from app.models.user import User
from app.models.content import About, Skill, Project, Experience, Education
from app.auth.oauth import auth_service
from app.deps.auth import get_current_user, get_current_admin_user

# Test database URL (SQLite in memory for speed)
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
def db():
    """Create a fresh database for each test."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    """Create a test client with database dependency override."""
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db):
    """Create a test user."""
    user = User(
        email="test@example.com",
        name="Test User",
        role="admin",
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def admin_token(test_user):
    """Create a valid admin JWT token."""
    token_data = {
        "sub": test_user.email,
        "user_id": test_user.id
    }
    return auth_service.create_access_token(token_data)


@pytest.fixture
def auth_headers(admin_token):
    """Create authorization headers with admin token."""
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture
def authenticated_client(client, auth_headers):
    """Create a client with authentication headers."""
    client.headers.update(auth_headers)
    return client


@pytest.fixture
def mock_current_user(test_user):
    """Mock the current user dependency."""
    def override_get_current_user():
        return test_user
    
    def override_get_current_admin_user():
        return test_user
    
    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[get_current_admin_user] = override_get_current_admin_user
    yield test_user
    app.dependency_overrides.clear()


@pytest.fixture
def sample_about_data():
    """Sample about data for testing."""
    return {
        "content": "This is a test about section content.",
        "photo_url": "https://example.com/photo.jpg"
    }


@pytest.fixture
def sample_skill_data():
    """Sample skill data for testing."""
    return {
        "name": "Python",
        "type": "technical",
        "level": 5
    }


@pytest.fixture
def sample_project_data():
    """Sample project data for testing."""
    return {
        "name": "Test Project",
        "description": "A test project for portfolio",
        "github_url": "https://github.com/test/project",
        "demo_url": "https://demo.example.com",
        "technologies": '["Python", "FastAPI", "PostgreSQL"]',
        "image_url": "https://example.com/project.jpg"
    }


@pytest.fixture
def sample_experience_data():
    """Sample experience data for testing."""
    from datetime import datetime
    return {
        "company": "Test Company",
        "position": "Software Developer",
        "description": "Developed awesome software",
        "start_date": datetime(2023, 1, 1),
        "end_date": datetime(2023, 12, 31),
        "location": "Remote"
    }


@pytest.fixture
def sample_education_data():
    """Sample education data for testing."""
    from datetime import datetime
    return {
        "institution": "Test University",
        "degree": "Bachelor of Science",
        "field_of_study": "Computer Science",
        "description": "Studied computer science fundamentals",
        "start_date": datetime(2019, 9, 1),
        "end_date": datetime(2023, 6, 30),
        "location": "Test City",
        "gpa": "3.8"
    }
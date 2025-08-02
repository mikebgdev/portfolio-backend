# 🚀 Portfolio Backend

[![CI/CD Status](https://github.com/mikebgdev/portfolio-backend/actions/workflows/ci.yml/badge.svg)](https://github.com/mikebgdev/portfolio-backend/actions/workflows/ci.yml)
[![Security Status](https://github.com/mikebgdev/portfolio-backend/actions/workflows/security.yml/badge.svg)](https://github.com/mikebgdev/portfolio-backend/actions/workflows/security.yml)
[![Coverage](https://img.shields.io/badge/coverage-80%2B-brightgreen)](./htmlcov/index.html)
[![Python](https://img.shields.io/badge/python-3.11+-blue)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## 🌟 Project Overview

A **production-ready, enterprise-grade backend API** built with FastAPI and PostgreSQL, designed to power modern portfolio websites with comprehensive content management capabilities. This system provides secure Google OAuth authentication, RESTful API endpoints for all portfolio sections, and a complete admin interface for seamless content updates.

### ✨ **Key Highlights**
- 🔐 **Enterprise Security**: Google OAuth 2.0 + JWT with role-based access control
- ⚡ **High Performance**: FastAPI with async/await, optimized database queries
- 🧪 **Quality Assured**: 80%+ test coverage with comprehensive test suite
- 🐳 **Container Ready**: Docker development and production configurations
- 🔄 **CI/CD Pipeline**: Automated testing, security scanning, and deployment
- 📊 **Observability**: Structured logging, health checks, and performance metrics
- 📚 **Auto Documentation**: Interactive OpenAPI/Swagger documentation
- 🛡️ **Security First**: Vulnerability scanning, input validation, security headers

### 🎯 **Built For**
- **Portfolio Websites**: Complete content management for personal portfolios
- **Developers**: Modern Python development with type hints and best practices  
- **Enterprises**: Scalable architecture with monitoring and security
- **Teams**: Comprehensive testing, documentation, and deployment automation

## Tech Stack & Architecture

### Core Technologies
- **FastAPI**: Modern, fast web framework for building APIs with Python 3.7+
- **PostgreSQL**: Robust relational database for data persistence
- **SQLAlchemy**: Python SQL toolkit and Object-Relational Mapping (ORM)
- **Pydantic**: Data validation and settings management using Python type annotations
- **Alembic**: Database migration tool for SQLAlchemy
- **Python-JOSE**: JavaScript Object Signing and Encryption library for JWT handling

### Authentication & Security
- **Google OAuth 2.0**: Secure authentication provider integration
- **JWT Tokens**: Stateless authentication with role-based access control
- **Passlib**: Password hashing and verification utilities
- **CORS Middleware**: Cross-origin resource sharing configuration
- **Security Headers**: Comprehensive security header implementation

### Architecture Patterns
The application follows a layered architecture with clear separation of concerns:

```
app/
├── main.py              # Application entry point and configuration
├── routers/             # API route definitions
│   ├── auth.py
│   ├── about.py
│   ├── skills.py
│   ├── projects.py
│   ├── experience.py
│   └── education.py
├── models/              # SQLAlchemy database models
├── schemas/             # Pydantic models for request/response
├── services/            # Business logic and service functions
├── deps/                # Dependency injection utilities
├── auth/                # Authentication and authorization logic
├── config.py            # Configuration management
└── database.py          # Database connection and session management
```

### Database Design
The database schema is designed for flexibility and performance:
- **Users**: Admin user management with role-based permissions
- **About**: Personal information and bio content
- **Skills**: Technical and interpersonal skills with categorization
- **Projects**: GitHub project integration with demo links
- **Experience**: Work history with detailed descriptions
- **Education**: Academic background and certifications

### API Design Principles
- RESTful endpoints with consistent naming conventions
- Comprehensive input validation with Pydantic models
- Standardized error responses with detailed error codes
- Automatic API documentation generation
- Version-controlled API with backward compatibility

## Setup Instructions

### Prerequisites
- Python 3.9+ with pip
- PostgreSQL 12+ database server
- Google OAuth 2.0 credentials
- Git for version control
- Docker (optional for containerized deployment)

### Local Development Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd portfolio-backend
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Environment Configuration**
Create a `.env` file in the root directory:
```env
# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/portfolio_db
POSTGRES_USER=portfolio_user
POSTGRES_PASSWORD=secure_password
POSTGRES_DB=portfolio_db

# Authentication
SECRET_KEY=your-super-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Google OAuth
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# Application Settings
DEBUG=True
CORS_ORIGINS=["http://localhost:3000", "http://localhost:5173"]
```

5. **Database Setup**
```bash
# Create database (if not exists)
createdb portfolio_db

# Run migrations
alembic upgrade head

# Seed initial data (optional)
python scripts/seed_data.py
```

6. **Start development server**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000` with automatic documentation at `http://localhost:8000/docs`

### Docker Development Setup

1. **Build and run with Docker Compose**
```bash
docker-compose up --build
```

2. **Run database migrations in container**
```bash
docker-compose exec backend alembic upgrade head
```

### Production Deployment

1. **Set production environment variables**
```bash
export DEBUG=False
export DATABASE_URL=postgresql://prod_user:prod_password@db_host:5432/portfolio_prod
```

2. **Install production dependencies**
```bash
pip install -r requirements-prod.txt
```

3. **Run with production WSGI server**
```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Available Scripts
- `uvicorn app.main:app --reload`: Start development server
- `pytest`: Run unit tests
- `pytest --cov`: Run tests with coverage report
- `alembic revision --autogenerate -m "message"`: Create new migration
- `alembic upgrade head`: Apply database migrations
- `python scripts/seed_data.py`: Seed initial data

## Implementation Guide

### Database Models Implementation

#### User Model
```python
# models/user.py
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    role = Column(String, default="admin")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

#### Content Models
```python
# models/content.py
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database import Base

class About(Base):
    __tablename__ = "about"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    photo_url = Column(String, nullable=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)  # 'technical' or 'interpersonal'
    level = Column(Integer, default=1)  # 1-5 proficiency level
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    github_url = Column(String, nullable=False)
    demo_url = Column(String, nullable=True)
    technologies = Column(String, nullable=True)  # JSON string
    image_url = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
```

### Pydantic Schemas
```python
# schemas/content.py
from pydantic import BaseModel, HttpUrl
from typing import Optional, List
from datetime import datetime

class AboutBase(BaseModel):
    content: str
    photo_url: Optional[HttpUrl] = None

class AboutCreate(AboutBase):
    pass

class AboutUpdate(AboutBase):
    content: Optional[str] = None

class AboutResponse(AboutBase):
    id: int
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True

class SkillBase(BaseModel):
    name: str
    type: str
    level: Optional[int] = 1

class SkillCreate(SkillBase):
    pass

class SkillUpdate(SkillBase):
    name: Optional[str] = None
    type: Optional[str] = None

class SkillResponse(SkillBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True
```

### API Router Implementation
```python
# routers/about.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.deps import get_db, get_current_admin_user
from app.schemas.content import AboutResponse, AboutUpdate
from app.services.content import about_service

router = APIRouter(prefix="/about", tags=["about"])

@router.get("/", response_model=AboutResponse)
async def get_about(db: Session = Depends(get_db)):
    """Get about section content."""
    about = about_service.get_about(db)
    if not about:
        raise HTTPException(status_code=404, detail="About content not found")
    return about

@router.put("/", response_model=AboutResponse)
async def update_about(
    about_data: AboutUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    """Update about section content (admin only)."""
    updated_about = about_service.update_about(db, about_data)
    return updated_about
```

### Service Layer Implementation
```python
# services/content.py
from sqlalchemy.orm import Session
from app.models.content import About, Skill, Project
from app.schemas.content import AboutUpdate, SkillCreate, ProjectCreate
from typing import List, Optional

class AboutService:
    def get_about(self, db: Session) -> Optional[About]:
        return db.query(About).first()

    def update_about(self, db: Session, about_data: AboutUpdate) -> About:
        about = self.get_about(db)
        if not about:
            # Create new about record if none exists
            about = About()
            db.add(about)

        update_data = about_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(about, field, value)

        db.commit()
        db.refresh(about)
        return about

class SkillService:
    def get_skills(self, db: Session) -> List<Skill]:
        return db.query(Skill).all()

    def create_skill(self, db: Session, skill_data: SkillCreate) -> Skill:
        skill = Skill(**skill_data.dict())
        db.add(skill)
        db.commit()
        db.refresh(skill)
        return skill

    def update_skill(self, db: Session, skill_id: int, skill_data: SkillUpdate) -> Skill:
        skill = db.query(Skill).filter(Skill.id == skill_id).first()
        if not skill:
            raise HTTPException(status_code=404, detail="Skill not found")

        update_data = skill_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(skill, field, value)

        db.commit()
        db.refresh(skill)
        return skill

    def delete_skill(self, db: Session, skill_id: int) -> bool:
        skill = db.query(Skill).filter(Skill.id == skill_id).first()
        if not skill:
            return False

        db.delete(skill)
        db.commit()
        return True

# Service instances
about_service = AboutService()
skill_service = SkillService()
```

### Authentication Implementation
```python
# auth/oauth.py
from fastapi import HTTPException, status
from google.auth.transport import requests
from google.oauth2 import id_token
import jwt
from datetime import datetime, timedelta
from app.config import settings

class AuthService:
    def verify_google_token(self, token: str) -> dict:
        try:
            idinfo = id_token.verify_oauth2_token(
                token, requests.Request(), settings.GOOGLE_CLIENT_ID
            )
            return idinfo
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Google token"
            )

    def create_access_token(self, data: dict) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        
        encoded_jwt = jwt.encode(
            to_encode, 
            settings.SECRET_KEY, 
            algorithm=settings.ALGORITHM
        )
        return encoded_jwt

    def verify_token(self, token: str) -> dict:
        try:
            payload = jwt.decode(
                token, 
                settings.SECRET_KEY, 
                algorithms=[settings.ALGORITHM]
            )
            return payload
        except jwt.PyJWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )

auth_service = AuthService()
```

### Dependency Injection
```python
# deps.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.auth.oauth import auth_service
from app.models.user import User

security = HTTPBearer()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    token = credentials.credentials
    payload = auth_service.verify_token(token)
    
    email = payload.get("sub")
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
    
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user

def get_current_admin_user(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user
```

## API Documentation & Testing

### OpenAPI Documentation
FastAPI automatically generates comprehensive API documentation available at:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI JSON**: `http://localhost:8000/openapi.json`

### API Endpoints Overview

#### Authentication Endpoints
```python
POST /api/v1/auth/login
Content-Type: application/json

{
  "google_token": "google_oauth_token_here"
}

Response:
{
  "access_token": "jwt_token_here",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "admin@example.com",
    "name": "Admin User",
    "role": "admin"
  }
}
```

#### Content Management Endpoints
```python
# Get about content
GET /api/v1/about

# Update about content (admin only)
PUT /api/v1/about
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "content": "Updated about content",
  "photo_url": "https://example.com/photo.jpg"
}

# Get all skills
GET /api/v1/skills

# Create new skill (admin only)
POST /api/v1/skills
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "name": "Python",
  "type": "technical",
  "level": 5
}
```

### Error Response Format
```python
{
  "detail": "Error message",
  "error_code": "SPECIFIC_ERROR_CODE",
  "timestamp": "2023-12-01T10:00:00Z"
}
```

### Unit Testing Examples
```python
# tests/test_about.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_get_about():
    response = client.get("/api/v1/about")
    assert response.status_code == 200
    assert "content" in response.json()

def test_update_about_unauthorized():
    response = client.put("/api/v1/about", json={"content": "New content"})
    assert response.status_code == 401

def test_update_about_authorized(admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.put(
        "/api/v1/about",
        json={"content": "Updated content"},
        headers=headers
    )
    assert response.status_code == 200
    assert response.json()["content"] == "Updated content"

# tests/test_skills.py
def test_create_skill(admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    skill_data = {
        "name": "React",
        "type": "technical",
        "level": 4
    }
    response = client.post("/api/v1/skills", json=skill_data, headers=headers)
    assert response.status_code == 201
    assert response.json()["name"] == "React"

def test_get_skills():
    response = client.get("/api/v1/skills")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
```

## Testing & Deployment

### Testing Strategy
```python
# conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session")
def db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client(db):
    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()

@pytest.fixture
def admin_token():
    # Mock admin token for testing
    return "mock_admin_token"
```

### Production Deployment Configuration
```python
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["gunicorn", "app.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
```

### Health Check Implementation
```python
# routers/health.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.deps import get_db

router = APIRouter()

@router.get("/health")
async def health_check(db: Session = Depends(get_db)):
    try:
        # Test database connection
        db.execute("SELECT 1")
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }
```

The backend is production-ready with comprehensive logging, monitoring, and deployment configurations for scalable hosting environments.
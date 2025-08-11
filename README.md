# 🚀 Portfolio Backend

[![CI Status](https://github.com/mikebgdev/portfolio-backend/actions/workflows/ci.yml/badge.svg)](https://github.com/mikebgdev/portfolio-backend/actions/workflows/ci.yml)
[![Security Status](https://github.com/mikebgdev/portfolio-backend/actions/workflows/security.yml/badge.svg)](https://github.com/mikebgdev/portfolio-backend/actions/workflows/security.yml)
[![Python](https://img.shields.io/badge/python-3.11+-blue)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## 🌟 Overview

A **modern portfolio backend** built with FastAPI and PostgreSQL, centered around a powerful **admin panel** for easy content management. Perfect for developers who want a clean, simple API with a beautiful interface to manage their portfolio data.

### ✨ **Key Features**
- 🎛️ **Beautiful Admin Panel**: SQLAdmin interface for easy content management
- 🔓 **Public API**: GET endpoints accessible without authentication
- 🔐 **Secure Admin**: Username/password authentication for content updates
- ⚡ **FastAPI**: Modern, fast API framework with automatic documentation
- 🗄️ **PostgreSQL**: Reliable database with migrations
- 🚀 **Simple Deployment**: Single command startup, no Docker required

### 🎯 **Perfect For**
- **Portfolio Websites**: Manage your professional content easily
- **Developers**: Clean API + admin panel = productivity
- **Simple Projects**: No complex setup, just run and use

## 🏗️ Architecture

### Tech Stack
- **FastAPI**: API framework with automatic docs
- **SQLAdmin**: Beautiful admin panel for content management
- **PostgreSQL**: Database with SQLAlchemy ORM
- **Alembic**: Database migrations
- **Python-JOSE + Passlib**: Secure authentication

### Security Model
- **GET endpoints**: Public (for frontend consumption)
- **POST/PUT/DELETE**: Admin authentication required
- **Admin Panel**: Same credentials as API
- **Password hashing**: bcrypt for secure storage

### Project Structure
```
app/
├── admin.py          # Admin panel configuration
├── main.py           # FastAPI application
├── config.py         # Settings and environment variables
├── database.py       # Database connection
├── models/           # SQLAlchemy models
├── routers/          # API endpoints
├── schemas/          # Pydantic schemas
├── services/         # Business logic
└── utils/            # Utilities (admin setup, etc.)
```

## 🚀 Quick Start

### 1. Environment Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your database credentials
```

### 2. Database Setup

```bash
# Run migrations
alembic upgrade head
```

### 3. Admin User Setup

**Option A: Automatic (default user)**
```bash
# Start the application (creates default admin if none exists)
uvicorn app.main:app --host 0.0.0.0 --port 8000
# Default credentials: admin@portfolio.com / admin123
```

**Option B: Interactive setup**
```bash
# Run interactive setup
python setup_admin.py
```

### 4. Access Your Portfolio

- **API Documentation**: http://localhost:8000/docs
- **Admin Panel**: http://localhost:8000/admin/
- **Health Check**: http://localhost:8000/health

## 🎛️ Admin Panel

The admin panel is the heart of this system, providing:

- **📝 Content Management**: Easy editing of all portfolio sections
- **👥 User Management**: Admin user management
- **🔍 Search & Filter**: Quick content discovery
- **📊 Clean Interface**: Professional, intuitive design
- **🔐 Secure Access**: Same authentication as API

### Admin Panel Sections
- **About**: Personal information and bio
- **Skills**: Technical and interpersonal skills
- **Projects**: Portfolio projects with links
- **Experience**: Work history
- **Education**: Academic background
- **Users**: Admin user management

## 🔌 API Endpoints

### Public Endpoints (No Authentication)
```
GET /api/v1/about/          # Get about information
GET /api/v1/skills/         # Get all skills
GET /api/v1/projects/       # Get all projects
GET /api/v1/experience/     # Get work experience
GET /api/v1/education/      # Get education history
```

### Admin Endpoints (Authentication Required)
```
POST /api/v1/auth/login     # Admin login
POST /api/v1/skills/        # Create skill
PUT  /api/v1/skills/{id}    # Update skill
DELETE /api/v1/skills/{id}  # Delete skill
# ... similar for all content types
```

### Authentication
```bash
# Login
curl -X POST "http://localhost:8000/api/v1/auth/login" \
     -H "Content-Type: application/json" \
     -d '{"username": "admin@portfolio.com", "password": "admin123"}'

# Use returned token
curl -H "Authorization: Bearer YOUR_TOKEN" \
     "http://localhost:8000/api/v1/skills/"
```

## 🗄️ Database Configuration

### Environment Variables
```env
# Database
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=your_user
POSTGRES_PASSWORD=your_password
POSTGRES_DB=portfolio_db

# Security
SECRET_KEY=your-secret-key-here
```

### Migrations
```bash
# Create migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Check current version
alembic current
```

## 🚀 Deployment

### Development
```bash
export PATH=$PATH:~/.local/bin
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Production
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### With Process Manager (PM2)
```bash
pm2 start "uvicorn app.main:app --host 0.0.0.0 --port 8000" --name portfolio-api
```

## 🔧 Configuration

### Settings (app/config.py)
- **Database**: PostgreSQL connection settings
- **Authentication**: JWT settings and secrets
- **CORS**: Cross-origin settings for frontend
- **Debug**: Development/production mode

### Admin Panel Customization
- Modify `app/admin.py` to customize admin interface
- Add/remove models from admin panel
- Customize list views, forms, and permissions

## 📚 Documentation

- **API Docs**: Auto-generated at `/docs` (Swagger UI)
- **ReDoc**: Alternative docs at `/redoc`
- **Admin Help**: Built-in help in admin panel

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/my-feature`
3. Commit changes: `git commit -am 'Add feature'`
4. Push to branch: `git push origin feature/my-feature`
5. Submit pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/mikebgdev/portfolio-backend/issues)
- **Documentation**: Check `/docs` endpoint when running
- **Admin Panel**: Built-in help and intuitive interface

---

**Made with ❤️ and FastAPI**
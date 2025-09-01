# Portfolio Backend API

[![CI](https://github.com/mikebgdev/portfolio-backend/actions/workflows/ci.yml/badge.svg)](https://github.com/mikebgdev/portfolio-backend/actions/workflows/ci.yml)
[![Security](https://github.com/mikebgdev/portfolio-backend/actions/workflows/security.yml/badge.svg)](https://github.com/mikebgdev/portfolio-backend/actions/workflows/security.yml)
![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)

A robust, production-ready FastAPI backend for personal portfolio websites with comprehensive monitoring, security, and deployment features.

## ✨ Features

### Core Features
- **🌍 Multilingual Support**: Complete English and Spanish content management
- **🎨 Iconify Integration**: Comprehensive icon and color management system with 100+ technology presets
- **📁 File Management**: Base64-encoded file serving with admin upload capabilities
- **🏗️ Clean Architecture**: Service layer pattern with dependency injection
- **📚 Auto Documentation**: Interactive Swagger UI and ReDoc interfaces

### Security & Performance  
- **🔒 Enterprise Security**: Rate limiting, input sanitization, security headers, CORS protection
- **⚡ Smart Caching**: Environment-aware caching (production only)
- **🛡️ Middleware Stack**: Comprehensive security, monitoring, and performance middleware
- **🔍 Request Monitoring**: Performance tracking and structured logging

### Administration & Deployment
- **👨‍💼 Enhanced Admin Panel**: SQLAdmin with smart tooltips, icon previews, and real-time validation
- **🎯 Smart Form Fields**: Automatic color suggestions for popular technologies
- **📧 Email System**: Multilingual contact forms with Gmail SMTP integration
- **🐳 Docker Ready**: Multi-stage Dockerfile optimized for production
- **🚀 CI/CD Pipeline**: Automated testing, security scanning, and deployment
- **📊 Health Monitoring**: Built-in health checks and metrics collection

## 🚀 Quick Start

Choose your preferred deployment method:

### Option 1: Docker (Recommended)

```bash
# Clone and configure
git clone https://github.com/mikebgdev/portfolio-backend.git
cd portfolio-backend

# Configure environment
cp .env.production.example .env
# Edit .env with your settings

# Start with Docker Compose
docker-compose up -d

# Run database migrations
docker-compose exec app alembic upgrade head
```

### Option 2: Local Development

```bash
# Setup environment
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure database
cp .env.example .env
# Edit .env with PostgreSQL credentials

# Setup database
createdb portfolio_db
alembic upgrade head

# Start development server
uvicorn app.main:app --reload
```

### Option 3: Coolify Deployment

```yaml
# Deploy directly to Coolify with:
version: '3.8'
services:
  app:
    image: ghcr.io/mikebgdev/portfolio-backend:latest
    environment:
      - POSTGRES_HOST=your-db-host
      - SECRET_KEY=your-secret-key
      - ENVIRONMENT=production
```

### 🎯 Access Points

- **🔧 Admin Panel**: http://localhost:8000/admin
- **📚 API Docs**: http://localhost:8000/docs  
- **🌐 API Base**: http://localhost:8000/api/v1/
- **❤️ Health Check**: http://localhost:8000/admin/

## 📋 API Reference

### Core Endpoints

All endpoints support `?lang=en|es` for multilingual content and return Base64-encoded file data.

| Endpoint | Method | Description | Features |
|----------|--------|-------------|----------|
| `/api/v1/site-config/` | GET | Site metadata & social sharing | SEO optimization |
| `/api/v1/about/` | GET | Personal bio & information | Photo uploads |
| `/api/v1/contact/` | GET | Contact details & CV | File downloads |
| `/api/v1/skills/` | GET | Skills grouped by categories | Iconify integration |
| `/api/v1/projects/` | GET | Portfolio projects | Image galleries |
| `/api/v1/experience/` | GET | Work experience timeline | Date sorting |
| `/api/v1/education/` | GET | Education records | Ongoing support |

### Iconify Features
| Endpoint | Description | Purpose |
|----------|-------------|---------|
| `/api/v1/iconify/tooltip` | Icon validation & suggestions | Smart admin tooltips |
| `/api/v1/iconify/search` | Search technology icons | Find appropriate icons |
| `/api/v1/iconify/categories` | Popular icon categories | Browse icon collections |
| `/api/v1/iconify/validate-color` | Color format validation | Ensure valid colors |

**📖 Complete Documentation**: [docs/api/API_DOCUMENTATION.md](./docs/api/API_DOCUMENTATION.md) | **🎨 Iconify Guide**: [docs/iconify/README.md](./docs/iconify/README.md)

## ⚙️ Configuration

### Environment Variables

Create `.env` file (copy from `.env.example`):

```bash
# Environment (controls cache behavior)
ENVIRONMENT=development  # development|production

# Database
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your-password
POSTGRES_DB=portfolio_db

# Security (required)
SECRET_KEY=your-super-secure-secret-key-at-least-32-characters-long

# CORS (environment-aware)
CORS_ORIGINS=["*"]  # Development (permissive)
# CORS_ORIGINS=["https://yourdomain.com"]  # Production (restrictive)

# Optional settings
RATE_LIMIT_PER_MINUTE=100
MAX_UPLOAD_SIZE=10485760
```

### Smart Caching System

**Environment-Based Caching:**
- **Development** (`ENVIRONMENT=development`): Cache **DISABLED** - always fresh data
- **Production** (`ENVIRONMENT=production`): Cache **ENABLED** - high performance

No manual cache management needed - the system adapts automatically!

### CORS Configuration

**Environment-Based CORS:**
- **Development** (`ENVIRONMENT=development`): CORS **PERMISSIVE** - accepts all origins (`["*"]`)
- **Production** (`ENVIRONMENT=production`): CORS **RESTRICTIVE** - only specified domains

For production, set specific domains:
```bash
CORS_ORIGINS=["https://yourdomain.com", "https://www.yourdomain.com"]
```

### Admin Panel

The admin panel is automatically available at `/admin` with:
- ✅ **Auto Admin Creation**: Creates default admin user on first run
- ✅ **Spanish Interface**: Localized labels and forms
- ✅ **Content Management**: CRUD operations for all portfolio content
- ✅ **User-Friendly**: Intuitive interface for non-technical users

## 🏗️ Project Structure

```
app/
├── admin/          # Admin interface configuration
├── models/         # Database models (SQLAlchemy)
├── routers/        # API endpoints (FastAPI)
├── schemas/        # Data validation (Pydantic)  
├── services/       # Business logic
├── middleware/     # Security, performance, monitoring
├── utils/          # Utilities (cache, validation, logging)
├── config.py       # Application configuration
├── main.py         # Application entry point
└── database.py     # Database connection
```

## 🔧 Development

### Development Commands

```bash
# Start development server with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run all tests with coverage
pytest tests/ -v --tb=short

# Code quality checks
black app/ --check              # Format checking
isort app/ --check              # Import sorting
flake8 app/ --max-line-length=100  # Linting
mypy app/ --ignore-missing-imports  # Type checking

# Database operations
alembic revision --autogenerate -m "Description"  # Create migration
alembic upgrade head                               # Apply migrations
alembic downgrade -1                              # Rollback last migration

# Docker development
docker-compose up -d          # Start services
docker-compose logs -f app    # View logs
docker-compose exec app bash  # Shell access
```

### Testing

```bash
# Run specific test categories
pytest tests/test_api_endpoints.py -v    # API tests
pytest tests/test_services.py -v         # Service layer tests
pytest -m "not slow"                     # Skip slow tests

# Test with different environments
ENVIRONMENT=testing pytest tests/       # Testing environment
DEBUG=true pytest tests/                # Debug mode
```

### Adding Content

Use the admin panel at `/admin` to:
- Add/edit personal information
- Manage skills and categories
- Add portfolio projects
- Update work experience
- Modify education records
- Configure site metadata

## 🚀 Production Deployment

### Docker Production Setup

```bash
# Build production image
docker build -t portfolio-backend:prod .

# Run with production config
docker run -d \
  --name portfolio-api \
  -p 8000:8000 \
  -e ENVIRONMENT=production \
  -e SECRET_KEY=your-secure-key \
  -e POSTGRES_HOST=your-db-host \
  portfolio-backend:prod
```

### Coolify Deployment

1. **Create new project** in Coolify
2. **Set repository**: `https://github.com/mikebgdev/portfolio-backend`
3. **Configure environment**:
   ```env
   ENVIRONMENT=production
   SECRET_KEY=your-32-char-secret
   POSTGRES_HOST=your-postgres-host
   POSTGRES_PASSWORD=secure-password
   CORS_ORIGINS=https://yourdomain.com
   ```
4. **Deploy**: Coolify auto-builds and deploys

### Manual Production Setup  

```bash
# Install production dependencies
pip install gunicorn

# Run with multiple workers
gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --access-logfile - \
  --error-logfile -
```

## 📚 Documentation

- **📖 API Documentation**: [docs/api/API_DOCUMENTATION.md](./docs/api/API_DOCUMENTATION.md)
- **🎨 Iconify System**: [docs/iconify/README.md](./docs/iconify/README.md)
- **🛠️ Admin Guide**: [docs/iconify/admin-guide.md](./docs/iconify/admin-guide.md)
- **📚 Interactive API Docs**: `/docs` (Swagger UI)  
- **📚 Alternative API Docs**: `/redoc` (ReDoc)
- **🎯 Admin Help**: Built-in tooltips and smart validation

## 🔒 Security Features

- **Rate Limiting**: Protection against abuse
- **CORS Protection**: Configurable cross-origin policies
- **Input Sanitization**: XSS and injection prevention
- **Security Headers**: Comprehensive header configuration
- **Session Security**: Secure admin authentication

## 📊 Monitoring

- **Health Checks**: `/health` endpoint
- **Performance Metrics**: Built-in monitoring
- **Structured Logging**: JSON logs for analysis
- **Request Tracking**: Performance monitoring

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/my-feature`
3. Commit changes: `git commit -am 'Add feature'`
4. Push to branch: `git push origin feature/my-feature`
5. Submit pull request

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Issues**: Check logs and verify configuration
- **API Docs**: Visit `/docs` when running
- **Admin Panel**: Built-in help and intuitive interface

---

**Made with ❤️ and FastAPI**
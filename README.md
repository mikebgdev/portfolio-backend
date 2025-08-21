# Portfolio Backend API

A robust FastAPI-based REST API for personal portfolio websites with multilingual support, admin panel, and automatic environment-based caching.

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13+-blue.svg)

## ✨ Features

- **🌍 Multilingual**: English and Spanish content support
- **👨‍💼 Admin Panel**: SQLAdmin interface with Spanish localization
- **⚡ Smart Caching**: Automatic cache in production, disabled in development
- **🔒 Security**: Rate limiting, CORS, input sanitization, security headers
- **📊 Monitoring**: Health checks, metrics, and performance tracking
- **📚 Auto Docs**: Swagger UI and ReDoc integration

## 🚀 Quick Start

### 1. Environment Setup

```bash
# Clone repository
git clone <repository-url>
cd portfolio-backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your database credentials

# Key configuration for development:
# ENVIRONMENT=development  # This disables cache automatically
# POSTGRES_HOST=localhost
# SECRET_KEY=your-secure-key-here
```

### 2. Database Setup

```bash
# Create database
createdb portfolio_db

# Run migrations
alembic upgrade head
```

### 3. Start Application

```bash
# Development
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 4. Access

- **API**: http://localhost:8000/api/v1/
- **Admin Panel**: http://localhost:8000/admin (auto-creates admin user)
- **API Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

## 📋 API Endpoints

All endpoints support `?lang=en|es` parameter for multilingual content.

### Public API (`/api/v1/`)

- `GET /site-config/` - Site configuration and social media metadata
- `GET /about/` - Personal information and biography
- `GET /contact/` - Contact information and social links
- `GET /skills/` - Skills grouped by categories
- `GET /projects/` - Portfolio projects list
- `GET /projects/{id}` - Specific project details
- `GET /experience/` - Work experience records
- `GET /experience/{id}` - Specific experience details
- `GET /education/` - Education records
- `GET /education/{id}` - Specific education details

Complete API documentation: [API_DOCUMENTATION.md](./API_DOCUMENTATION.md)

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

### Common Commands

```bash
# Start development server
uvicorn app.main:app --reload

# Run tests  
pytest

# Create database migration
alembic revision --autogenerate -m "Description"

# Apply migration
alembic upgrade head

# Check code style
flake8 app/
black app/ --check
```

### Adding Content

Use the admin panel at `/admin` to:
- Add/edit personal information
- Manage skills and categories
- Add portfolio projects
- Update work experience
- Modify education records
- Configure site metadata

## 🚀 Deployment

### Production Setup

1. **Environment Configuration**:
```bash
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=production-secure-key
CORS_ORIGINS=["https://yourdomain.com"]
```

2. **Database Setup**:
```bash
# Production database
createdb portfolio_prod
alembic upgrade head
```

3. **Run with Gunicorn**:
```bash
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### Docker Deployment

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 📚 Documentation

- **API Documentation**: [API_DOCUMENTATION.md](./API_DOCUMENTATION.md)
- **Interactive API Docs**: `/docs` (Swagger UI)  
- **Alternative API Docs**: `/redoc` (ReDoc)
- **Admin Help**: Built-in help in admin panel

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
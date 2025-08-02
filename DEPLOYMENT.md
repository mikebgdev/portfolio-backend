# Portfolio Backend Deployment Guide

## Quick Start

### Local Development

1. **Clone and setup**:
```bash
git clone <repository-url>
cd portfolio-backend
cp .env.example .env
# Edit .env with your configuration
```

2. **Run with Docker Compose**:
```bash
docker-compose up --build
```

3. **Access the API**:
- API: http://localhost:8000
- Documentation: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

### Production Deployment

1. **Set environment variables**:
```bash
export SECRET_KEY="your-production-secret-key"
export GOOGLE_CLIENT_ID="your-google-client-id"
export GOOGLE_CLIENT_SECRET="your-google-client-secret"
export POSTGRES_USER="portfolio_user"
export POSTGRES_PASSWORD="secure-production-password"
export CORS_ORIGINS='["https://your-frontend-domain.com"]'
```

2. **Deploy with production Docker Compose**:
```bash
docker-compose -f docker-compose.prod.yml up -d
```

3. **Run database migrations**:
```bash
docker-compose exec backend alembic upgrade head
```

4. **Seed initial data**:
```bash
docker-compose exec backend python scripts/seed_data.py
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Required |
| `SECRET_KEY` | JWT signing secret | Required |
| `GOOGLE_CLIENT_ID` | Google OAuth client ID | Required |
| `GOOGLE_CLIENT_SECRET` | Google OAuth client secret | Required |
| `DEBUG` | Enable debug mode | `False` |
| `CORS_ORIGINS` | Allowed CORS origins | `[]` |

## API Endpoints

### Authentication
- `POST /api/v1/auth/login` - Login with Google OAuth
- `GET /api/v1/auth/me` - Get current user info
- `GET /api/v1/auth/status` - Check auth status

### Content Management
- `GET /api/v1/about` - Get about content
- `PUT /api/v1/about` - Update about content (admin)
- `GET /api/v1/skills` - Get all skills
- `POST /api/v1/skills` - Create skill (admin)
- `GET /api/v1/projects` - Get all projects
- `POST /api/v1/projects` - Create project (admin)

### Database Management
- `GET /health` - Health check with DB status

## Security

- Google OAuth 2.0 authentication
- JWT token-based access control
- Admin-only endpoints protected
- CORS configuration
- SQL injection prevention via SQLAlchemy ORM

## Monitoring

The application includes:
- Health check endpoint at `/health`
- Database connectivity testing
- Structured error responses
- Request/response logging (in debug mode)
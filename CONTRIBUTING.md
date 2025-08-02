# Contributing to Portfolio Backend

Thank you for your interest in contributing to the Portfolio Backend project! This document provides guidelines and information for contributors.

## 🤝 How to Contribute

### Types of Contributions
- 🐛 **Bug Reports**: Help us identify and fix issues
- ✨ **Feature Requests**: Suggest new functionality
- 📚 **Documentation**: Improve or add documentation
- 🧪 **Testing**: Add or improve test coverage
- 🔧 **Code**: Fix bugs or implement new features
- 🛡️ **Security**: Report security vulnerabilities (see SECURITY.md)

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- Docker and Docker Compose
- Git
- PostgreSQL (for local development)

### Development Setup

1. **Fork and Clone**
```bash
git clone https://github.com/yourusername/portfolio-backend.git
cd portfolio-backend
```

2. **Environment Setup**
```bash
# Copy environment template
cp .env.example .env

# Configure Google OAuth credentials
# Edit .env with your development credentials
```

3. **Start Development Environment**
```bash
# Using Docker (Recommended)
docker-compose up --build

# Or local development
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements-test.txt
```

4. **Initialize Database**
```bash
# With Docker
docker-compose exec backend alembic upgrade head
docker-compose exec backend python scripts/seed_data.py

# Local development
alembic upgrade head
python scripts/seed_data.py
```

5. **Verify Setup**
```bash
# Run tests
pytest

# Check API
curl http://localhost:8000/health
```

## 📝 Development Guidelines

### Code Style
- **Python Style**: Follow PEP 8 with Black formatter
- **Import Sorting**: Use isort for import organization
- **Type Hints**: Use type hints for all functions and methods
- **Docstrings**: Use Google-style docstrings for functions and classes

### Code Quality Tools
```bash
# Format code
black .
isort .

# Type checking
mypy app

# Linting
flake8 app tests

# Security scanning
bandit -r app/
```

### Git Workflow

1. **Create Feature Branch**
```bash
git checkout -b feature/your-feature-name
# or
git checkout -b bugfix/issue-description
```

2. **Make Changes**
- Write code following the style guidelines
- Add or update tests
- Update documentation if needed

3. **Test Your Changes**
```bash
# Run all tests
pytest

# Run specific test types
pytest -m unit
pytest -m integration

# Check coverage
pytest --cov=app --cov-report=html
```

4. **Commit Changes**
```bash
git add .
git commit -m "feat: add user profile management

- Add user profile CRUD operations
- Implement profile validation
- Add comprehensive tests
- Update API documentation

Closes #123"
```

### Commit Message Convention
We use [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or modifying tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(auth): add Google OAuth integration
fix(api): resolve validation error in skills endpoint
docs: update deployment guide with Docker instructions
test: add integration tests for authentication flow
```

### Testing Guidelines

#### Test Structure
```
tests/
├── unit/                    # Unit tests
│   ├── test_auth.py        # Authentication logic
│   ├── test_services.py    # Business logic
│   └── test_models.py      # Database models
└── integration/             # Integration tests
    ├── test_auth_api.py    # Authentication API
    ├── test_content_api.py # Content management API
    └── test_database.py    # Database operations
```

#### Writing Tests
- **Unit Tests**: Test individual functions and methods in isolation
- **Integration Tests**: Test API endpoints and database operations
- **Use Fixtures**: Leverage pytest fixtures for common setup
- **Mock External Dependencies**: Mock Google OAuth and external services
- **Test Edge Cases**: Include error conditions and boundary cases

#### Test Example
```python
def test_create_skill_success(authenticated_client, sample_skill_data):
    """Test successful skill creation with valid data."""
    response = authenticated_client.post("/api/v1/skills", json=sample_skill_data)
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == sample_skill_data["name"]
    assert data["type"] == sample_skill_data["type"]
```

### Documentation Standards

#### Code Documentation
```python
def create_user(db: Session, user_data: UserCreate) -> User:
    """Create a new user in the database.
    
    Args:
        db: Database session
        user_data: User creation data with validation
        
    Returns:
        Created user instance
        
    Raises:
        HTTPException: If user creation fails
    """
```

#### API Documentation
- Use FastAPI's automatic documentation features
- Add comprehensive docstrings to all endpoints
- Include example requests and responses
- Document error cases and status codes

## 🔍 Pull Request Process

### Before Submitting
- [ ] Tests pass locally (`pytest`)
- [ ] Code follows style guidelines (`black`, `isort`, `flake8`)
- [ ] Type checking passes (`mypy`)
- [ ] Security scan passes (`bandit`)
- [ ] Documentation updated if needed
- [ ] Commit messages follow convention

### Pull Request Template
When creating a pull request, include:

1. **Description**: Clear description of changes
2. **Issue Reference**: Link to related issues
3. **Type of Change**: Bug fix, feature, documentation, etc.
4. **Testing**: How you tested your changes
5. **Checklist**: Completed checklist items

### Review Process
1. **Automated Checks**: CI/CD pipeline runs automatically
2. **Code Review**: Maintainers review code and provide feedback
3. **Testing**: Additional testing if needed
4. **Approval**: Required approval from maintainers
5. **Merge**: Squash merge into main branch

## 🐛 Reporting Issues

### Bug Reports
Include the following information:
- **Description**: Clear description of the bug
- **Steps to Reproduce**: Detailed steps to reproduce the issue
- **Expected Behavior**: What you expected to happen
- **Actual Behavior**: What actually happened
- **Environment**: Python version, OS, Docker version, etc.
- **Logs**: Relevant error messages or logs

### Feature Requests
Include the following information:
- **Problem Statement**: What problem does this solve?
- **Proposed Solution**: How would you like it to work?
- **Alternatives**: Alternative solutions considered
- **Additional Context**: Any other relevant information

## 🛡️ Security

For security vulnerabilities, please follow our [Security Policy](SECURITY.md):
- **DO NOT** open public issues for security vulnerabilities
- Email security@mikebg.dev with details
- Follow responsible disclosure practices

## 📚 Resources

### Documentation
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [pytest Documentation](https://docs.pytest.org/)
- [Docker Documentation](https://docs.docker.com/)

### Project Documentation
- [Deployment Guide](DEPLOYMENT.md)
- [Testing Guide](TESTING.md)
- [Security Policy](SECURITY.md)
- [API Documentation](http://localhost:8000/docs)

## 💬 Community

### Getting Help
- **GitHub Issues**: For bugs and feature requests
- **GitHub Discussions**: For questions and general discussion
- **Email**: For security issues and private concerns

### Code of Conduct
This project follows the [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/). Please be respectful and inclusive in all interactions.

## 🎉 Recognition

Contributors will be recognized in:
- Project README
- Release notes
- GitHub contributors page

Thank you for contributing to Portfolio Backend! 🚀
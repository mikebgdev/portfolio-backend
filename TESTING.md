# Testing Guide

## Overview

This project includes comprehensive testing with pytest, covering unit tests, integration tests, and API endpoint testing.

## Test Structure

```
tests/
├── conftest.py              # Test configuration and fixtures
├── unit/                    # Unit tests
│   ├── test_auth.py        # Authentication service tests
│   ├── test_services.py    # Business logic tests
│   └── test_models.py      # Database model tests
└── integration/             # Integration tests
    ├── test_auth_api.py    # Authentication API tests
    ├── test_content_api.py # Content management API tests
    └── test_database.py    # Database integration tests
```

## Running Tests

### Prerequisites

```bash
# Install test dependencies
pip install -r requirements-test.txt
```

### Basic Test Execution

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test types
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only
pytest -m auth          # Authentication tests only
```

### Advanced Test Options

```bash
# Run tests with detailed output
pytest -v

# Run tests and generate HTML coverage report
pytest --cov=app --cov-report=html

# Run tests with specific pattern
pytest tests/unit/test_auth.py::TestAuthService::test_create_access_token

# Run tests and stop on first failure
pytest -x

# Run tests in parallel (requires pytest-xdist)
pytest -n auto
```

## Test Categories

### Unit Tests
- **Authentication**: JWT token creation/validation, Google OAuth integration
- **Services**: Business logic for content management, user operations
- **Models**: Database model validation, constraints, relationships

### Integration Tests
- **API Endpoints**: Full request/response cycle testing
- **Database Operations**: Transaction handling, cascade operations
- **Authentication Flow**: End-to-end auth workflow testing

## Test Configuration

### Environment Variables

Tests use SQLite in-memory database by default. Configuration is handled in `conftest.py`:

```python
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
```

### Test Data

Sample data fixtures are provided in `conftest.py`:
- `test_user`: Admin user for authentication testing
- `sample_*_data`: Sample data for content models
- `admin_token`: Valid JWT token for admin operations

## Writing New Tests

### Unit Test Example

```python
def test_new_feature(db, sample_data):
    """Test description."""
    # Arrange
    service = MyService()
    
    # Act
    result = service.process(sample_data)
    
    # Assert
    assert result.success is True
    assert result.data == expected_data
```

### Integration Test Example

```python
def test_api_endpoint(authenticated_client, sample_data):
    """Test API endpoint with authentication."""
    response = authenticated_client.post("/api/v1/endpoint", json=sample_data)
    
    assert response.status_code == 201
    assert response.json()["field"] == sample_data["field"]
```

## Test Fixtures

### Database Fixtures
- `db`: Fresh database session for each test
- `client`: FastAPI test client
- `authenticated_client`: Client with admin authentication

### Authentication Fixtures
- `test_user`: Test user with admin role
- `admin_token`: Valid JWT token
- `auth_headers`: Authorization headers
- `mock_current_user`: Mock authenticated user dependency

### Data Fixtures
- `sample_about_data`: About section data
- `sample_skill_data`: Skill data with type and level
- `sample_project_data`: Project data with GitHub URL
- `sample_experience_data`: Work experience data
- `sample_education_data`: Education record data

## Mocking

### Google OAuth Mocking

```python
@patch('app.auth.oauth.auth_service.verify_google_token')
def test_google_auth(mock_verify_google, client):
    mock_verify_google.return_value = {
        'email': 'test@example.com',
        'name': 'Test User'
    }
    # Test implementation
```

### Database Mocking

```python
def test_with_mock_db(mock_current_user):
    # Uses dependency override for authentication
    # Database operations use test database
```

## Coverage Requirements

- Minimum coverage: 80%
- Target coverage: 90%+
- Critical paths (auth, security): 95%+

## Continuous Integration

Tests run automatically on:
- Pull requests to main branch
- Pushes to main/develop branches
- Nightly security scans

CI pipeline includes:
- Unit and integration tests
- Code coverage reporting
- Security vulnerability scanning
- Code quality checks (linting, formatting)

## Test Data Management

### Creating Test Data

```python
# Use factories for complex objects
def create_test_user(email="test@example.com"):
    return User(email=email, name="Test User", role="admin")

# Use fixtures for reusable data
@pytest.fixture
def sample_project():
    return Project(name="Test Project", ...)
```

### Database State

Each test gets a fresh database:
- Tables created before each test
- All data cleaned up after each test
- No test interference

## Debugging Tests

### Failed Test Investigation

```bash
# Run with verbose output
pytest -v -s

# Run single failing test
pytest tests/path/to/test.py::test_name -v

# Run with debugger
pytest --pdb tests/path/to/test.py::test_name
```

### Common Issues

1. **Database State**: Ensure tests clean up properly
2. **Authentication**: Use provided fixtures for auth testing
3. **Async Operations**: Use `pytest-asyncio` for async tests
4. **Mocking**: Patch the correct import path

## Performance Testing

For performance testing:

```bash
# Time-based testing
pytest --durations=10  # Show 10 slowest tests

# Memory usage
pytest --profile      # Requires pytest-profiling
```

## Best Practices

1. **Test Isolation**: Each test should be independent
2. **Clear Names**: Test names should describe what they test
3. **AAA Pattern**: Arrange, Act, Assert
4. **Single Responsibility**: One assertion per test when possible
5. **Use Fixtures**: Reuse common setup code
6. **Mock External Dependencies**: Don't test external services
7. **Test Edge Cases**: Include boundary conditions and error cases
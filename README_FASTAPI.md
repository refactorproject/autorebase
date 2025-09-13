# AutoRebase FastAPI Integration

A FastAPI application for processing GitHub SHAs and software versioning operations.

## Features

- **GitHub SHA Processing**: Validate and process three GitHub SHAs (Base Software 0, Base Software 1, Feature Software 0)
- **Dynamic Repository URLs**: Accept repository URLs in API requests (no config files needed)
- **RESTful API**: Clean REST endpoints with automatic documentation
- **Input Validation**: Pydantic models for robust input validation
- **Error Handling**: Comprehensive error handling and validation
- **Health Checks**: Built-in health monitoring endpoints
- **Comprehensive Testing**: Unit tests, integration tests, and manual tests

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Application

```bash
python main.py
```

The API will be available at:
- **API**: http://localhost:8000
- **Documentation**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 3. Test the API

#### Using curl:

```bash
curl -X POST "http://localhost:8000/github/input-repos" \
     -H "Content-Type: application/json" \
     -d '{
       "base_software_0": "abc123def456",
       "base_software_1": "def456ghi789", 
       "feature_software_0": "ghi789jkl012",
       "base_repo_url": "https://github.com/microsoft/vscode.git",
       "feature_repo_url": "https://github.com/microsoft/vscode.git"
     }'
```

#### Using the interactive docs:

Visit http://localhost:8000/docs and use the Swagger UI to test the endpoints.

## API Endpoints

### POST `/github/input-repos`

Process three GitHub SHAs with their repository URLs and validate them against their respective repositories.

**Request Body:**
```json
{
  "base_software_0": "abc123def456",
  "base_software_1": "def456ghi789",
  "feature_software_0": "ghi789jkl012",
  "base_repo_url": "https://github.com/microsoft/vscode.git",
  "feature_repo_url": "https://github.com/microsoft/vscode.git"
}
```

**Response:**
```json
{
  "success": true,
  "message": "All GitHub SHAs validated successfully",
  "base_software_0": "abc123def456",
  "base_software_1": "def456ghi789", 
  "feature_software_0": "ghi789jkl012",
  "base_repo_url": "https://github.com/microsoft/vscode.git",
  "feature_repo_url": "https://github.com/microsoft/vscode.git",
  "processing_details": {
    "base_0_info": {...},
    "base_1_info": {...},
    "feature_0_info": {...}
  }
}
```

### GET `/github/health`

Health check endpoint for the GitHub service.

### GET `/health`

Overall API health check.

## Development

### Running in Development Mode

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Running Tests

The project includes comprehensive tests to ensure nothing breaks during development:

#### **Unit Tests**
```bash
# Run all unit tests
pytest tests/test_models.py tests/test_services.py -v

# Run specific test file
pytest tests/test_models.py -v

# Run with coverage
pytest tests/ --cov=api --cov-report=html
```

#### **Integration Tests**
```bash
# Run integration tests
pytest tests/test_api_endpoints.py -v

# Run all tests
pytest tests/ -v
```

#### **Manual Tests (requires running server)**
```bash
# Start the server first
python main.py

# In another terminal, run manual tests
python tests/test_api.py
# or
python run_tests.py manual
```

#### **Test Runner Script**
```bash
# Run all automated tests
python run_tests.py

# Run manual tests (requires running server)
python run_tests.py manual
```

#### **Test Structure**
```
tests/
├── __init__.py              # Test package
├── conftest.py              # Pytest fixtures and configuration
├── test_models.py           # Unit tests for Pydantic models
├── test_services.py          # Unit tests for GitHub service
├── test_api_endpoints.py    # Integration tests for API endpoints
└── test_api.py              # Manual tests (requires running server)
```

## Project Structure

```
autorebase/
├── api/
│   ├── models/
│   │   └── github_models.py      # Pydantic models
│   ├── routers/
│   │   └── github_router.py      # API routes
│   └── services/
│       └── github_service.py     # Business logic
├── config/
│   └── repos.yaml                # Repository configuration
├── data/
│   ├── repos/                    # Repository import directories
│   └── sample/                   # Sample data
├── scripts/
│   ├── import_repos.py           # Python import script
│   ├── import_repos.sh           # Shell import script
│   └── import_from_config.py     # YAML config import script
├── tests/                        # Comprehensive test suite
├── main.py                       # FastAPI application
├── run_tests.py                  # Test runner script
├── requirements.txt              # Dependencies
├── pytest.ini                   # Pytest configuration
└── README_FASTAPI.md             # This file
```

## Repository Import

The project includes utilities to import repositories for processing:

### Method 1: Using YAML Configuration (Recommended)

1. **Update the configuration file:**
   ```bash
   # Edit config/repos.yaml
   nano config/repos.yaml
   ```

2. **Update repository URLs and tags:**
   ```yaml
   repositories:
     base:
       url: "https://github.com/your-org/base-repo.git"
       tags:
         base-0: "base-0"
         base-1: "base-1"
     
     feature:
       url: "https://github.com/your-org/feature-repo.git"
       tags:
         feature-0: "feature-0"
   ```

3. **Run the import script:**
   ```bash
   python scripts/import_from_config.py
   ```

### Method 2: Using Shell Script

1. **Update the script variables:**
   ```bash
   # Edit scripts/import_repos.sh
   nano scripts/import_repos.sh
   ```

2. **Update these variables:**
   ```bash
   BASE_REPO_URL="https://github.com/your-org/base-repo.git"
   FEATURE_REPO_URL="https://github.com/your-org/feature-repo.git"
   BASE_0_TAG="base-0"
   BASE_1_TAG="base-1"
   FEATURE_0_TAG="feature-0"
   ```

3. **Run the import script:**
   ```bash
   ./scripts/import_repos.sh
   ```

## Configuration

The API uses environment variables for configuration. Create a `.env` file:

```env
GITHUB_API_BASE=https://api.github.com
API_TIMEOUT=30
```

## Error Handling

The API provides comprehensive error handling:

- **400 Bad Request**: Invalid input or validation errors
- **422 Unprocessable Entity**: Pydantic validation errors
- **500 Internal Server Error**: Unexpected server errors
- **Detailed Error Messages**: Clear error descriptions in responses

## Sample Data

The `data/sample/` directory contains sample files for testing and development:

- `base-1.0/`, `base-1.1/`, `feature-5.0/`: Sample software versions
- `sw0.py`, `sw1.py`, `fsw0.py`, `fsw1.py`: Sample Python files
- `requirements_map.yaml`: Requirements mapping

## Testing Strategy

The project uses a comprehensive testing strategy:

1. **Unit Tests**: Test individual components in isolation
2. **Integration Tests**: Test API endpoints with mocked dependencies
3. **Manual Tests**: Test against running server instance
4. **Continuous Integration**: Automated testing in GitHub Actions

## License

This project is part of the AutoRebase system for automated software rebasing and version management.

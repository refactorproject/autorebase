"""
Pytest configuration and fixtures for AutoRebase API tests
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
import httpx

from main import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI application"""
    return TestClient(app)


@pytest.fixture
def mock_github_response():
    """Mock successful GitHub API response"""
    return {
        "sha": "abc123def456",
        "commit": {
            "message": "Test commit message",
            "author": {
                "name": "Test Author",
                "date": "2024-01-01T00:00:00Z"
            }
        }
    }


@pytest.fixture
def mock_github_error_response():
    """Mock GitHub API error response"""
    return {
        "message": "Not Found",
        "documentation_url": "https://docs.github.com/rest"
    }


@pytest.fixture
def valid_request_data():
    """Valid request data for testing"""
    return {
        "base_software_0": "abc123def456",
        "base_software_1": "def456ghi789",
        "feature_software_0": "ghi789jkl012",
        "base_repo_url": "https://github.com/microsoft/vscode.git",
        "feature_repo_url": "https://github.com/microsoft/vscode.git"
    }


@pytest.fixture
def invalid_request_data():
    """Invalid request data for testing"""
    return {
        "base_software_0": "invalid_sha",
        "base_software_1": "def456ghi789",
        "feature_software_0": "ghi789jkl012",
        "base_repo_url": "not-a-github-url",
        "feature_repo_url": "https://github.com/microsoft/vscode.git"
    }

"""
Unit tests for Pydantic models
"""

import pytest
from pydantic import ValidationError

from api.models.github_models import GitHubSHARequest, GitHubSHAResponse


class TestGitHubSHARequest:
    """Test cases for GitHubSHARequest model"""
    
    def test_valid_request(self):
        """Test valid request data"""
        data = {
            "base_software_0": "abc123def456",
            "base_software_1": "def456ghi789",
            "feature_software_0": "ghi789jkl012",
            "base_repo_url": "https://github.com/microsoft/vscode.git",
            "feature_repo_url": "https://github.com/microsoft/vscode.git"
        }
        
        request = GitHubSHARequest(**data)
        
        assert request.base_software_0 == "abc123def456"
        assert request.base_software_1 == "def456ghi789"
        assert request.feature_software_0 == "ghi789jkl012"
        assert request.base_repo_url == "https://github.com/microsoft/vscode.git"
        assert request.feature_repo_url == "https://github.com/microsoft/vscode.git"
    
    def test_invalid_sha_format(self):
        """Test invalid SHA format"""
        data = {
            "base_software_0": "invalid_sha",
            "base_software_1": "def456ghi789",
            "feature_software_0": "ghi789jkl012",
            "base_repo_url": "https://github.com/microsoft/vscode.git",
            "feature_repo_url": "https://github.com/microsoft/vscode.git"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            GitHubSHARequest(**data)
        
        assert "string does not match regex" in str(exc_info.value)
    
    def test_short_sha(self):
        """Test SHA that's too short"""
        data = {
            "base_software_0": "abc123",  # Too short
            "base_software_1": "def456ghi789",
            "feature_software_0": "ghi789jkl012",
            "base_repo_url": "https://github.com/microsoft/vscode.git",
            "feature_repo_url": "https://github.com/microsoft/vscode.git"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            GitHubSHARequest(**data)
        
        assert "at least 7 characters" in str(exc_info.value)
    
    def test_invalid_repo_url(self):
        """Test invalid repository URL"""
        data = {
            "base_software_0": "abc123def456",
            "base_software_1": "def456ghi789",
            "feature_software_0": "ghi789jkl012",
            "base_repo_url": "not-a-github-url",
            "feature_repo_url": "https://github.com/microsoft/vscode.git"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            GitHubSHARequest(**data)
        
        assert "string does not match regex" in str(exc_info.value)
    
    def test_missing_fields(self):
        """Test missing required fields"""
        data = {
            "base_software_0": "abc123def456",
            "base_software_1": "def456ghi789",
            # Missing feature_software_0
            "base_repo_url": "https://github.com/microsoft/vscode.git",
            "feature_repo_url": "https://github.com/microsoft/vscode.git"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            GitHubSHARequest(**data)
        
        assert "field required" in str(exc_info.value)


class TestGitHubSHAResponse:
    """Test cases for GitHubSHAResponse model"""
    
    def test_successful_response(self):
        """Test successful response"""
        data = {
            "success": True,
            "message": "All GitHub SHAs validated successfully",
            "base_software_0": "abc123def456",
            "base_software_1": "def456ghi789",
            "feature_software_0": "ghi789jkl012",
            "base_repo_url": "https://github.com/microsoft/vscode.git",
            "feature_repo_url": "https://github.com/microsoft/vscode.git",
            "processing_details": {
                "base_0_info": {"valid": True},
                "base_1_info": {"valid": True},
                "feature_0_info": {"valid": True}
            }
        }
        
        response = GitHubSHAResponse(**data)
        
        assert response.success is True
        assert response.message == "All GitHub SHAs validated successfully"
        assert response.base_software_0 == "abc123def456"
        assert response.base_software_1 == "def456ghi789"
        assert response.feature_software_0 == "ghi789jkl012"
        assert response.base_repo_url == "https://github.com/microsoft/vscode.git"
        assert response.feature_repo_url == "https://github.com/microsoft/vscode.git"
        assert response.processing_details is not None
    
    def test_error_response(self):
        """Test error response"""
        data = {
            "success": False,
            "message": "Validation failed",
            "base_software_0": "abc123def456",
            "base_software_1": "def456ghi789",
            "feature_software_0": "ghi789jkl012",
            "base_repo_url": "https://github.com/microsoft/vscode.git",
            "feature_repo_url": "https://github.com/microsoft/vscode.git"
        }
        
        response = GitHubSHAResponse(**data)
        
        assert response.success is False
        assert response.message == "Validation failed"
        assert response.processing_details is None

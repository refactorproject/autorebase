"""
Integration tests for API endpoints
"""

import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient


class TestAPIEndpoints:
    """Test cases for API endpoints"""
    
    def test_root_endpoint(self, client):
        """Test root endpoint"""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "AutoRebase API"
        assert data["version"] == "1.0.0"
        assert "/docs" in data["docs"]
    
    def test_health_endpoint(self, client):
        """Test health endpoint"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "AutoRebase API"
    
    def test_github_root_endpoint(self, client):
        """Test GitHub router root endpoint"""
        response = client.get("/github/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "GitHub SHA Processing API"
        assert data["version"] == "1.0.0"
        assert "input_repos" in data["endpoints"]
        assert "health" in data["endpoints"]
    
    def test_github_health_endpoint(self, client):
        """Test GitHub service health endpoint"""
        response = client.get("/github/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "GitHub SHA Processor"
    
    @patch('api.services.github_service.GitHubService.process_shas')
    def test_input_repos_success(self, mock_process_shas, client, valid_request_data):
        """Test successful input-repos endpoint"""
        # Mock successful response
        mock_response = {
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
        mock_process_shas.return_value = mock_response
        
        response = client.post("/github/input-repos", json=valid_request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "All GitHub SHAs validated successfully" in data["message"]
        assert data["base_software_0"] == "abc123def456"
        assert data["base_software_1"] == "def456ghi789"
        assert data["feature_software_0"] == "ghi789jkl012"
    
    @patch('api.services.github_service.GitHubService.process_shas')
    def test_input_repos_validation_failure(self, mock_process_shas, client, valid_request_data):
        """Test input-repos endpoint with validation failure"""
        # Mock validation failure response
        mock_response = {
            "success": False,
            "message": "Validation failed: Base Software 0: Commit not found",
            "base_software_0": "abc123def456",
            "base_software_1": "def456ghi789",
            "feature_software_0": "ghi789jkl012",
            "base_repo_url": "https://github.com/microsoft/vscode.git",
            "feature_repo_url": "https://github.com/microsoft/vscode.git",
            "processing_details": {
                "validation_errors": ["Base Software 0: Commit not found"]
            }
        }
        mock_process_shas.return_value = mock_response
        
        response = client.post("/github/input-repos", json=valid_request_data)
        
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "Validation failed" in data["detail"]
    
    def test_input_repos_invalid_data(self, client):
        """Test input-repos endpoint with invalid data"""
        invalid_data = {
            "base_software_0": "invalid_sha",  # Invalid SHA format
            "base_software_1": "def456ghi789",
            "feature_software_0": "ghi789jkl012",
            "base_repo_url": "not-a-github-url",  # Invalid URL
            "feature_repo_url": "https://github.com/microsoft/vscode.git"
        }
        
        response = client.post("/github/input-repos", json=invalid_data)
        
        assert response.status_code == 422  # Validation error
        data = response.json()
        assert "detail" in data
    
    def test_input_repos_missing_fields(self, client):
        """Test input-repos endpoint with missing fields"""
        incomplete_data = {
            "base_software_0": "abc123def456",
            "base_software_1": "def456ghi789",
            # Missing feature_software_0
            "base_repo_url": "https://github.com/microsoft/vscode.git",
            "feature_repo_url": "https://github.com/microsoft/vscode.git"
        }
        
        response = client.post("/github/input-repos", json=incomplete_data)
        
        assert response.status_code == 422  # Validation error
        data = response.json()
        assert "detail" in data
    
    @patch('api.services.github_service.GitHubService.process_shas')
    def test_input_repos_server_error(self, mock_process_shas, client, valid_request_data):
        """Test input-repos endpoint with server error"""
        # Mock exception
        mock_process_shas.side_effect = Exception("Internal server error")
        
        response = client.post("/github/input-repos", json=valid_request_data)
        
        assert response.status_code == 500
        data = response.json()
        assert "detail" in data
        assert "Internal server error" in data["detail"]

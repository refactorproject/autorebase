"""
Tests for AutoRebase functionality
"""

import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient

from main import app
from api.models.autorebase_models import AutoRebaseRequest, AutoRebaseResponse
from api.services.autorebase_service import AutoRebaseService
from api.autorebase.core import AutoRebase


class TestAutoRebaseModels:
    """Test cases for AutoRebase models"""
    
    def test_valid_autorebase_request(self):
        """Test valid AutoRebase request"""
        data = {
            "base_software_0": "abc123def456",
            "base_software_1": "def456ghi789",
            "feature_software_0": "ghi789jkl012",
            "base_repo_url": "https://github.com/microsoft/vscode.git",
            "feature_repo_url": "https://github.com/microsoft/vscode.git",
            "work_dir": "data/repos"
        }
        
        request = AutoRebaseRequest(**data)
        
        assert request.base_software_0 == "abc123def456"
        assert request.base_software_1 == "def456ghi789"
        assert request.feature_software_0 == "ghi789jkl012"
        assert request.base_repo_url == "https://github.com/microsoft/vscode.git"
        assert request.feature_repo_url == "https://github.com/microsoft/vscode.git"
        assert request.work_dir == "data/repos"


class TestAutoRebaseCore:
    """Test cases for AutoRebase core functionality"""
    
    @pytest.fixture
    def autorebase(self):
        """Create AutoRebase instance"""
        return AutoRebase(work_dir="test_repos")
    
    @pytest.mark.asyncio
    async def test_autorebase_initialization(self, autorebase):
        """Test AutoRebase initialization"""
        assert autorebase.work_dir.name == "test_repos"
        assert autorebase.base_0_dir.name == "base-0"
        assert autorebase.base_1_dir.name == "base-1"
        assert autorebase.feature_0_dir.name == "feature-0"
    
    @pytest.mark.asyncio
    async def test_run_autorebase_placeholder(self, autorebase):
        """Test autorebase placeholder functionality"""
        result = await autorebase.run_autorebase()
        
        assert result["success"] is True
        assert "placeholder" in result["message"]
        assert "base_0_dir" in result["details"]
        assert "base_1_dir" in result["details"]
        assert "feature_0_dir" in result["details"]


class TestAutoRebaseService:
    """Test cases for AutoRebase service"""
    
    @pytest.fixture
    def service(self):
        """Create AutoRebaseService instance"""
        return AutoRebaseService()
    
    @pytest.fixture
    def valid_request(self):
        """Create valid AutoRebase request"""
        return AutoRebaseRequest(
            base_software_0="abc123def456",
            base_software_1="def456ghi789",
            feature_software_0="ghi789jkl012",
            base_repo_url="https://github.com/microsoft/vscode.git",
            feature_repo_url="https://github.com/microsoft/vscode.git",
            work_dir="test_repos"
        )
    
    @pytest.mark.asyncio
    async def test_process_autorebase_success(self, service, valid_request):
        """Test successful autorebase processing"""
        # Mock the AutoRebase.process_repositories method
        mock_results = {
            "success": True,
            "message": "Complete process finished successfully",
            "clone_results": {
                "success": True,
                "results": {
                    "base_0": {"success": True, "message": "Cloned", "directory": "test_repos/base-0", "sha": "abc123def456"},
                    "base_1": {"success": True, "message": "Cloned", "directory": "test_repos/base-1", "sha": "def456ghi789"},
                    "feature_0": {"success": True, "message": "Cloned", "directory": "test_repos/feature-0", "sha": "ghi789jkl012"}
                }
            },
            "autorebase_results": {
                "success": True,
                "message": "AutoRebase completed",
                "details": {"status": "success"}
            }
        }
        
        with patch('api.autorebase.core.AutoRebase.process_repositories', return_value=mock_results):
            result = await service.process_autorebase(valid_request)
        
        assert result.success is True
        assert "Complete process finished successfully" in result.message
        assert result.base_software_0 == "abc123def456"
        assert result.base_software_1 == "def456ghi789"
        assert result.feature_software_0 == "ghi789jkl012"
        assert result.clone_results is not None
        assert result.autorebase_results is not None


class TestAutoRebaseEndpoints:
    """Test cases for AutoRebase API endpoints"""
    
    def test_autorebase_root_endpoint(self, client):
        """Test AutoRebase root endpoint"""
        response = client.get("/autorebase/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "AutoRebase Processing API"
        assert "process" in data["endpoints"]
        assert "health" in data["endpoints"]
    
    def test_autorebase_health_endpoint(self, client):
        """Test AutoRebase health endpoint"""
        response = client.get("/autorebase/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "AutoRebase Processor"
    
    @patch('api.services.autorebase_service.AutoRebaseService.process_autorebase')
    def test_autorebase_process_endpoint_success(self, mock_process, client):
        """Test successful AutoRebase process endpoint"""
        # Mock successful response
        mock_response = AutoRebaseResponse(
            success=True,
            message="Complete process finished successfully",
            base_software_0="abc123def456",
            base_software_1="def456ghi789",
            feature_software_0="ghi789jkl012",
            base_repo_url="https://github.com/microsoft/vscode.git",
            feature_repo_url="https://github.com/microsoft/vscode.git",
            work_dir="data/repos"
        )
        mock_process.return_value = mock_response
        
        test_data = {
            "base_software_0": "abc123def456",
            "base_software_1": "def456ghi789",
            "feature_software_0": "ghi789jkl012",
            "base_repo_url": "https://github.com/microsoft/vscode.git",
            "feature_repo_url": "https://github.com/microsoft/vscode.git"
        }
        
        response = client.post("/autorebase/process", json=test_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "Complete process finished successfully" in data["message"]
    
    def test_autorebase_process_endpoint_invalid_data(self, client):
        """Test AutoRebase process endpoint with invalid data"""
        invalid_data = {
            "base_software_0": "invalid_sha",
            "base_software_1": "def456ghi789",
            "feature_software_0": "ghi789jkl012",
            "base_repo_url": "not-a-github-url",
            "feature_repo_url": "https://github.com/microsoft/vscode.git"
        }
        
        response = client.post("/autorebase/process", json=invalid_data)
        
        assert response.status_code == 422  # Validation error
        data = response.json()
        assert "detail" in data

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
            "base_software_1": "def456789abc",
            "feature_software_0": "789abc123def",
            "base_repo_url": "https://github.com/microsoft/vscode.git",
            "feature_repo_url": "https://github.com/microsoft/vscode.git",
            "work_dir": "data/repos"
        }
        
        request = AutoRebaseRequest(**data)
        
        assert request.base_software_0 == "abc123def456"
        assert request.base_software_1 == "def456789abc"
        assert request.feature_software_0 == "789abc123def"
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
        assert "No common files found" in result["message"] or "AutoRebase process completed successfully" in result["message"]
        # Check that we have the expected structure in details
        assert "files_processed" in result["details"]
        assert "patches_generated" in result["details"]


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
            base_software_1="def456789abc",
            feature_software_0="789abc123def",
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
        assert result.base_software_1 == "def456789abc"
        assert result.feature_software_0 == "789abc123def"
        assert result.clone_results is not None
        assert result.autorebase_results is not None


# Note: AutoRebase endpoints are now integrated into the GitHub input endpoint
# The autorebase process runs automatically after SHA validation

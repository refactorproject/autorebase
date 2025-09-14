"""
Unit tests for GitHub service
"""

import pytest
from unittest.mock import AsyncMock, patch
import httpx

from api.services.github_service import GitHubService
from api.models.github_models import GitHubSHARequest


class TestGitHubService:
    """Test cases for GitHubService"""
    
    @pytest.fixture
    def service(self):
        """Create GitHubService instance"""
        return GitHubService()
    
    @pytest.fixture
    def valid_request(self):
        """Create valid request"""
        return GitHubSHARequest(
            base_software_0="abc123def456",
            base_software_1="def456789abc",
            feature_software_0="789abc123def",
            base_repo_url="https://github.com/microsoft/vscode.git",
            feature_repo_url="https://github.com/microsoft/vscode.git"
        )
    
    def test_extract_repo_info(self, service):
        """Test repository info extraction"""
        owner, repo = service.extract_repo_info("https://github.com/microsoft/vscode.git")
        
        assert owner == "microsoft"
        assert repo == "vscode"
    
    def test_extract_repo_info_invalid_url(self, service):
        """Test repository info extraction with invalid URL"""
        with pytest.raises(ValueError):
            service.extract_repo_info("not-a-github-url")
    
    @pytest.mark.asyncio
    async def test_validate_sha_success(self, service):
        """Test successful SHA validation"""
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json = AsyncMock(return_value={
            "sha": "abc123def456",
            "commit": {
                "message": "Test commit",
                "author": {
                    "name": "Test Author",
                    "date": "2024-01-01T00:00:00Z"
                }
            }
        })
        
        with patch('httpx.AsyncClient.get', return_value=mock_response):
            result = await service.validate_sha("abc123def456", "microsoft", "vscode")
        
        assert result["valid"] is True
        assert result["sha"] == "abc123def456"
        assert result["message"] == "Test commit"
        assert result["author"] == "Test Author"
    
    @pytest.mark.asyncio
    async def test_validate_sha_not_found(self, service):
        """Test SHA validation when commit not found"""
        mock_response = AsyncMock()
        mock_response.status_code = 404
        
        with patch('httpx.AsyncClient.get', return_value=mock_response):
            result = await service.validate_sha("invalid_sha", "microsoft", "vscode")
        
        assert result["valid"] is False
        assert "Commit not found" in result["error"]
    
    @pytest.mark.asyncio
    async def test_validate_sha_request_error(self, service):
        """Test SHA validation with request error"""
        with patch('httpx.AsyncClient.get', side_effect=httpx.RequestError("Network error")):
            result = await service.validate_sha("abc123def456", "microsoft", "vscode")
        
        assert result["valid"] is False
        assert "Request failed" in result["error"]
    
    @pytest.mark.asyncio
    async def test_process_shas_all_valid(self, service, valid_request):
        """Test processing all valid SHAs with autorebase"""
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json = AsyncMock(return_value={
            "sha": "abc123def456",
            "commit": {
                "message": "Test commit",
                "author": {
                    "name": "Test Author",
                    "date": "2024-01-01T00:00:00Z"
                }
            }
        })
        
        # Mock autorebase results
        mock_autorebase_results = {
            "success": True,
            "message": "Complete process finished successfully",
            "clone_results": {
                "success": True,
                "results": {
                    "base_0": {"success": True, "message": "Cloned", "directory": "data/repos/base-0", "sha": "abc123def456"},
                    "base_1": {"success": True, "message": "Cloned", "directory": "data/repos/base-1", "sha": "def456ghi789"},
                    "feature_0": {"success": True, "message": "Cloned", "directory": "data/repos/feature-0", "sha": "ghi789jkl012"}
                }
            },
            "autorebase_results": {
                "success": True,
                "message": "AutoRebase completed",
                "details": {"status": "success"}
            }
        }
        
        with patch('httpx.AsyncClient.get', return_value=mock_response), \
             patch('api.autorebase.core.AutoRebase.process_repositories', return_value=mock_autorebase_results):
            result = await service.process_shas(valid_request)
        
        assert result.success is True
        assert "All GitHub SHAs validated successfully and AutoRebase process completed" in result.message
        assert result.base_software_0 == "abc123def456"
        assert result.base_software_1 == "def456789abc"
        assert result.feature_software_0 == "789abc123def"
        assert result.base_repo_url == "https://github.com/microsoft/vscode.git"
        assert result.feature_repo_url == "https://github.com/microsoft/vscode.git"
        assert result.processing_details is not None
        assert "autorebase_results" in result.processing_details
    
    @pytest.mark.asyncio
    async def test_process_shas_some_invalid(self, service, valid_request):
        """Test processing with some invalid SHAs"""
        # Mock successful response for first two SHAs
        mock_success_response = AsyncMock()
        mock_success_response.status_code = 200
        mock_success_response.json = AsyncMock(return_value={
            "sha": "abc123def456",
            "commit": {
                "message": "Test commit",
                "author": {
                    "name": "Test Author",
                    "date": "2024-01-01T00:00:00Z"
                }
            }
        })
        
        # Mock error response for third SHA
        mock_error_response = AsyncMock()
        mock_error_response.status_code = 404
        
        with patch('httpx.AsyncClient.get', side_effect=[mock_success_response, mock_success_response, mock_error_response]):
            result = await service.process_shas(valid_request)
        
        assert result.success is False
        assert "Validation failed" in result.message
        assert "Feature Software 0" in result.message
        assert result.processing_details is not None
        assert "validation_errors" in result.processing_details
    
    @pytest.mark.asyncio
    async def test_process_shas_exception(self, service, valid_request):
        """Test processing with exception"""
        with patch('httpx.AsyncClient.get', side_effect=Exception("Unexpected error")):
            result = await service.process_shas(valid_request)
        
        assert result.success is False
        assert "Processing failed" in result.message
        assert "Unexpected error" in result.message

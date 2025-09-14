"""
Manual integration tests for the AutoRebase API
These tests require a running server instance
"""

import pytest
import requests
import json
from fastapi.testclient import TestClient

from main import app

API_BASE = "http://localhost:8000"


class TestManualIntegration:
    """Manual integration tests that require a running server"""
    
    @pytest.mark.skip(reason="Requires running server")
    def test_health_manual(self):
        """Test the health endpoint with running server"""
        response = requests.get(f"{API_BASE}/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "AutoRebase API"
    
    @pytest.mark.skip(reason="Requires running server")
    def test_github_root_manual(self):
        """Test the GitHub router root endpoint with running server"""
        response = requests.get(f"{API_BASE}/github/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "GitHub SHA Processing API"
        assert "input_repos" in data["endpoints"]
    
    @pytest.mark.skip(reason="Requires running server")
    def test_input_repos_manual(self):
        """Test the input-repos endpoint with running server"""
        test_data = {
            "base_software_0": "a1b2c3d4e5f6",
            "base_software_1": "b2c3d4e5f6g7",
            "feature_software_0": "c3d4e5f6g7h8",
            "base_repo_url": "https://github.com/microsoft/vscode.git",
            "feature_repo_url": "https://github.com/microsoft/vscode.git"
        }
        
        response = requests.post(
            f"{API_BASE}/github/input-repos",
            json=test_data
        )
        
        # This will likely fail with 400 due to invalid SHAs, but should not be 500
        assert response.status_code in [200, 400]
        data = response.json()
        assert "success" in data
        assert "message" in data


def run_manual_tests():
    """Run manual tests (for development/debugging)"""
    print("AutoRebase API Manual Test Suite")
    print("=" * 50)
    
    try:
        # Test health endpoint
        print("Testing health endpoint...")
        response = requests.get(f"{API_BASE}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        print()
        
        # Test GitHub root endpoint
        print("Testing GitHub router root...")
        response = requests.get(f"{API_BASE}/github/")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        print()
        
        # Test input-repos endpoint
        print("Testing input-repos endpoint...")
        test_data = {
            "base_software_0": "a1b2c3d4e5f6",
            "base_software_1": "b2c3d4e5f6g7",
            "feature_software_0": "c3d4e5f6g7h8",
            "base_repo_url": "https://github.com/microsoft/vscode.git",
            "feature_repo_url": "https://github.com/microsoft/vscode.git"
        }
        
        response = requests.post(
            f"{API_BASE}/github/input-repos",
            json=test_data
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        print()
        
        print("Note: AutoRebase process now runs automatically after SHA validation")
        
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the API.")
        print("Make sure the server is running on http://localhost:8000")
        print("Run: python main.py")
    except Exception as e:
        print(f"Unexpected error: {e}")


def run_simple_tests():
    """Run simple manual tests (convenience function)"""
    print("AutoRebase API Simple Test Suite")
    print("=" * 50)
    print("⚠️  Make sure the server is running: python main.py")
    print()
    
    run_manual_tests()


if __name__ == "__main__":
    run_manual_tests()

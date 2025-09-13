#!/usr/bin/env python3
"""
Simple test script for the AutoRebase API
"""

import requests
import json

API_BASE = "http://localhost:8000"

def test_health():
    """Test the health endpoint"""
    print("Testing health endpoint...")
    response = requests.get(f"{API_BASE}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_github_root():
    """Test the GitHub router root endpoint"""
    print("Testing GitHub router root...")
    response = requests.get(f"{API_BASE}/github/")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_input_repos():
    """Test the input-repos endpoint"""
    print("Testing input-repos endpoint...")
    
    # Test data - using real GitHub SHAs from a public repo
    test_data = {
        "base_software_0": "a1b2c3d4e5f6",
        "base_software_1": "b2c3d4e5f6g7",
        "feature_software_0": "c3d4e5f6g7h8",
        "base_repo_url": "https://github.com/microsoft/vscode.git",
        "feature_repo_url": "https://github.com/microsoft/vscode.git"
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/github/input-repos",
            json=test_data
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
    print()

if __name__ == "__main__":
    print("AutoRebase API Test Suite")
    print("=" * 50)
    
    try:
        test_health()
        test_github_root()
        test_input_repos()
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the API.")
        print("Make sure the server is running on http://localhost:8000")
        print("Run: python main.py")

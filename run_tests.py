#!/usr/bin/env python3
"""
Test runner script for AutoRebase API
"""

import subprocess
import sys
import os


def run_tests():
    """Run all tests"""
    print("AutoRebase API Test Runner")
    print("=" * 50)
    
    # Check if pytest is installed
    try:
        import pytest
    except ImportError:
        print("❌ pytest not found. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pytest", "pytest-asyncio"])
    
    # Run unit tests
    print("\n🧪 Running Unit Tests...")
    result = subprocess.run([
        sys.executable, "-m", "pytest", 
        "tests/test_models.py", 
        "tests/test_services.py",
        "-v", "--tb=short"
    ])
    
    if result.returncode != 0:
        print("❌ Unit tests failed!")
        return False
    
    # Run integration tests
    print("\n🔗 Running Integration Tests...")
    result = subprocess.run([
        sys.executable, "-m", "pytest", 
        "tests/test_api_endpoints.py",
        "-v", "--tb=short"
    ])
    
    if result.returncode != 0:
        print("❌ Integration tests failed!")
        return False
    
    print("\n✅ All tests passed!")
    return True


def run_manual_tests():
    """Run manual tests (requires running server)"""
    print("Manual Test Runner")
    print("=" * 50)
    print("⚠️  Make sure the server is running: python main.py")
    print()
    
    try:
        from tests.test_api import run_manual_tests
        run_manual_tests()
    except ImportError as e:
        print(f"❌ Error importing manual tests: {e}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "manual":
        run_manual_tests()
    else:
        success = run_tests()
        sys.exit(0 if success else 1)

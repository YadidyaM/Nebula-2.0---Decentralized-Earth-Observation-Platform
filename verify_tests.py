#!/usr/bin/env python3
"""
Simple test verification script for Nebula Protocol
"""

import os
import sys
import subprocess
from pathlib import Path

def check_file_exists(file_path, description):
    """Check if a file exists."""
    if Path(file_path).exists():
        print(f"✅ {description}: {file_path}")
        return True
    else:
        print(f"❌ {description}: {file_path} - NOT FOUND")
        return False

def check_python_imports():
    """Check if required Python packages can be imported."""
    required_packages = [
        "pytest",
        "pytest_asyncio", 
        "pytest_cov",
        "fastapi",
        "motor",
        "redis",
        "sgp4",
        "numpy",
        "scipy",
        "astropy"
    ]
    
    print("\n🔍 Checking Python package imports...")
    all_imports_ok = True
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError as e:
            print(f"❌ {package}: {e}")
            all_imports_ok = False
    
    return all_imports_ok

def main():
    print("🌌 Nebula Protocol Test Suite Verification")
    print("=" * 50)
    
    # Check test files exist
    test_files = [
        ("backend/pyproject.toml", "Pytest configuration"),
        ("backend/tests/conftest.py", "Test configuration"),
        ("backend/tests/test_config.py", "Test environment config"),
        ("backend/tests/test_api_endpoints.py", "API endpoint tests"),
        ("backend/tests/test_ai_agents.py", "AI agent tests"),
        ("backend/tests/test_satellite_physics.py", "Satellite physics tests"),
        ("backend/tests/test_blockchain.py", "Blockchain tests"),
        ("backend/tests/test_websocket.py", "WebSocket tests"),
        ("backend/tests/README.md", "Test documentation"),
        ("backend/run_tests.py", "Test runner script"),
        ("backend/requirements.txt", "Dependencies with test packages")
    ]
    
    print("\n📁 Checking test files...")
    all_files_exist = True
    for file_path, description in test_files:
        if not check_file_exists(file_path, description):
            all_files_exist = False
    
    # Check Python imports
    imports_ok = check_python_imports()
    
    # Summary
    print("\n📊 Verification Summary:")
    print(f"Test files: {'✅ All present' if all_files_exist else '❌ Some missing'}")
    print(f"Python packages: {'✅ All available' if imports_ok else '❌ Some missing'}")
    
    if all_files_exist and imports_ok:
        print("\n🎉 Test suite verification PASSED!")
        print("\n🚀 You can now run tests with:")
        print("   python backend/run_tests.py")
        print("   python backend/run_tests.py --coverage")
        print("   python backend/run_tests.py --test-type unit")
        return 0
    else:
        print("\n💥 Test suite verification FAILED!")
        print("\n🔧 Please install missing dependencies:")
        print("   pip install -r backend/requirements.txt")
        return 1

if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
Test runner script for Nebula Protocol backend tests
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed")
        print(f"Error: {e.stderr}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Nebula Protocol Test Runner")
    parser.add_argument("--test-type", choices=["unit", "integration", "api", "all"], 
                       default="all", help="Type of tests to run")
    parser.add_argument("--coverage", action="store_true", 
                       help="Generate coverage report")
    parser.add_argument("--verbose", "-v", action="store_true", 
                       help="Verbose output")
    parser.add_argument("--parallel", "-n", type=int, default=1,
                       help="Number of parallel test processes")
    parser.add_argument("--markers", "-m", 
                       help="Run tests with specific markers")
    
    args = parser.parse_args()
    
    # Change to backend directory
    backend_dir = Path(__file__).parent / "backend"
    os.chdir(backend_dir)
    
    print("🌌 Nebula Protocol Test Runner")
    print("=" * 50)
    
    # Build pytest command
    pytest_cmd = ["python", "-m", "pytest"]
    
    # Add test path
    pytest_cmd.append("tests/")
    
    # Add markers based on test type
    if args.test_type == "unit":
        pytest_cmd.extend(["-m", "unit"])
    elif args.test_type == "integration":
        pytest_cmd.extend(["-m", "integration"])
    elif args.test_type == "api":
        pytest_cmd.extend(["-m", "api"])
    
    # Add custom markers if specified
    if args.markers:
        pytest_cmd.extend(["-m", args.markers])
    
    # Add coverage if requested
    if args.coverage:
        pytest_cmd.extend(["--cov=app", "--cov-report=html", "--cov-report=term-missing"])
    
    # Add verbose output
    if args.verbose:
        pytest_cmd.append("-v")
    
    # Add parallel execution
    if args.parallel > 1:
        pytest_cmd.extend(["-n", str(args.parallel)])
    
    # Convert to string for subprocess
    pytest_command = " ".join(pytest_cmd)
    
    # Run tests
    success = run_command(pytest_command, f"Running {args.test_type} tests")
    
    if success and args.coverage:
        print("\n📊 Coverage report generated in htmlcov/index.html")
    
    # Run linting if tests pass
    if success:
        print("\n🔍 Running code quality checks...")
        
        # Run black formatter check
        run_command("python -m black --check app/", "Code formatting check")
        
        # Run isort import sorting check
        run_command("python -m isort --check-only app/", "Import sorting check")
        
        # Run flake8 linting
        run_command("python -m flake8 app/", "Code linting")
        
        # Run mypy type checking
        run_command("python -m mypy app/", "Type checking")
    
    if success:
        print("\n🎉 All tests and quality checks passed!")
        sys.exit(0)
    else:
        print("\n💥 Tests or quality checks failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()

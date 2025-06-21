#!/usr/bin/env python3
"""
Test runner script for the ValMed backend.
Provides easy commands to run different types of tests with proper isolation.
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    print(f"{'='*60}\n")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=False)
        print(f"\n✅ {description} completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ {description} failed with exit code {e.returncode}")
        return False

def main():
    """Main test runner function."""
    if len(sys.argv) < 2:
        print("Usage: python run_tests.py <command>")
        print("\nAvailable commands:")
        print("  all          - Run all tests")
        print("  unit         - Run unit tests only")
        print("  integration  - Run integration tests only")
        print("  orders       - Run orders router tests only")
        print("  performance  - Run performance tests (N+1 query fix)")
        print("  coverage     - Run tests with coverage report")
        print("  lint         - Run linting checks")
        print("  clean        - Clean up test artifacts")
        return
    
    command = sys.argv[1].lower()
    
    # Ensure we're in the backend directory
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)
    
    if command == "all":
        success = run_command(
            ["python", "-m", "pytest", "tests/", "-v"],
            "All tests"
        )
    
    elif command == "unit":
        success = run_command(
            ["python", "-m", "pytest", "tests/", "-m", "unit", "-v"],
            "Unit tests"
        )
    
    elif command == "integration":
        success = run_command(
            ["python", "-m", "pytest", "tests/", "-m", "integration", "-v"],
            "Integration tests"
        )
    
    elif command == "orders":
        success = run_command(
            ["python", "-m", "pytest", "tests/routers/test_orders.py", "-v"],
            "Orders router tests"
        )
    
    elif command == "performance":
        success = run_command(
            ["python", "-m", "pytest", "tests/test_performance.py", "-v"],
            "Performance tests (N+1 query fix verification)"
        )
    
    elif command == "coverage":
        success = run_command(
            ["python", "-m", "pytest", "tests/", "--cov=.", "--cov-report=term-missing", "--cov-report=html"],
            "Tests with coverage report"
        )
    
    elif command == "lint":
        success = run_command(
            ["python", "-m", "flake8", ".", "--max-line-length=100"],
            "Linting checks"
        )
    
    elif command == "clean":
        # Clean up test artifacts
        test_files = ["test.db", ".coverage", "htmlcov/"]
        for file_path in test_files:
            if os.path.exists(file_path):
                if os.path.isdir(file_path):
                    import shutil
                    shutil.rmtree(file_path)
                else:
                    os.remove(file_path)
                print(f"✅ Cleaned up: {file_path}")
        print("✅ Cleanup completed!")
        return
    
    else:
        print(f"Unknown command: {command}")
        return
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main() 
#!/usr/bin/env python3
"""
Development setup script for pytest-pyrest plugin
"""
import os
import sys
import subprocess
import shutil
from pathlib import Path


def run_command(cmd, cwd=None):
    """Run a command and return the result"""
    print(f"Running: {cmd}")
    result = subprocess.run(
        cmd, 
        shell=True, 
        cwd=cwd,
        capture_output=True, 
        text=True
    )
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return False
    print(f"Success: {result.stdout}")
    return True


def setup_development():
    """Set up development environment"""
    print("Setting up pytest-pyrest development environment...")
    
    # Create logs directory if it doesn't exist
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Install the package in development mode
    if not run_command("pip install -e ."):
        print("Failed to install package in development mode")
        return False
    
    # Install development dependencies
    if not run_command("pip install -e .[dev]"):
        print("Failed to install development dependencies")
        return False
    
    # Run tests to verify installation
    if not run_command("pytest --version"):
        print("Failed to verify pytest installation")
        return False
    
    print("Development environment setup complete!")
    return True


def run_tests():
    """Run the test suite"""
    print("Running test suite...")
    
    # Run basic tests
    if not run_command("pytest code/sample_tests/ -v"):
        print("Tests failed")
        return False
    
    # Run with coverage
    if not run_command("pytest code/sample_tests/ --cov=pyrest --cov-report=html"):
        print("Coverage tests failed")
        return False
    
    print("All tests passed!")
    return True


def clean_build():
    """Clean build artifacts"""
    print("Cleaning build artifacts...")
    
    # Remove build directories
    for path in ["build", "dist", "*.egg-info"]:
        if os.path.exists(path):
            shutil.rmtree(path)
    
    # Remove Python cache
    for root, dirs, files in os.walk("."):
        for dir_name in dirs:
            if dir_name == "__pycache__":
                shutil.rmtree(os.path.join(root, dir_name))
    
    print("Cleanup complete!")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "setup":
            setup_development()
        elif command == "test":
            run_tests()
        elif command == "clean":
            clean_build()
        else:
            print(f"Unknown command: {command}")
            print("Available commands: setup, test, clean")
    else:
        print("Usage: python scripts/setup_dev.py [setup|test|clean]")

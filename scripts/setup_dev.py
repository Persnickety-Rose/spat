#!/usr/bin/env python3
"""Development setup script for pytest-pyrest plugin."""

import glob
import os
import shutil
import subprocess
import sys
from pathlib import Path


def run_command(cmd, cwd=None):
    """Run a command and return whether it succeeded."""
    print(f"Running: {cmd}")
    result = subprocess.run(
        cmd,
        shell=True,
        cwd=cwd,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return False
    if result.stdout:
        print(result.stdout)
    return True


def setup_development():
    """Set up development environment."""
    print("Setting up pytest-pyrest development environment...")

    Path("logs").mkdir(exist_ok=True)

    if not Path(".venv").exists():
        if not run_command("uv venv .venv"):
            print("Failed to create virtual environment")
            return False

    if not run_command("uv sync --extra dev"):
        print("Failed to install dependencies")
        return False

    if not run_command("uv run pytest --version"):
        print("Failed to verify pytest installation")
        return False

    print("Development environment setup complete!")
    return True


def run_tests():
    """Run the test suite."""
    print("Running test suite...")

    if not run_command("uv run pytest code/sample_tests/ -v"):
        print("Tests failed")
        return False

    if not run_command(
        "uv run pytest code/sample_tests/ --cov=pyrest --cov-report=html"
    ):
        print("Coverage tests failed")
        return False

    print("All tests passed!")
    return True


def clean_build():
    """Clean build artifacts."""
    print("Cleaning build artifacts...")

    for path in ["build", "dist"]:
        if os.path.exists(path):
            shutil.rmtree(path)

    for path in glob.glob("**/*.egg-info", recursive=True):
        shutil.rmtree(path)

    for root, dirs, _files in os.walk("."):
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

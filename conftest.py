import os
import csv
import pytest

def pytest_configure(config):
    """Load environment variables from CSV files before tests run"""
    # Check if pytest-env plugin is available
    try:
        import pytest_env
    except ImportError:
        print("Warning: pytest-env plugin not installed. Install with: pip install pytest-env")
        return
    
    # Load environment variables from CSV files
    env_files = [
        "code/sample_tests/env/qa-environment.csv"
    ]
    
    for env_file in env_files:
        if os.path.exists(env_file):
            print(f"Loading environment from: {env_file}")
            with open(env_file, 'r') as f:
                reader = csv.reader(f)
                for row in reader:
                    if len(row) >= 2:
                        key, value = row[0], row[1]
                        os.environ[key] = value
                        print(f"Set {key}={value}")

def pytest_collection_modifyitems(config, items):
    """Modify test collection if needed"""
    pass 
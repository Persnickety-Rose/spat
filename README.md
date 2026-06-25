# pytest-pyrest

A PyTest plugin for REST API testing with enhanced fixtures and utilities.

## Installation

```bash
# Install from local directory
pip install -e .

# Or install dependencies manually
pip install pytest requests pytest-env
```

## Features

- **PyTest Plugin Integration**: Full PyTest plugin with fixtures and markers
- **API Client Fixture**: Easy-to-use API client for making HTTP requests
- **Assertion Helpers**: Built-in assertion utilities for API responses
- **Environment Management**: Load environment variables from CSV files
- **Logging**: Comprehensive logging for API requests and responses

## Quick Start

### Basic Usage

```python
import pytest

@pytest.mark.api
def test_get_posts(api_client, assert_api):
    """Test getting posts from WordPress API"""
    response = api_client.get("wp-json/wp/v2/posts")
    
    assert_api.status_code(response, 200)
    assert_api.has_content(response)
```

### Environment Setup

Create a CSV file with environment variables:

```csv
envURL,http://localhost:8888
WP_USERNAME,admin
WP_PASSWORD,password
```

### Running Tests

```bash
# Run all API tests
pytest -m api

# Run with custom environment file
pytest --env-file=my-environment.csv

# Run with verbose output
pytest -v

# Run specific test file
pytest code/sample_tests/test_plugin_example.py
```

## Fixtures

### `api_client`

Provides an API client instance for making HTTP requests.

```python
def test_api_request(api_client):
    response = api_client.get("api/endpoint")
    response = api_client.post("api/endpoint", data={"key": "value"})
    response = api_client.put("api/endpoint/1", data={"key": "value"})
    response = api_client.delete("api/endpoint/1")
```

### `assert_api`

Provides assertion helpers for API responses.

```python
def test_api_response(api_client, assert_api):
    response = api_client.get("api/endpoint")
    
    # Basic assertions
    assert_api.status_code(response, 200)
    assert_api.has_content(response)
    
    # JSON assertions
    assert_api.json_contains(response, "id")
    assert_api.json_contains(response, "name", "expected_value")
    
    # Text search
    assert_api.contains_text(response, "expected_text")

    # Success and failure helpers
    assert_api.success(response, 200)
    assert_api.failure(response, 404, expect_content=True)
```

## Command Line Options

- `--env-file`: Path to environment CSV file (default: qa-environment.csv)
- `--vars-file`: Path to additional variables CSV file
- `--api-log-level`: Logging level (DEBUG, INFO, WARNING, ERROR)
- `--api-log-file`: Custom log file path

## Markers

- `@pytest.mark.api`: Mark test as an API test
- `@pytest.mark.slow`: Mark test as slow running

## Configuration

### pyproject.toml

```toml
[tool.pytest.ini_options]
testpaths = ["code/sample_tests"]
markers = [
    "api: mark test as an API test",
    "slow: mark test as slow running",
]
env = [
    "envURL=http://localhost:8888",
    "pyTestEnv=code/sample_tests/env/qa-environment.csv",
    "pyTestDebug=true",
]
log_cli = true
log_cli_level = "INFO"
```

### Environment Files

Create CSV files with key-value pairs:

```csv
envURL,https://api.example.com
API_KEY,your_api_key_here
USERNAME,test_user
PASSWORD,test_password
```

## Examples

See `code/sample_tests/test_plugin_example.py` and `code/sample_tests/test_wordpress_api.py` for examples.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

[GNU General Public License v3.0](https://www.gnu.org/licenses/gpl-3.0.en.html)

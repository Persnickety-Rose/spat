"""
PyTest plugin for REST API testing
"""
import os
import csv
import logging
import pytest
from typing import Optional, Dict, Any
from .API_Call import API


def pytest_configure(config):
    """Configure the plugin and set up logging"""
    # Register custom markers
    config.addinivalue_line(
        "markers", "api: mark test as an API test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    
    # Set up logging
    setup_logging(
        config.getoption("api_log_level"),
        config.getoption("log_file") or None,
    )


def pytest_addoption(parser):
    """Add command line options"""
    group = parser.getgroup("pyrest")
    group.addoption(
        "--env-file",
        action="store",
        default=None,
        help="Path to environment CSV file"
    )
    group.addoption(
        "--vars-file",
        action="store",
        help="Path to additional variables CSV file"
    )
    group.addoption(
        "--api-log-level",
        action="store",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level for API tests"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection"""
    # Load environment variables
    load_environment_variables(config)
    
    # Add markers to tests
    for item in items:
        if "api" in item.keywords:
            item.add_marker(pytest.mark.api)


def setup_logging(log_level: str = "INFO", log_file: str | None = None):
    """Set up logging using ``--api-log-level`` and pytest ``--log-file``."""
    level = getattr(logging, log_level.upper(), logging.INFO)
    logger = logging.getLogger('pyrest')
    logger.setLevel(level)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    if log_file:
        log_dir = os.path.dirname(os.path.abspath(log_file))
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)


def load_environment_variables(config):
    """Load environment variables from CSV files"""
    env_file = config.getoption("env_file")
    vars_file = config.getoption("vars_file")
    
    # Load main environment file
    if env_file and os.path.exists(env_file):
        with open(env_file, 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) >= 2:
                    key, value = row[0], row[1]
                    os.environ[key] = value
    
    # Load additional variables file
    if vars_file and os.path.exists(vars_file):
        with open(vars_file, 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) >= 2:
                    key, value = row[0], row[1]
                    os.environ[key] = value


def get_auth(
    username_env: str = "API_USERNAME",
    password_env: str = "API_PASSWORD",
    username_default: str = "",
    password_default: str = "",
) -> tuple[str, str]:
    """Return basic-auth credentials from environment variables.

    Reads ``API_USERNAME`` / ``API_PASSWORD`` by default. Returns empty
    strings when unset so requests proceed without basic auth. Pass
    alternate env var names for APIs that use different credentials.
    """
    return (
        os.getenv(username_env, username_default),
        os.getenv(password_env, password_default),
    )


@pytest.fixture
def api_client():
    """Fixture that provides an API client instance"""
    return APIClient()


class APIClient:
    """Enhanced API client for PyTest integration"""
    
    def __init__(self):
        self.base_url = os.getenv("envURL", "https://petstore.swagger.io/v2")
        self.logger = logging.getLogger('pyrest.api')
        self.default_auth = get_auth()
    
    def request(
        self,
        method: str = "GET",
        endpoint: str = "",
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        auth: Optional[tuple] = None,
        verify_ssl: bool = True,
        cert_path: Optional[str] = None
    ) -> API:
        """
        Make an API request
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            endpoint: API endpoint path
            data: Request body data
            headers: Request headers
            params: URL parameters
            auth: Authentication tuple (username, password)
            verify_ssl: Whether to verify SSL certificates
            cert_path: Path to custom CA certificate bundle
            
        Returns:
            API instance with response data
        """
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        
        if auth is None:
            auth = self.default_auth
        
        # Create API instance
        api = API(
            address=url,
            method=method.upper(),
            data=data or "",
            header=headers or "",
            params=params or "",
            user=auth[0] if auth else "",
            password=auth[1] if auth else "",
            verify_ssl=verify_ssl,
            cert_path=cert_path
        )
        
        # Make the request
        api.CallAPI()
        
        self.logger.info(f"{method} {url} -> {api.status}")
        
        return api
    
    def get(self, endpoint: str, **kwargs) -> API:
        """Make a GET request"""
        return self.request("GET", endpoint, **kwargs)
    
    def post(self, endpoint: str, data: Dict[str, Any], **kwargs) -> API:
        """Make a POST request"""
        return self.request("POST", endpoint, data=data, **kwargs)
    
    def put(self, endpoint: str, data: Dict[str, Any], **kwargs) -> API:
        """Make a PUT request"""
        return self.request("PUT", endpoint, data=data, **kwargs)
    
    def delete(self, endpoint: str, **kwargs) -> API:
        """Make a DELETE request"""
        return self.request("DELETE", endpoint, **kwargs)


@pytest.fixture
def assert_api():
    """Fixture that provides assertion helpers for API responses"""
    return APIAssertions()


class APIAssertions:
    """Helper class for API response assertions"""
    
    def __init__(self):
        self.logger = logging.getLogger('pyrest.assertions')
    
    def status_code(self, response: API, expected_code: int):
        """Assert response status code"""
        assert response.status == expected_code, \
            f"Expected status code {expected_code}, got {response.status}"
    
    def has_content(self, response: API):
        """Assert response has content"""
        assert len(response.content) > 0, "Response has no content"
    
    def contains_text(self, response: API, text: str):
        """Assert response contains specific text."""
        content = response.content
        if isinstance(content, bytes):
            content = content.decode("utf-8", errors="replace")
        assert text in content, f"Expected to find '{text}' in response content"

    def json_contains(self, response: API, key: str, value: Any = None):
        """Assert JSON response contains key/value"""
        assert hasattr(response, 'json'), "Response is not JSON"
        assert key in response.json, f"Key '{key}' not found in response"
        if value is not None:
            assert response.json[key] == value, \
                f"Expected {key}={value}, got {response.json[key]}"
    
    def success(self, response: API, expected_code: int = 200):
        """Assert successful API call."""
        self.status_code(response, expected_code)
        self.has_content(response)

    def failure(self, response: API, expected_code: int = 400, expect_content: bool = False):
        """Assert failed API call."""
        self.status_code(response, expected_code)
        if expect_content:
            self.has_content(response)
        else:
            assert len(response.content) == 0, "Expected empty response content"

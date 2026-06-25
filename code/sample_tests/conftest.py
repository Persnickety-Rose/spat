"""
PyTest configuration for sample tests
"""
import pytest
import os

# Import fixtures from wp_api_client to make them available to all tests
from apis.wp_api_client import wp_client, authenticated_wp_client


@pytest.fixture(scope="session")
def base_url():
    """Base URL for API testing"""
    return os.getenv("envURL", "http://localhost:8888")


@pytest.fixture(scope="session")
def api_credentials():
    """API credentials for authenticated requests"""
    from pyrest.plugin import get_wp_auth
    username, password = get_wp_auth()
    return {
        "username": username,
        "password": password,
    }


@pytest.fixture
def test_name(request):
    """Fixture that provides the current test name"""
    return request.node.name


@pytest.fixture
def test_logger():
    """Fixture that provides a logger with test context"""
    import logging
    logger = logging.getLogger('myLogger')
    logger.setLevel(logging.DEBUG)
    return logger


@pytest.fixture
def sample_post_data():
    """Sample post data for testing"""
    return {
        "title": "Test Post",
        "content": "This is a test post content",
        "status": "publish"
    }


@pytest.fixture
def sample_user_data():
    """Sample user data for testing"""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword"
    }

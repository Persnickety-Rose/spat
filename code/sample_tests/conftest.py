"""
PyTest configuration for sample tests
"""
import pytest
import os


@pytest.fixture(scope="session")
def base_url():
    """Base URL for API testing"""
    return os.getenv("envURL", "http://localhost:8888")


@pytest.fixture(scope="session")
def api_credentials():
    """API credentials for authenticated requests"""
    return {
        "username": os.getenv("WP_USERNAME", "admin"),
        "password": os.getenv("WP_PASSWORD", "password")
    }


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

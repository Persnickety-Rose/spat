"""
pytest-pyrest - A PyTest plugin for REST API testing
"""

from .API_Call import API
from .base_client import BaseAPIClient
from .plugin import APIClient, APIAssertions, api_client, assert_api, get_auth

__version__ = "0.1.0"
__author__ = "Jasmine-Arabella Post"

__all__ = [
    "API",
    "BaseAPIClient",
    "APIClient",
    "APIAssertions",
    "api_client",
    "assert_api",
    "get_auth",
]

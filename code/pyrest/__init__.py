"""
pytest-pyrest - A PyTest plugin for REST API testing
"""

from .API_Call import API
from .util import AssertTest, AssertSearch
from .plugin import APIClient, APIAssertions, api_client, assert_api, get_wp_auth

__version__ = "0.1.0"
__author__ = "Jasmine-Arabella Post"

__all__ = [
    'API',
    'AssertTest', 
    'AssertSearch',
    'APIClient',
    'APIAssertions',
    'api_client',
    'assert_api',
    'get_wp_auth',
]

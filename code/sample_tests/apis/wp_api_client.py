#!/usr/bin/env python
"""
WordPress API Client using the PyRest Plugin Framework
This demonstrates the modern approach to creating API call classes using the plugin framework
"""

import pytest
from typing import Dict, Any, Optional
from pyrest.API_Call import API
import os


class WordPressAPIClient:
    """
    WordPress API Client using the plugin framework approach.
    This class provides a clean interface for WordPress API operations
    without requiring inheritance from the base API class.
    """
    
    def __init__(self, base_url: str, username: str = "", password: str = "", 
                 verify_ssl: bool = False, cert_path: Optional[str] = None):
        """
        Initialize the WordPress API client
        
        Args:
            base_url: Base URL for the WordPress site
            username: WordPress username for authenticated requests
            password: WordPress password for authenticated requests
            verify_ssl: Whether to verify SSL certificates
            cert_path: Path to custom CA certificate bundle
        """
        self.base_url = base_url.rstrip('/')
        self.username = username
        self.password = password
        self.verify_ssl = verify_ssl
        self.cert_path = cert_path
        self.default_headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    def _create_api_instance(self, endpoint: str, method: str = "GET", 
                           data: Optional[Dict[str, Any]] = None,
                           headers: Optional[Dict[str, str]] = None,
                           params: Optional[Dict[str, Any]] = None) -> API:
        """
        Create and configure an API instance
        
        Args:
            endpoint: API endpoint path
            method: HTTP method
            data: Request body data
            headers: Request headers
            params: URL parameters
            
        Returns:
            Configured API instance
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        # Merge headers
        request_headers = self.default_headers.copy()
        if headers:
            request_headers.update(headers)
        
        # Create API instance
        api = API(
            address=url,
            method=method.upper(),
            data=data or "",
            header=request_headers,
            params=params or "",
            user=self.username,
            password=self.password,
            verify_ssl=self.verify_ssl,
            cert_path=self.cert_path
        )
        
        return api
    
    def get_pages(self, params: Optional[Dict[str, Any]] = None) -> API:
        """
        Get all pages
        
        Args:
            params: Optional query parameters
            
        Returns:
            API response object
        """
        api = self._create_api_instance(
            endpoint="/wp-json/wp/v2/pages",
            method="GET",
            params=params
        )
        api.CallAPI()
        return api
    
    def get_page(self, page_id: int) -> API:
        """
        Get a specific page by ID
        
        Args:
            page_id: WordPress page ID
            
        Returns:
            API response object
        """
        api = self._create_api_instance(
            endpoint=f"/wp-json/wp/v2/pages/{page_id}",
            method="GET"
        )
        api.CallAPI()
        return api
    
    def create_page(self, title: str, content: str, status: str = "publish",
                   additional_data: Optional[Dict[str, Any]] = None) -> API:
        """
        Create a new page
        
        Args:
            title: Page title
            content: Page content
            status: Page status (draft, publish, etc.)
            additional_data: Additional page data
            
        Returns:
            API response object
        """
        if not self.username or not self.password:
            raise ValueError("Username and password required for creating pages")
        
        page_data = {
            "title": title,
            "content": content,
            "status": status
        }
        
        if additional_data:
            page_data.update(additional_data)
        
        api = self._create_api_instance(
            endpoint="/wp-json/wp/v2/pages",
            method="POST",
            data=page_data
        )
        api.CallAPI()
        return api
    
    def update_page(self, page_id: int, **kwargs) -> API:
        """
        Update an existing page
        
        Args:
            page_id: WordPress page ID
            **kwargs: Page data to update
            
        Returns:
            API response object
        """
        if not self.username or not self.password:
            raise ValueError("Username and password required for updating pages")
        
        api = self._create_api_instance(
            endpoint=f"/wp-json/wp/v2/pages/{page_id}",
            method="POST",
            data=kwargs
        )
        api.CallAPI()
        return api
    
    def delete_page(self, page_id: int, force: bool = False) -> API:
        """
        Delete a page
        
        Args:
            page_id: WordPress page ID
            force: Whether to force delete (bypass trash)
            
        Returns:
            API response object
        """
        if not self.username or not self.password:
            raise ValueError("Username and password required for deleting pages")
        
        params = {"force": force} if force else None
        
        api = self._create_api_instance(
            endpoint=f"/wp-json/wp/v2/pages/{page_id}",
            method="DELETE",
            params=params
        )
        api.CallAPI()
        return api
    
    def get_posts(self, params: Optional[Dict[str, Any]] = None) -> API:
        """
        Get all posts
        
        Args:
            params: Optional query parameters
            
        Returns:
            API response object
        """
        api = self._create_api_instance(
            endpoint="/wp-json/wp/v2/posts",
            method="GET",
            params=params
        )
        api.CallAPI()
        return api
    
    def get_post(self, post_id: int) -> API:
        """
        Get a specific post by ID
        
        Args:
            post_id: WordPress post ID
            
        Returns:
            API response object
        """
        api = self._create_api_instance(
            endpoint=f"/wp-json/wp/v2/posts/{post_id}",
            method="GET"
        )
        api.CallAPI()
        return api
    
    def create_post(self, title: str, content: str, status: str = "publish",
                   additional_data: Optional[Dict[str, Any]] = None) -> API:
        """
        Create a new post
        
        Args:
            title: Post title
            content: Post content
            status: Post status (draft, publish, etc.)
            additional_data: Additional post data
            
        Returns:
            API response object
        """
        if not self.username or not self.password:
            raise ValueError("Username and password required for creating posts")
        
        post_data = {
            "title": title,
            "content": content,
            "status": status
        }
        
        if additional_data:
            post_data.update(additional_data)
        
        api = self._create_api_instance(
            endpoint="/wp-json/wp/v2/posts",
            method="POST",
            data=post_data
        )
        api.CallAPI()
        return api
    
    def get_users(self, params: Optional[Dict[str, Any]] = None) -> API:
        """
        Get all users (requires authentication)
        
        Args:
            params: Optional query parameters
            
        Returns:
            API response object
        """
        if not self.username or not self.password:
            raise ValueError("Username and password required for getting users")
        
        api = self._create_api_instance(
            endpoint="/wp-json/wp/v2/users",
            method="GET",
            params=params
        )
        api.CallAPI()
        return api
    
    def get_current_user(self) -> API:
        """
        Get current user information (requires authentication)
        
        Returns:
            API response object
        """
        if not self.username or not self.password:
            raise ValueError("Username and password required for getting current user")
        
        api = self._create_api_instance(
            endpoint="/wp-json/wp/v2/users/me",
            method="GET"
        )
        api.CallAPI()
        return api
    
    def get_categories(self, params: Optional[Dict[str, Any]] = None) -> API:
        """
        Get all categories
        
        Args:
            params: Optional query parameters
            
        Returns:
            API response object
        """
        api = self._create_api_instance(
            endpoint="/wp-json/wp/v2/categories",
            method="GET",
            params=params
        )
        api.CallAPI()
        return api


# PyTest fixtures for easy integration
@pytest.fixture
def wp_client():
    """
    Fixture that provides a WordPress API client instance
    """
    base_url = os.getenv("envURL", "http://localhost:8888")
    username = os.getenv("WP_USERNAME", "")
    password = os.getenv("WP_PASSWORD", "")
    
    return WordPressAPIClient(
        base_url=base_url,
        username=username,
        password=password,
        verify_ssl=False
    )


@pytest.fixture
def authenticated_wp_client():
    """
    Fixture that provides an authenticated WordPress API client instance
    Requires WP_USERNAME and WP_PASSWORD environment variables
    """
    base_url = os.getenv("envURL", "http://localhost:8888")
    username = os.getenv("WP_USERNAME")
    password = os.getenv("WP_PASSWORD")
    
    if not username or not password:
        pytest.skip("WP_USERNAME and WP_PASSWORD environment variables required")
    
    return WordPressAPIClient(
        base_url=base_url,
        username=username,
        password=password,
        verify_ssl=False
    )

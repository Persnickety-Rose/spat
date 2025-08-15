#!/usr/bin/env python
"""
Example tests using the WordPress API Client with the PyRest Plugin Framework
This demonstrates the modern approach to writing API tests
"""

import pytest
import json
from apis.wp_api_client import WordPressAPIClient, wp_client, authenticated_wp_client
import os


class TestWordPressPages:
    """Test WordPress pages functionality"""
    
    def test_get_pages(self, wp_client, assert_api):
        """Test getting all pages"""
        response = wp_client.get_pages()
        
        # Use plugin assertion helpers
        assert_api.status_code(response, 200)
        assert_api.has_content(response)
        
        # Additional assertions
        assert hasattr(response, 'json')
        assert isinstance(response.json, list)
    
    def test_get_pages_with_params(self, wp_client, assert_api):
        """Test getting pages with query parameters"""
        params = {"per_page": 5, "orderby": "date"}
        response = wp_client.get_pages(params=params)
        
        assert_api.status_code(response, 200)
        assert_api.has_content(response)
    
    def test_get_specific_page(self, wp_client, assert_api):
        """Test getting a specific page by ID"""
        # First get all pages to find an ID
        pages_response = wp_client.get_pages()
        assert_api.status_code(pages_response, 200)
        
        if pages_response.json:
            page_id = pages_response.json[0]['id']
            response = wp_client.get_page(page_id)
            
            assert_api.status_code(response, 200)
            assert_api.has_content(response)
            assert response.json['id'] == page_id


class TestWordPressPosts:
    """Test WordPress posts functionality"""
    
    def test_get_posts(self, wp_client, assert_api):
        """Test getting all posts"""
        response = wp_client.get_posts()
        
        assert_api.status_code(response, 200)
        assert_api.has_content(response)
    
    def test_get_posts_with_params(self, wp_client, assert_api):
        """Test getting posts with query parameters"""
        params = {"per_page": 3, "orderby": "title"}
        response = wp_client.get_posts(params=params)
        
        assert_api.status_code(response, 200)
        assert_api.has_content(response)


class TestWordPressCategories:
    """Test WordPress categories functionality"""
    
    def test_get_categories(self, wp_client, assert_api):
        """Test getting all categories"""
        response = wp_client.get_categories()
        
        assert_api.status_code(response, 200)
        assert_api.has_content(response)


class TestWordPressAuthenticatedOperations:
    """Test authenticated WordPress operations"""
    
    def test_get_current_user(self, authenticated_wp_client, assert_api):
        """Test getting current user information"""
        response = authenticated_wp_client.get_current_user()
        
        assert_api.status_code(response, 200)
        assert_api.has_content(response)
        assert_api.json_contains(response, 'id')
    
    def test_get_users(self, authenticated_wp_client, assert_api):
        """Test getting all users"""
        response = authenticated_wp_client.get_users()
        
        assert_api.status_code(response, 200)
        assert_api.has_content(response)
    
    def test_create_page(self, authenticated_wp_client, assert_api):
        """Test creating a new page"""
        test_title = "Test Page from Plugin Framework"
        test_content = "This is a test page created using the plugin framework"
        
        response = authenticated_wp_client.create_page(
            title=test_title,
            content=test_content,
            status="draft"
        )
        
        assert_api.status_code(response, 201)  # Created
        assert_api.has_content(response)
        assert_api.json_contains(response, 'title', test_title)
        assert_api.json_contains(response, 'content', test_content)
    
    def test_create_post(self, authenticated_wp_client, assert_api):
        """Test creating a new post"""
        test_title = "Test Post from Plugin Framework"
        test_content = "This is a test post created using the plugin framework"
        
        response = authenticated_wp_client.create_post(
            title=test_title,
            content=test_content,
            status="draft"
        )
        
        assert_api.status_code(response, 201)  # Created
        assert_api.has_content(response)
        assert_api.json_contains(response, 'title', test_title)
        assert_api.json_contains(response, 'content', test_content)


class TestWordPressErrorHandling:
    """Test error handling scenarios"""
    
    def test_get_nonexistent_page(self, wp_client, assert_api):
        """Test getting a page that doesn't exist"""
        response = wp_client.get_page(99999)
        
        assert_api.status_code(response, 404)
    
    def test_create_page_without_auth(self, wp_client):
        """Test that creating a page without authentication fails"""
        with pytest.raises(ValueError, match="Username and password required"):
            wp_client.create_page("Test", "Content")


# Example using the plugin's api_client fixture directly
class TestUsingPluginAPIClient:
    """Example using the plugin's built-in api_client fixture"""
    
    def test_using_plugin_client(self, api_client, assert_api):
        """Test using the plugin's api_client fixture"""
        response = api_client.get("/wp-json/wp/v2/pages")
        
        assert_api.status_code(response, 200)
        assert_api.has_content(response)
    
    def test_using_plugin_client_with_auth(self, api_client, assert_api):
        """Test using the plugin's api_client with authentication"""
        username = os.getenv("WP_USERNAME")
        password = os.getenv("WP_PASSWORD")
        
        if not username or not password:
            pytest.skip("Authentication credentials not available")
        
        response = api_client.get(
            "/wp-json/wp/v2/users/me",
            auth=(username, password)
        )
        
        assert_api.status_code(response, 200)
        assert_api.has_content(response)


# Example of a more complex test scenario
class TestWordPressWorkflow:
    """Test a complete WordPress workflow"""
    
    def test_page_lifecycle(self, authenticated_wp_client, assert_api):
        """Test creating, updating, and deleting a page"""
        # Create a page
        create_response = authenticated_wp_client.create_page(
            title="Lifecycle Test Page",
            content="Initial content",
            status="draft"
        )
        
        assert_api.status_code(create_response, 201)
        page_id = create_response.json['id']
        
        # Update the page
        update_response = authenticated_wp_client.update_page(
            page_id,
            title="Updated Lifecycle Test Page",
            content="Updated content"
        )
        
        assert_api.status_code(update_response, 200)
        assert_api.json_contains(update_response, 'title', "Updated Lifecycle Test Page")
        
        # Verify the update
        get_response = authenticated_wp_client.get_page(page_id)
        assert_api.status_code(get_response, 200)
        assert_api.json_contains(get_response, 'content', "Updated content")
        
        # Clean up - delete the page
        delete_response = authenticated_wp_client.delete_page(page_id, force=True)
        assert_api.status_code(delete_response, 200)

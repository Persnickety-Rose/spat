"""
WordPress API tests using the PyRest plugin framework and WordPressAPIClient.
"""

import json
import os
import uuid
from random import choice
from string import ascii_letters

import pytest

from apis.wp_api_client import WordPressAPIClient

pytestmark = pytest.mark.api


class TestWordPressPages:
    """Test WordPress pages functionality."""

    def test_get_pages(self, wp_client, assert_api):
        """Test getting all pages."""
        response = wp_client.get_pages()

        assert_api.status_code(response, 200)
        assert_api.has_content(response)
        assert len(response.content) > 10, "There was no data sent back from the call"
        assert hasattr(response, "json")
        assert isinstance(response.json, list)

    def test_get_pages_with_params(self, wp_client, assert_api):
        """Test getting pages with query parameters."""
        params = {"per_page": 5, "orderby": "date"}
        response = wp_client.get_pages(params=params)

        assert_api.status_code(response, 200)
        assert_api.has_content(response)

    def test_get_specific_page(self, wp_client, assert_api):
        """Test getting a specific page by ID."""
        pages_response = wp_client.get_pages()
        assert_api.status_code(pages_response, 200)

        if pages_response.json:
            page_id = pages_response.json[0]["id"]
            response = wp_client.get_page(page_id)

            assert_api.status_code(response, 200)
            assert_api.has_content(response)
            assert response.json["id"] == page_id


class TestWordPressPosts:
    """Test WordPress posts functionality."""

    def test_get_posts(self, wp_client, assert_api):
        """Test getting all posts."""
        response = wp_client.get_posts()

        assert len(response.content) > 0
        assert_api.status_code(response, 200)
        assert_api.has_content(response)

    def test_get_posts_with_params(self, wp_client, assert_api):
        """Test getting posts with query parameters."""
        params = {"per_page": 3, "orderby": "title"}
        response = wp_client.get_posts(params=params)

        assert_api.status_code(response, 200)
        assert_api.has_content(response)


class TestWordPressCategories:
    """Test WordPress categories functionality."""

    def test_get_categories(self, wp_client, assert_api):
        """Test getting all categories."""
        response = wp_client.get_categories()

        assert_api.status_code(response, 200)
        assert_api.has_content(response)


class TestWordPressAuthenticatedOperations:
    """Test authenticated WordPress operations."""

    def test_get_current_user(self, authenticated_wp_client, assert_api):
        """Test getting current user information."""
        response = authenticated_wp_client.get_current_user()

        assert_api.status_code(response, 200)
        assert_api.has_content(response)
        assert_api.json_contains(response, "id")

    def test_get_users(self, authenticated_wp_client, assert_api):
        """Test getting all users."""
        response = authenticated_wp_client.get_users()

        assert_api.status_code(response, 200)
        assert_api.has_content(response)

    def test_create_page(self, authenticated_wp_client, assert_api):
        """Test creating a new page."""
        test_title = "Test Page from Plugin Framework"
        test_content = "This is a test page created using the plugin framework"

        response = authenticated_wp_client.create_page(
            title=test_title,
            content=test_content,
            status="draft",
        )

        try:
            assert_api.status_code(response, 201)
            assert_api.has_content(response)
            assert_api.json_contains(response, "title")
            assert response.json["title"]["raw"] == test_title
            assert_api.json_contains(response, "content")
            assert response.json["content"]["raw"] == test_content
        except AssertionError as exc:
            if hasattr(response, "json"):
                response_json = json.dumps(response.json, indent=2)
            else:
                content = response.content
                if isinstance(content, bytes):
                    content = content.decode("utf-8", errors="replace")
                response_json = content
            pytest.fail(f"{exc}\n\nFull response JSON:\n{response_json}")

    def test_create_post(self, authenticated_wp_client, assert_api):
        """Test creating a new draft post."""
        test_title = "Test Post from Plugin Framework"
        test_content = "This is a test post created using the plugin framework"

        response = authenticated_wp_client.create_post(
            title=test_title,
            content=test_content,
            status="draft",
        )

        assert_api.status_code(response, 201)
        assert_api.has_content(response)
        assert response.json["title"]["raw"] == test_title
        assert response.json["content"]["raw"] == test_content

    def test_create_published_post(self, authenticated_wp_client, assert_api):
        """Test creating a published post with unique content."""
        post_title = f"This is cow number {uuid.uuid4().hex[:8]}"
        content = "".join(choice(ascii_letters) for _ in range(120))

        response = authenticated_wp_client.create_post(
            title=post_title,
            content=content,
            status="publish",
        )

        assert len(response.content) > 0
        assert_api.status_code(response, 201)
        assert_api.has_content(response)

    def test_create_draft_post_with_long_content(self, authenticated_wp_client, assert_api):
        """Test creating a draft post with long content."""
        post_title = f"There are {uuid.uuid4().hex[:8]} cows"
        token = "".join(choice(ascii_letters) for _ in range(8))
        content = " ".join(token for _ in range(600))

        response = authenticated_wp_client.create_post(
            title=post_title,
            content=content,
            status="draft",
        )

        assert len(response.content) > 0
        assert_api.status_code(response, 201)
        assert_api.has_content(response)


class TestWordPressErrorHandling:
    """Test error handling scenarios."""

    def test_get_nonexistent_page(self, wp_client, assert_api):
        """Test getting a page that doesn't exist."""
        response = wp_client.get_page(99999)

        assert_api.status_code(response, 404)

    def test_get_nonexistent_post(self, wp_client, assert_api):
        """Test getting a post that doesn't exist."""
        response = wp_client.get_post(99999)

        assert len(response.content) > 0
        assert_api.status_code(response, 404)

    def test_create_page_without_auth(self, wp_client):
        """Test that creating a page without authentication fails."""
        with pytest.raises(ValueError, match="Username and password required"):
            wp_client.create_page("Test", "Content")

    def test_create_post_without_auth(self):
        """Test that creating a post without authentication fails."""
        unauthenticated_client = WordPressAPIClient(
            base_url=os.getenv("envURL", "http://localhost:8888"),
            username="",
            password="",
        )

        post_title = f"This is the {uuid.uuid4().hex[:8]} big dead cow"
        content = "".join(choice(ascii_letters) for _ in range(120))

        with pytest.raises(ValueError, match="Username and password required"):
            unauthenticated_client.create_post(
                title=post_title,
                content=content,
                status="publish",
            )


class TestUsingPluginAPIClient:
    """Example using the plugin's built-in api_client fixture."""

    def test_using_plugin_client(self, api_client, assert_api):
        """Test using the plugin's api_client fixture."""
        response = api_client.get("/wp-json/wp/v2/pages")

        assert_api.status_code(response, 200)
        assert_api.has_content(response)

    def test_using_plugin_client_with_auth(self, api_client, assert_api):
        """Test using the plugin's api_client with authentication."""
        username = os.getenv("WP_USERNAME")
        password = os.getenv("WP_PASSWORD")

        if not username or not password:
            pytest.skip("Authentication credentials not available")

        response = api_client.get(
            "/wp-json/wp/v2/users/me",
            auth=(username, password),
        )

        assert_api.status_code(response, 200)
        assert_api.has_content(response)


class TestWordPressWorkflow:
    """Test a complete WordPress workflow."""

    def test_page_lifecycle(self, authenticated_wp_client, assert_api):
        """Test creating, updating, and deleting a page."""
        create_response = authenticated_wp_client.create_page(
            title="Lifecycle Test Page",
            content="Initial content",
            status="draft",
        )

        assert_api.status_code(create_response, 201)
        page_id = create_response.json["id"]

        update_response = authenticated_wp_client.update_page(
            page_id,
            title="Updated Lifecycle Test Page",
            content="Updated content",
        )

        assert_api.status_code(update_response, 200)
        assert_api.json_contains(update_response, "title", "Updated Lifecycle Test Page")

        get_response = authenticated_wp_client.get_page(page_id)
        assert_api.status_code(get_response, 200)
        assert_api.json_contains(get_response, "content", "Updated content")

        delete_response = authenticated_wp_client.delete_page(page_id, force=True)
        assert_api.status_code(delete_response, 200)

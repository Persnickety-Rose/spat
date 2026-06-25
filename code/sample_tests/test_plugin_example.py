"""
Example tests using the pytest-pyrest plugin
"""
import pytest
from pyrest.plugin import get_wp_auth
import os


@pytest.mark.api
def test_get_posts_using_plugin(api_client, assert_api):
    """Test getting posts using the plugin fixtures"""
    # Make API request
    response = api_client.get("wp-json/wp/v2/posts")
    
    # Assert response
    assert_api.status_code(response, 200)
    assert_api.has_content(response)


@pytest.mark.api
def test_get_specific_post(api_client, assert_api):
    """Test getting a specific post"""
    # Make API request
    response = api_client.get("wp-json/wp/v2/posts/1")
    
    # Assert response
    assert_api.status_code(response, 200)
    assert_api.has_content(response)
    
    # Check JSON structure
    assert_api.json_contains(response, "id")
    assert_api.json_contains(response, "title")


@pytest.mark.api
def test_create_post(api_client, assert_api):
    """Test creating a new post"""
    post_data = {
        "title": "Test Post",
        "content": "This is a test post content",
        "status": "publish"
    }
    
    # Make API request
    response = api_client.post("wp-json/wp/v2/posts", data=post_data)
    
    # Assert response
    assert_api.status_code(response, 201)  # Created
    assert_api.has_content(response)


@pytest.mark.api
def test_update_post(api_client, assert_api):
    """Test updating an existing post"""
    update_data = {
        "title": "Updated Test Post",
        "content": "This is updated content"
    }
    
    # Make API request
    response = api_client.put("wp-json/wp/v2/posts/1", data=update_data)
    
    # Assert response
    assert_api.status_code(response, 200)
    assert_api.has_content(response)


@pytest.mark.api
def test_delete_post(api_client, assert_api):
    """Test deleting a post"""
    # Make API request
    response = api_client.delete("wp-json/wp/v2/posts/1")
    
    # Assert response
    assert_api.status_code(response, 200)
    # Note: WordPress might return 404 if post doesn't exist


@pytest.mark.api
def test_authenticated_request(api_client, assert_api):
    """Test authenticated request"""
    response = api_client.get("wp-json/wp/v2/users/me")
    
    # Assert response
    assert_api.status_code(response, 200)
    assert_api.has_content(response)


@pytest.mark.api
def test_with_custom_headers(api_client, assert_api):
    """Test request with custom headers"""
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    # Make request with custom headers
    response = api_client.get(
        "wp-json/wp/v2/posts",
        headers=headers
    )
    
    # Assert response
    assert_api.status_code(response, 200)
    assert_api.has_content(response)


@pytest.mark.api
def test_with_query_parameters(api_client, assert_api):
    """Test request with query parameters"""
    params = {
        "per_page": 5,
        "page": 1
    }
    
    # Make request with parameters
    response = api_client.get(
        "wp-json/wp/v2/posts",
        params=params
    )
    
    # Assert response
    assert_api.status_code(response, 200)
    assert_api.has_content(response)


@pytest.mark.api
def test_legacy_api_class_usage():
    """Example of using the legacy API class directly"""
    from pyrest import API
    
    username, password = get_wp_auth()
    
    # Create API instance
    api = API(
        address="http://localhost:8888/wp-json/wp/v2/posts",
        method="GET",
        user=username,
        password=password,
    )
    
    # Make request
    api.CallAPI()
    
    # Assert response
    assert api.status == 200
    assert len(api.content) > 0


@pytest.mark.api
def test_legacy_assertions():
    """Example of using legacy assertion functions"""
    from pyrest import API, AssertTest, AssertSearch
    
    username, password = get_wp_auth()
    
    # Create API instance
    api = API(
        address="http://localhost:8888/wp-json/wp/v2/posts",
        method="GET",
        user=username,
        password=password,
    )
    
    # Make request
    api.CallAPI()
    
    # Use legacy assertions
    AssertTest(
        testObject=api,
        assertTest="testObject.status == 200",
        message="Expected status code 200"
    )
    
    AssertSearch(api, "title")

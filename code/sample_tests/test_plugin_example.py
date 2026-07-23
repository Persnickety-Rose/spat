"""
Example tests using the pytest-pyrest plugin
"""
import pytest

created_post_id = None


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

    global created_post_id
    created_post_id = response.json["id"]


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
    assert created_post_id is not None, "test_create_post must run first"
    response = api_client.delete(f"wp-json/wp/v2/posts/{created_post_id}")
    
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

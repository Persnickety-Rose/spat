#!/usr/bin/env python
################################################################################
# Description: Migrated version of test_wpT02.py using the plugin framework     #
# This demonstrates how to migrate from traditional to plugin approach          #
# Author: Jasmine-Arabella Post                                                 #
# Date Started: 20171122                                                        #
################################################################################

import pytest
from random import choice
from string import ascii_letters
import logging
import datetime
from random_word import RandomWords
import json
import os

# Setup time stamp
now = datetime.datetime.now()
time = now.strftime("%d--%H%M%S")
number_name = now.strftime("%H%M%S")

# Setup Logging
myLogger = logging.getLogger('myLogger')
myLogger.setLevel(logging.DEBUG)


@pytest.mark.api
def test_get_pages(request, wp_client, assert_api):
    """Migrated version of test_tmp() using plugin framework"""
    test_name = request.node.name
    myLogger.info("Test " + test_name + " is starting")
    
    response = wp_client.get_pages()
    
    assert_api.status_code(response, 200)
    assert_api.has_content(response)
    assert len(response.content) > 10, "There was no data sent back from the call"
    
    myLogger.info("This test passed\n")


@pytest.mark.api
def test_get_posts(request, wp_client, assert_api):
    """Migrated version of test_Get_Posts() using plugin framework"""
    test_name = request.node.name
    myLogger.info("Test " + test_name + " is starting")
    
    response = wp_client.get_posts()
    
    assert len(response.content) > 0
    assert_api.status_code(response, 200)
    assert_api.has_content(response)
    
    myLogger.info("This test passed\n")


@pytest.mark.api
def test_get_posts_call_succeeded(request, wp_client, assert_api):
    """Migrated version of test_Get_Posts_Call_Succeeded() using plugin framework"""
    test_name = request.node.name
    myLogger.info("Test " + test_name + " is starting")
    
    response = wp_client.get_posts()
    
    assert len(response.content) > 0
    assert_api.status_code(response, 200)
    assert_api.has_content(response)
    
    myLogger.info("This test passed\n")


@pytest.mark.api
def test_get_posts_call_failed(request, wp_client, assert_api):
    """Migrated version of test_Get_Posts_Call_Failed() using plugin framework"""
    test_name = request.node.name
    myLogger.info("Test " + test_name + " is starting")
    
    # Test with a bad endpoint - this would need to be implemented in the client
    # For now, we'll test with a non-existent post ID
    response = wp_client.get_post(99999)  # Non-existent post
    
    assert len(response.content) > 0
    assert_api.status_code(response, 404)
    
    myLogger.info("This test passed\n")


@pytest.mark.api
def test_make_good_new_post(request, authenticated_wp_client, assert_api):
    """Migrated version of test_Make_Good_New_Post() using plugin framework"""
    test_name = request.node.name
    myLogger.info("Test " + test_name + " is starting")
    
    post_title = 'This is cow number ' + number_name
    content = ''.join(choice(ascii_letters) for i in range(120))
    
    response = authenticated_wp_client.create_post(
        title=post_title,
        content=content,
        status="publish"
    )
    
    assert len(response.content) > 0
    assert_api.status_code(response, 201)
    assert_api.has_content(response)
    
    myLogger.info("This test passed\n")


@pytest.mark.api
def test_make_failed_new_post(request, wp_client, assert_api):
    """Migrated version of test_Make_Failed_New_Post() using plugin framework"""
    test_name = request.node.name
    myLogger.info("Test " + test_name + " is starting")
    
    post_title = 'This is the ' + ''.join(choice(ascii_letters) for i in range(12)) + ' big dead cow'
    content = ''.join(choice(ascii_letters) for i in range(120))
    
    # This test expects a 401 error when no authentication is provided
    # We'll test this by creating a client without authentication
    from apis.wp_api_client import WordPressAPIClient
    
    unauthenticated_client = WordPressAPIClient(
        base_url=os.getenv("envURL", "http://localhost:8888"),
        username="",
        password=""
    )
    
    # This should raise a ValueError since we're trying to create a post without auth
    with pytest.raises(ValueError, match="Username and password required"):
        unauthenticated_client.create_post(
            title=post_title,
            content=content,
            status="publish"
        )
    
    myLogger.info("This test passed\n")


@pytest.mark.api
def test_make_good_new_post_2(request, authenticated_wp_client, assert_api):
    """Migrated version of test_Make_Good_New_Post_2() using plugin framework"""
    test_name = request.node.name
    myLogger.info("Test " + test_name + " is starting")
    
    post_title = 'There are ' + number_name + ' cows'
    words = RandomWords()
    rWords = words.get_random_word()
    content = ' '.join(rWords for i in range(600))
    
    response = authenticated_wp_client.create_post(
        title=post_title,
        content=content,
        status="draft"
    )
    
    assert len(response.content) > 0
    assert_api.status_code(response, 201)
    assert_api.has_content(response)
    
    myLogger.info("This test passed\n")


# End of File
# ==============================================================================

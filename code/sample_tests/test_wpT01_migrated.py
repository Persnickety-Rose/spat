#!/usr/bin/env python
################################################################################
# Description: Migrated version of test_wpT01.py using the plugin framework    #
# This demonstrates how to migrate from traditional to plugin approach         #
# Author: Jasmine-Arabella Post                                                #
# Date Started: 20171122                                                       #
################################################################################

import pytest
import inspect
import logging
import datetime
import os
from apis.wp_api_client import wp_client, assert_api

# Set time stamp
now = datetime.datetime.now()
time = now.strftime("%d--%H%M%S")
number_name = now.strftime("%H%M%S")

# Setup Logging
myLogger = logging.getLogger('myLogger')
myLogger.setLevel(logging.DEBUG)


@pytest.mark.api
def test_get_pages():
    """Migrated version of test_tmp() using plugin framework"""
    test_name = inspect.stack()[0][3]
    myLogger.info("Test " + test_name + " is starting")
    
    # Use plugin framework instead of traditional approach
    response = wp_client.get_pages()
    
    # Use plugin assertion helpers
    assert_api.status_code(response, 200)
    assert_api.has_content(response)
    
    # Additional assertion equivalent to the original
    assert len(response.content) > 10, "There was no data sent back from the call"
    
    myLogger.info("This test passed\n")


# End of File
# ==============================================================================

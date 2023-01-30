#!/usr/bin/env python
########################################################################################################################
# Description:  Test clase file for WordPress RESTful API                                                              #
# This is an example of how a restful api class file should be written                                                 #
# Author: Jasmine-Arabella Post                                                                                        #
# Date Started: some time before 20160901                                                                              #
########################################################################################################################


#########################
#     Setup stuff       #
#########################
import pytest

# import local code
import repackage
repackage.up(2)
from pyrest.API_Call import API

default_header = ""


############################################################
#                    Test Classes                          #
############################################################
class GetAllUsers(API):
    """
    This class uses the 'user' endpoint to get a list of all of the users
    """
    def __init__(self, user, password, env):
        """
        :param user: --REQUIRED-- the user to log in with
        :param password: --REQUIRED-- the password to log in with
        :param env: --REQUIRED-- the environment you are testing it
        """
        endpoint = "/wp-json/wp/v2/users"
        self.address = env + endpoint
        self.method = "GET"
        self.user = user
        self.password = password
        self.data = ""
        self.header = default_header
        self.params = ""


class GetUser(API):
    """
    This Class gets the current user info
    """
    def __init__(self, user, password, env):
        """
        :param user: --REQUIRED-- the user to log in with
        :param password: --REQUIRED-- the password to log in with
        :param env: --REQUIRED-- the environment you are testing it
        """
        endpoint = "/wp-json/wp/v2/users/me"
        self.address = env + endpoint
        self.method = "GET"
        self.user = user
        self.password = password
        self.data = ""
        self.header = default_header
        self.params = ""


class GetAllPosts(API):

    def __init__(self, env):
        endpoint = "/wp-json/wp/v2/posts"
        self.address = env + endpoint
        self.method = "GET"
        self.password = ""
        self.user = ""
        self.data = ""
        self.header = default_header
        self.params = ""


class GetPosts(API):

    def __init__(self, env):
        endpoint = "/wp-json/wp/v2/posts"
        self.address = env + endpoint
        self.method = "GET"
        self.password = ""
        self.user = ""
        self.data = ""
        self.header = default_header
        self.params = ""


class GetPosts_bad(API):

    def __init__(self, env):
        """
        GetPosts_bad has a bad URL so it will always fail
        This is for testing of the test system only
        """
        endpoint = "/wp-json/wp/v123/posts"
        self.address = env + endpoint
        self.method = "GET"
        self.password = ""
        self.user = ""
        self.data = ""
        self.header = default_header
        self.params = ""


class PostNewPost(API):

    def __init__(self, user, data, env, password="password"):
        endpoint = "/wp-json/wp/v2/posts"
        self.address = env + endpoint
        self.method = "POST"
        self.user = user
        self.password = password
        self.data = data
        self.header = default_header
        self.params = ""


class GetAllCategories(API):


    def __init__(self, env):
        endpoint = "/wp-json/wp/v2/categories"
        self.address = env + endpoint
        self.method = "GET"
        self.password = ""
        self.user = ""
        self.data = ""
        self.header = default_header
        self.params = ""


class PostNewPage(API):

    def __init__(self, user, data, env, password="password"):
        endpoint = "/wp-json/wp/v2/pages"
        self.address = env + endpoint
        self.method = "POST"
        self.user = user
        self.password = password
        self.data = data
        self.header = default_header
        self.params = ""


class PostUpdatePage(API):

    def __init__(self, user, page_id, data, env, password="password"):
        endpoint = "/wp-json/wp/v2/pages/" + str(page_id)
        self.address = env + endpoint
        self.method = "POST"
        self.user = user
        self.password = password
        self.data = data
        self.header = default_header
        self.params = ""


class GetPages(API):

    def __init__(self, env, data=''):
        endpoint = "/wp-json/wp/v2/pages/"
        self.address = env + endpoint
        self.method = "GET"
        self.user = ""
        self.password = ""
        self.data = data
        self.header = default_header
        self.params = ""


# End of File
# ==============================================================================

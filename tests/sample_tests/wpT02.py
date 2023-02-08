#! /usr/bin/env python
################################################################################
# Description: These are some sample tests                                     #
# They are based on the WP API                                                 #
# Author: Jasmine-Arabella Post                                                      #
# Date Started: 20171122                                                       #
################################################################################


#########################
#    Imports & Setup    #
#########################
import pytest
import inspect
from random import choice
from string import ascii_letters
import logging
import datetime
from random_word import RandomWords
import json
from apis import WP_APIs
import os

# imports from local code
import repackage
repackage.up(1)
from pyrest.util import AssertTest

# setup time stamp
now = datetime.datetime.now()
time = now.strftime("%d--%H%M%S")
number_name = now.strftime("%H%M%S")



#    Setup Logging
#=================
from pyrest import setup
myLogger = logging.getLogger('myLogger')
myLogger.setLevel(logging.DEBUG)

# Set environment to test in
# NOTE: must be done after import setup
env = str(os.getenv("envURL"))


############################################################
#                  Tests Starts Here                       #
############################################################

def test_tmp():
    test_name = inspect.stack()[0][3]
    myLogger.info("Test " + test_name + " is starting")
    test = WP_APIs.GetPages(env)
    test.CallAPI()
    test.Call_Succeeded(test)

    # Trying to figure out the issue with my assertTest function
    AssertTest(testObject=test, assertTest = str(len(test.content)) + " > 10",
                       message="There was no data sent back from the call")

    myLogger.info("This test passed\n")


def test_Get_Posts():
    test_name = inspect.stack()[0][3]
    myLogger.info("Test " + test_name + " is starting")
    test = WP_APIs.GetPosts(env)
    test.CallAPI()
    assert (len(test.content) > 0)
    test.Call_Succeeded(test)
    myLogger.info("This test passed\n")


def test_Get_Posts_Call_Succeeded():
    test_name = inspect.stack()[0][3]
    myLogger.info("Test " + test_name + " is starting")
    test = WP_APIs.GetPosts(env)
    test.CallAPI()
    assert (len(test.content) > 0)
    test.Call_Succeeded(test)
    myLogger.info("This test passed\n")


def test_Get_Posts_Call_Failed():
    test_name = inspect.stack()[0][3]
    myLogger.info("Test " + test_name + " is starting")
    test = WP_APIs.GetPosts_bad(env)
    test.CallAPI()
    assert (len(test.content) > 0)
    test.Call_Failed(test, return_code="404", returns_content='yes')
    myLogger.info("This test passed\n")


def test_Make_Good_New_Post(capsys):
    test_name = inspect.stack()[0][3]
    myLogger.info("Test " + test_name + " is starting")
    post_title = 'This is cow number ' + number_name
    content = ''.join(choice(ascii_letters) for i in range(120))
    data = {'status': 'publish', 'Content-Type': 'application/x-www-form-urlencoded'}
    data['title'] = post_title
    data['content_raw'] = content
    test = WP_APIs.PostNewPost(user='testAdmin01', data=data, env=env)
    test.CallAPI()

    if not len(test.content) > 0:
        assert len(test.content) > 0
        out, err = capsys.readouterr()
        myLogger.error("Out put: ", out)
        myLogger.error("Error is: " + err)
        myLogger.error("This test FAILED")
        return

    if not test.status == int("201"):
        assert test.status == int("201"), "We didn't get the expected return code"
        out, err = capsys.readouterr()
        myLogger.error("Out put: ")
        myLogger.error("Error is: ", err)
        myLogger.error("This test FAILED")
        return
    test.Call_Succeeded(test, return_code="201")
    myLogger.info("This test passed\n")


def test_Make_Failed_New_Post():
    test_name = inspect.stack()[0][3]
    myLogger.info("Test " + test_name + " is starting")
    post_title = 'This is the ' + ''.join(choice(ascii_letters) for i in range(12)) + ' big dead cow'
    content = ''.join(choice(ascii_letters) for i in range(120))
    data = {'status': 'publish', 'Content-Type': 'application/x-www-form-urlencoded'}
    data['title'] = post_title
    data['content_raw'] = content
    test = WP_APIs.PostNewPost(user='', data=data, env=env)
    test.CallAPI()
    assert (test.status == int("401"))
    assert (str(test.content).find("Sorry, you are not allowed to create posts as this user.") > 0 )
    test.Call_Failed(test, return_code='401', returns_content='yes')
    myLogger.info("This test passed\n")


def test_Make_Good_New_Post_2(capsys):
    test_name = inspect.stack()[0][3]
    myLogger.info("Test " + test_name + " is starting")
    post_title = 'There are ' + number_name + ' cows'
    rWords = RandomWords()
    content = ' '.join(rWords.random_word() for i in range(600))
    data = {'status': 'draft', 'Content-Type': 'application/x-www-form-urlencoded'}
    data['title'] = post_title
    data['content_raw'] = content
    test = WP_APIs.PostNewPost(user='testAdmin01', data=data, env=env)
    test.CallAPI()

    if not len(test.content) > 0:
        assert len(test.content) > 0
        out, err = capsys.readouterr()
        myLogger.error("Out put: ", out)
        myLogger.error("Error is: " + err)
        myLogger.error("This test FAILED")
        return

    if not test.status == int("201"):
        assert test.status == int("201"), "We didn't get the expected return code"
        out, err = capsys.readouterr()
        myLogger.error("Out put: ")
        myLogger.error("Error is: ", err)
        myLogger.error("This test FAILED")
        return
    test.Call_Succeeded(test, return_code="201")
    myLogger.info("This test passed\n")


# End of File
# ==============================================================================

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
import logging
import datetime
from apis import WP_APIs
import os

# imoports from local files
import repackage
repackage.up(1)
from pyrest.util import *

# Set time stamp
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
    test = WP_APIs.GetPages(env=env)
    test.CallAPI()
    test.Call_Succeeded(test)

    # Trying to figure out the issue with my assertTest function
    AssertTest(testObject=test, assertTest = str(len(test.content)) + " > 10",
                       message="There was no data sent back from the call")

    myLogger.info("This test passed\n")


# End of File
# ==============================================================================

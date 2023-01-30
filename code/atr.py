#! /usr/bin/env python
########################################################################################################################
# Description: atr is the "API Test Runner" to run API tests via py.tesrt                                                         #
# Author: Jasmine-Arabella Post                                                                                        #
# Date Started:  20161028                                                                                              #
########################################################################################################################


#########################
#      Setup Stuff      #
#########################
import os
import argparse
import logging
from argparse import RawTextHelpFormatter
from subprocess import call
import re



#   Process CLI Options
#======================
app_description = """ATR is API Test Runner
----------------------
This test runner will take a py.test formatted file
and run it in the given environment.
"""
parser = argparse.ArgumentParser(description=app_description, formatter_class=RawTextHelpFormatter)

# Required parameters
required = parser.add_argument_group("Required")
required.add_argument('-e', '--environment', dest='env', action="store", default="qa",
                      choices=['dev', 'qa', 'prod'],
                      help="This sets the server environment the test will be run against")
required.add_argument('-f', '--file2test', dest='test_file', action='store', required=True,  help="The file to test (jmx).")

# optional parameters
parser.add_argument('-d', '--debug', dest="debug", action="store_true",  default=False,
                    help="This option sets logging to debug mode. The default is INFO")
parser.add_argument('-v', '--variables', dest="vars", action="store",
                    help="This option allows you to use a CSV file to add more global variables to your test suite")

userOptions = parser.parse_args()


#   Set Environment to Test In
#=============================
# build path to file
envFile = userOptions.env + "-environment.csv"
cwd = os.getcwd()

# need to get the path out of test_file
# then replayc /pyrest/ with that
path4test = os.path.dirname(userOptions.test_file)
path2file = "{}/{}/env/{}".format(cwd, path4test, envFile)

# Verify path to environment configuration file
if not os.path.isfile(path2file):
    print( "Could not find '" + str(path2file) + "', the environment file.  There for tests can not be run.")
    exit()

# Set path file to OS env var
os.environ["pyTestEnv"] = path2file



#    Set Log Level
#=================
# Defaults to INFO, but can be set to DEBUG
if userOptions.debug:
    os.environ["pyTestDebug"] = 'true'


#   Set Other Variables
#======================
if userOptions.vars:
    os.environ["pyTestVars"] = userOptions.vars


########################################
#           Call py.test               #
########################################

# check for specific test
look4test = re.compile('::.*')
bearFile = look4test.sub("", userOptions.test_file)


# Verify path to test file
if not os.path.isfile(bearFile):
    print( "Could not find '" + bearFile + "', the test file.  There for tests can not be run.")
    exit()

os.environ["pyTestFile"] = userOptions.test_file

# Call py.test
call(["py.test","-v", userOptions.test_file])


# End of File
# ==============================================================================
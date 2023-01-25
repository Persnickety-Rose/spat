#! /usr/bin/env python
########################################################################################################################
# Description:  This just sets up some variables, imports etc. for interactive testing                                 #
# Author: Jasmine-Arabella Post                                                                                        #
# Date Started: 20161020                                                                                               #
########################################################################################################################
# NOTE: as of 20190809 this does not work with test environment files or test opitonal files


#########################
#      Setup Stuff      #
#########################
import util
import logging
import datetime
import os
from util import *

# setup a time stamp
now = datetime.datetime.now()
myTime = now.strftime("%Y%m%d-%H%M%S")



#   Test Environment Variables
#=============================
# the following is needed to replace the work of the test runner.
envFile = "qa-environment.csv"
cwd = os.getcwd()
path2file = cwd + "/pyrest/" + envFile
os.environ["pyTestEnv"] = path2file
os.environ["pyTestFile"] = "Adhock"
os.environ["pyTestDebug"] = 'true'


########################################
#           Setup Logging              #
########################################
# create time stamp for logging
now = datetime.datetime.now()
time = now.strftime("%d%H%M%S")
number_name = time

# build loggers
myLogger = logging.getLogger()

# Check to see if we are using DEBUG or INFO
if os.getenv("pyTestDebug"):
    myLogger.setLevel(logging.DEBUG)
    l_level = "DEBUG"
else:
    myLogger.setLevel(logging.INFO)
    l_level = "INFO"

# Get full path to log file
testfilename =   os.environ["pyTestFile"].strip(".py").replace('/','-')
log_file_name = "logs/{time}-{filename}.log".format(time=time, filename=testfilename)

log_handler = logging.FileHandler(log_file_name)
log_handler.setLevel(logging.NOTSET)
myLogger.addHandler(log_handler)

# build log file header
formatter0 = logging.Formatter()
log_handler.setFormatter(formatter0)
myLogger.info("============================================================")
myLogger.info("  The following is some basic info on this log file")
myLogger.info("------------------------------------------------------------")
myLogger.info("The log file is: " + log_file_name)
myLogger.debug("The environment variables are: " + str(os.environ))

# see if we have optional varialbes and add them
if os.getenv("pyTestVars"):
      varsFile = os.environ["pyTestVars"]
      myLogger.debug("The optional variables CSV file is: " + varsFile)
      get_additional_var()

# finish the log header
formatter1 = logging.Formatter('Log file created at: %(asctime)s \nThe test file is: ' +  os.environ["pyTestFile"]  + '\nThe log level is: ' + l_level)
log_handler.setFormatter(formatter1)
myLogger.info("")

# setup header for regular logging statements
log_handler.setFormatter(formatter0)
myLogger.info("\nDate        Time         Line   Level     Message")
myLogger.info("============================================================")

# set format for regular logging statements
formatterFinal = logging.Formatter('%(asctime)s - %(lineno)d  - %(levelname)s - %(message)s')
log_handler.setFormatter(formatterFinal)


#   Some helper functions
#========================
def newName():
  """
  A function to create a name with a time stamp
  """
    now = datetime.datetime.now()
    nowtime = now.strftime("%f")
    returnString = "JP-" + str(nowtime)
    return returnString


############################################################
#          Setup is done, start testing                    #
############################################################
# the following two lines allow you to import as if you are
# above the pyrest folder
import repackage
repackage.up()

from sample_tests.apis import WP_APIs

myEnv = "https://my_wp-mfpost902951.codeanyapp.com"


# End of File
# ==============================================================================

#! /usr/bin/env python
########################################################################################################################
# Description:  This file is run before every test suite to do some setup work.                                        #
# Author: Jasmine-Arabella Post                                                                                        #
# Date Started: 20161028                                                                                               #
########################################################################################################################


#########################
#     Setup Stuff       #
#########################
import os
import csv
import datetime
import logging
from . util import *


########################################
#  Process environment file variables  #
########################################
def get_env_var():
  """
  This sets up the environment variables from the env file.
  """
  # get the current env that is bing tested
  if os.getenv("pyTestEnv"):
      envFile = os.environ["pyTestEnv"]
      myLogger.debug("The env CSV file is: " + envFile)
  else:
      msg =  "Could not find the environment file parameter.  There for tests can not be run."
      myLogger.error(msg=msg)
      print(msg)
      exit()

  # read csv file into env. variables 
  readCsvFile = csv.reader(open(envFile, 'r'))
  varDict = {}
  for row in readCsvFile:
      csvKey, csvValue = row
      myLogger.debug("Adding this variable: " + str(csvKey))
      os.environ[str(csvKey)] = str(csvValue)
    

########################################
#     Process additional variables     #
########################################    
#  The following is for processing additional global variables.
#  This is so that you can have variables that are not associated
#  with the environment, but are global to all tests.

def get_additional_var():
  """
  Sets up additonal environment variables from the optional file
  """
  # get the current env that is bing tested
  if not os.path.isfile(varsFile):
      msg = "Could not find '" + str(varsFile) + "', the additional variables file.  There for tests can not be run."
      myLogger.error(msg=msg)
      print(msg)
      exit()
  else:

      # read vars file into dictionary
      readVarsFile = csv.reader(open(varsFile, 'r'))
      varDict2 = {}
      for row in readVarsFile:
          csvKey, csvValue = row
          myLogger.debug("Adding optional variable: " + str(csvKey))
          os.environ[str(csvKey)] = str(csvValue)  
    

########################################
#          Setup Logging               #
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

# set envrionment variabless
get_env_var()
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




# End of File
# ==============================================================================
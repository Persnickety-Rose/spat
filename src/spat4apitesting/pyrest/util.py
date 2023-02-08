#!/usr/bin/env python
########################################################################################################################
# Description:  some utility functions for py.test                                                                     #
# Author: Jasmine-Arabella Post                                                                                        #
# Date Started: 20160929                                                                                               #
########################################################################################################################


#########################
#     Setup Stuff       #
#########################
import logging
utilLog = logging.getLogger('myLogger')
utilLog.setLevel(logging.INFO)


############################################################
#                 The assert functions                    #
############################################################

def AssertTest(testObject, assertTest, message, assertError="yes"):
    """
    This method does an assertion test and logs the resluts

    :param testObject: --REQUIRED-- the object created by the test
    :param assertTest: --REQUIRED-- the assert statement to tesat for
    :param message: --REQUIRED-- the messaage logged to explain the issue
    :param assertError: Raise an assertion error.    Default YES
    """

    if not eval(assertTest):        
        utilLog.error("= = = = = = = = = = = Error = = = = = = = = = = = ")
        utilLog.error(message)
        utilLog.error("The method used is: " + testObject.method)
        utilLog.error("The url called is: " + testObject.address)
        utilLog.error("The header sent is: " + str(testObject.header))
        utilLog.error("The data sent is: " + str(testObject.data))

        try:
            utilLog.error("The return header was: " + str(testObject.return_headers))
        except:
            utilLog.error("The return header was not returned")

        try:
            utilLog.error("The data returned was: " + str(testObject.content))
        except:
            utilLog.error("The return data was not returned")

        utilLog.error("= = = = = = = = = = Test Failed = = = = = = = = = = \n")

        if assertError == "yes":
            raise AssertionError
        else:
            return "failed"


def AssertSearch(testObject, searchTerm, assertError="yes"):
    """
    This method searches for a string in the return content and logs the resluts

    :param testObject: --REQUIRED-- the object created by the test
    :param searchTerm: --REQUIRED-- the text to search for
    :param assertError: Raise an assertion error.    Default YES
    """
  
    # - 2Do - add ability to input a list of search terms
    # - 2Do - add option to log INFO that the search term found
    # - 2Do - add option for regx search

    if not testObject.content.find(searchTerm) > 0:
        utilLog.error("= = = = = = = = = = = Error = = = = = = = = = = = ")
        errorMessage = "Could NOT find '" + searchTerm + "' in the returned content"
        utilLog.error(errorMessage)
        utilLog.error("The method used is: " + testObject.method)
        utilLog.error("The url called is: " + testObject.address)
        utilLog.error("The header sent is: " + str(testObject.header))
        utilLog.error("The data sent is: " + str(testObject.data))

        try:
            utilLog.error("The return header was: " + str(testObject.return_headers))
        except:
            utilLog.error("The return header was not returned")

        try:
            utilLog.error("The data returned was: " + str(testObject.content))
        except:
            utilLog.error("The return data was not returned")

        utilLog.error("= = = = = = = = = = Test Failed = = = = = = = = = = \n")

        if assertError == "yes":
            raise AssertionError
        else:
            return "failed"


# End of File
# ==============================================================================
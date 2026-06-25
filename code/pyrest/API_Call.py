#! /usr/bin/env python
########################################################################################################################
# Description: This file contains the base class for calling API's                                                     #
# Author: Jasmine-Arabella Post                                                                                        #
# Date Started: 20160922                                                                                              #
########################################################################################################################


#########################
#    Setup Stuff      #
#########################
import requests
import json
import re
import logging
import ssl

# setting up logging
callLogger = logging.getLogger('myLogger')
callLogger.setLevel(logging.NOTSET)

# Create a custom SSL context with secure defaults
ssl_context = ssl.create_default_context()
ssl_context.minimum_version = ssl.TLSVersion.TLSv1_2
ssl_context.verify_mode = ssl.CERT_REQUIRED


############################################################
#                     API Class                        #
############################################################
class API(object):
    """
    This is the base class for all APIs that are to be tested.  This class uses the requests library to make the call
    and has other methods for analyzing the results.
    """

    def __init__(self, address, data="", header="", method="GET", params="", user="", password="", verify_ssl=True, cert_path=None):
        """
        :param address: --REQUIRED-- The full url being called.
        :param data: Any and all data that needs to be sent as part of the payload
        :param header: The API call headers
        :param method: What request method should be used
        :param params: Any URL parameters that need to be passed
        :param user: The log in user if needed
        :param password: The log in users password if needed
        :param verify_ssl: Whether to verify SSL certificates (default: True)
        :param cert_path: Path to custom CA certificate bundle (default: None)
        """
        self.address = address
        self.params = params
        self.method = method
        self.header = header
        self.user = user
        self.password = password
        self.data = data
        self.verify_ssl = verify_ssl
        self.cert_path = cert_path

    ########################################
    #          Method to call API          #
    ########################################
    def CallAPI(self):
        """
        This method makes the actual API call.
        After a successful API call the following attributes are available.
          <object>.json is the JSON returned from the call
          <object>.content is the content returned, JSON, text or otherwise
          <object>.return_headers is the text of the returned headers
          <object>.url is the called URL
          <object>.status is the returend status
          <object>.body is the request body
        :return: the return status of the call made
        """
        global info, testFAILED
        testFAILED = "false"

        def logFailedTest():
            """
            This little method is just used to log failed API calls
            :return: Nothing
            """
            global testFAILED
            callLogger.error("= = = = = = = = = = = Error = = = = = = = = = = = ")
            callLogger.error("The framework failed to call the API ")
            callLogger.error("The method used is: " + self.method)
            callLogger.error("The url called is: " + self.address)
            callLogger.error("The header sent is: " + str(self.header))
            callLogger.error("The date sent is: " + str(self.data))
            callLogger.error("= = = = = = = = = = Test Failed = = = = = = = = = = \n")

            testFAILED = "true"
            # raise  AssertionError


        
        #   Make the API call
        #====================

        # Setup request parameters
        request_params = {
            "method": self.method,
            "url": self.address,
            "verify": self.cert_path if self.cert_path else self.verify_ssl
        }
        
        if self.header != "":
            request_params["headers"] = self.header

        if self.params != "":
            request_params["params"] = self.params

        if self.data != "":
            request_params["data"] = self.data

        # Make call
        if self.user:
            try:
                info = requests.request(auth=(self.user, self.password), **request_params)
            except requests.RequestException as e:
                callLogger.error(f"SSL/TLS Error: {str(e)}")
                logFailedTest()
        else:
            try:
                info = requests.request(**request_params)
            except requests.RequestException as e:
                callLogger.error(f"SSL/TLS Error: {str(e)}")
                logFailedTest()

        # for debug what was sent
        callLogger.debug("                                ---New API Call---")
        callLogger.debug("The method used is: " + self.method)
        callLogger.debug("The url called is: " + self.address)
        callLogger.debug("The header sent is: " + str(self.header))
        callLogger.debug("The date sent is: " + str(self.data))

        # what was returned
        if not testFAILED == "true":
            callLogger.debug("The return code was: " + str(info.status_code))
            callLogger.debug("The header returned is: " + str(info.headers))
            callLogger.debug("The content returned is: " + str(info.content))

            # is the return code json or http
            if re.search(r'DOCTYPE html', str(info.content), flags=re.I):
                print("\n\nCall returned HTML, not json")
                callLogger.error("The API call returned HTML")
                return "FAILED"

        
        #  set some attributes
        #=====================
        # list of attributes
        listAttrib = ["self.json = info.json()", "self.content = info.content", "self.return_headers = info.headers",
                     "self.url = info.url", "self.status = info.status_code", "self.body = info.request.body",
                     "self.info = info"]
        # if URL was called loop through list of attributes to create
        if not testFAILED == "true":
            for atrib in listAttrib:
                try:
                    exec(atrib) in globals(), locals()
                except (AttributeError, ValueError, TypeError):
                    callLogger.error("Failed to create attribute: " + atrib)
                    pass
            returnMessage = self.status
        else:
            returnMessage = "Test Failed"

        return returnMessage

    ########################################
    #   Method to pretty print the JSON    #
    ########################################
    def JSON_PP(self):
        """
        This is a simple method to pretty print the returned JSON
        It is mainly used in interactive testing.
        :return: Nothing, but the JSON is printed to StdOut
        """
        global info
        json1 = json.loads(info.content)
        print( json.dumps(json1, indent=4, sort_keys=True))
        
        
# End of File
# ==============================================================================
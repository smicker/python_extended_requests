#!/usr/bin/python3

from requests_toolbelt import sessions      # pip install requests-toolbelt
from requests_toolbelt.utils import dump
from requests.adapters import HTTPAdapter   # pip install requests
from requests.packages.urllib3.util.retry import Retry
from requests.auth import HTTPBasicAuth
import http # Just for simple logging of web calls
import string

DEFAULT_TIMEOUT = 5 # seconds
DEFAULT_MAX_RETRIES = 3

# The backoff factor will make each consecutive retry of web call sleep different
# amount of seconds between each retry, calculated as:
# {backoff factor} * (2 ** ({number of total retries} - 1))
# Setting backoff factor to 1 will then sleep 0.5, 1, 2, 4, 8, 16, 32, 64 sec between retries.
# Setting it to 0 will disable exponential backoff.
DEFAULT_BACKOFF_FACTOR = 1

class WebCaller:
    '''
    This class is a helper class for web calling, for example GET and POST requests.
    It sets a default timeout of the web calls and also adds a retry mechanism with
    exponential backoff. It also has the possibility to set a base_url so you don't
    have to print out the whole url in each web call. The same goes for setting a
    basic auth so you don't need to provide that on every call.

    It is inspired by the info on this page:
    https://findwork.dev/blog/advanced-usage-python-requests-timeouts-retries-hooks/

    Args (All args are OPTIONAL):

    base_url            If you call a lot of pages with the same base url, ex. 
                        http://mypage.com/main and http://mypage.com/about etc,
                        you can set base_url to http://mypage.com and then you can just use
                        /main or /about as url when you do the calls later on.
    throw_on_problem    If True, all web calls will throw an HTTPError if the response code
                        is 4xx or 5xx. Default is True.
    timeout             Sets the timeout in seconds for a web call. Default is 5 sec.
                        Set to None to remove the default timeout.
    retries             Sets the amount of retries each web call shall do. Default is 3.
                        Set to 0 to have no retries.
    '''
    def __init__(self, base_url:string=None,
                 throw_on_problem:bool=True,
                 timeout:int=DEFAULT_TIMEOUT,
                 retries:int=DEFAULT_MAX_RETRIES):

        # Create a custom requests object. (Modifying the global requests module throws an error)
        self.web = sessions.BaseUrlSession(base_url=base_url)

        if throw_on_problem:
            # Create a hook that throws a HTTPError exception on every 4xx or 5xx response
            # from server.
            assert_status_hook = lambda response, *args, **kwargs: response.raise_for_status()
            self.web.hooks["response"] = [assert_status_hook]
        
        if retries and retries < 0: retries = 0
        retry_strategy = Retry(
            total = DEFAULT_MAX_RETRIES if retries is None else retries,
            status_forcelist = [429, 500, 502, 503, 504], # The HTTP response codes to retry on
            allowed_methods = ["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE", "POST"], # The methods to retry on
            backoff_factor = DEFAULT_BACKOFF_FACTOR 
        )
        adapter = TimeoutHTTPAdapter(timeout=timeout, max_retries=retry_strategy)

        # Mount the timeout and retry adapter for both http and https usage
        self.web.mount("https://", adapter)
        self.web.mount("http://", adapter)

        self.auth = None

        # Enable simple logging (Prints headers etc but not body)
        #http.client.HTTPConnection.debuglevel = 1

        # Enable extended logging (Prints everything, including response body)
        #self.web.hooks["response"] = [self.__logging_hook]
    
    def __logging_hook(self, response, *args, **kwargs):
        '''Used as a response hook when activating extended logging'''
        data = dump.dump_all(response)
        print(data.decode('utf-8'))
    
    def setBasicAuth(self, user: string, password: string):
        '''Adds basic authentication to all consecutive web calls'''
        self.auth = HTTPBasicAuth(user, password)

    def __updateArgs(self, **kwargs) -> dict:
        '''Adds more default values, like auth, to the args sent to web calls'''
        # Add default authentication
        if not "auth" in kwargs:
            if self.auth:
                # Add default auth
                kwargs["auth"] = self.auth
        return kwargs

    def web_get(self, url, *args, **kwargs):
        '''
        Performs a get request. Use the same arguments as for the requests.get function.
        Note that a default timeout will be used. If no timeout is wanted add the arg timeout=-1
        or if a special timeout is wanted add the timeout=x where x is the amount of seconds.
        '''
        kwargs = self.__updateArgs(**kwargs)

        #print("Calling: " + (self.web.base_url if self.web.base_url else "") + url)
        return self.web.get(url, *args, **kwargs)
    

    def web_post(self, url, *args, **kwargs):
        '''
        Performs a post request. Use the same arguments as for the requests.post function.
        Note that a default timeout will be used. If no timeout is wanted add the arg timeout=-1
        or if a special timeout is wanted add the timeout=x where x is the amount of seconds.
        '''
        kwargs = self.__updateArgs(**kwargs)

        #print("Calling: " + (self.web.base_url if self.web.base_url else "") + url)
        return self.web.post(url, *args, **kwargs)

    def close(self):
        '''Close the web session'''
        self.web.close()

class TimeoutHTTPAdapter(HTTPAdapter):
    '''
    A special adapter that can be used to set a default web call timeout.
    To set the default timeout, pass the timeout=x as an argument to the init function
    where x is the amount of seconds to use. If the timeout argument is not set,
    this adapter will have no effect.
    Note that if you use this adapter and add the argument timeout=None to any web call
    that has mounted this adapter (like https or http), the default timeout will be used
    anyway. This is the same as not including the timeout argument at all. So if you want
    to turn off timeout for a web call you shall instead set timeout=-1.
    '''
    def __init__(self, *args, **kwargs):
        if "timeout" in kwargs:
            self.timeout = kwargs["timeout"]
            del kwargs["timeout"]
        super().__init__(*args, **kwargs)

    def send(self, request, **kwargs):
        timeout = kwargs.get("timeout")
        if timeout is None and self.timeout:
            # If timeout is not specified in the web call, use default value set in init.
            kwargs["timeout"] = self.timeout
        elif timeout == -1:
            del kwargs["timeout"]
        return super().send(request, **kwargs)
# Description: requester.py try get response given an url string
# Colaborators: Saulo Ricci
# Date: 01/02/2012

import socket
import time
import urllib2
import urllib
import random

TIMEOUT_SECS = 15

class requester:
    """
    Implements a interface to request data across the http protocol.
    Deals with the 500, 404 error and reports other ones if they rise.
    
    Args:
        url_str: the url to be requested
        dict_params: the params refered to HTTP GET.
    
    Returns:
        a tuple (Status, Url), where Status is about the status of the requesting process.
            Url contains the true url.
    """
    def __init__(self):
        socket.setdefaulttimeout(TIMEOUT_SECS)
        pass

    def get_url(self, url_str, dict_params=None, sleep_time=None):
        req = None

        if dict_params:
            params = urllib.urlencode(dict_params)
            req = urllib2.Request(url=url_str, data=params)
        else:
            req = urllib2.Request(url=url_str)

        try:
            f = urllib2.urlopen(req)
            url = f.geturl()
            f.close()
            if sleep_time:
                time.sleep(sleep_time + random.random())
            return (200, url)
        except urllib2.HTTPError, e:
            return (e.code, None)
        except Exception, e:
            return (e, None)

    def get_response(self, url_str, dict_params=None):
        """
        Getting the content of the url to be requested.
        Args:
            url_str: the url to be requested
            dict_param: some parameters to request in case of HTTP GET
        Returns:
            a tuple (Status, Content, Info), where Status is points to some status of the requesting,
            Content contains the page of content and Info about the requested.
        """
        req = None

        if dict_params:
            params = urllib.urlencode(dict_params)
            req = urllib2.Request(url=url_str, data=params)
        else:
            req = urllib2.Request(url=url_str)

        try:
            f = urllib2.urlopen(req)
            content = f.read()
            time.sleep(0.0001)
            info = f.info()
            f.close()
            return (200, content, info)
        except urllib2.HTTPError, e:
            return (e.code, None, None)
        except Exception, e:
            return (e, None, None)

def main():
    requester_obj = requester()
    status, response = requester_obj.get_url('https://foursquare.com/user/19455')
    #status, response = requester_obj.get_url('https://api.foursquare.com/v2/users/14242081?oauth_token=1YCVKX1ZGM2EGVIDYFEXSVGNHSM11VID3F5AVFV2TZLEQDTQ')
    print response
    print status

if __name__ == '__main__':
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import hashlib
import random
import sys
import urllib

import requests

from lib.core.common import outputscreen
from lib.core.data import th, conf

USER_AGENT = "Mozilla/5.0 (Windows; U; MSIE 10.0; Windows NT 9.0; es-ES)"
user_agent = {"user-agent": USER_AGENT}


class Inspector:
    """This class mission is to examine the behaviour of the application when on
        purpose an inexistent page is requested"""
    TEST404_OK = 0
    TEST404_MD5 = 1
    TEST404_STRING = 2
    TEST404_URL = 3
    TEST404_NONE = 4

    def __init__(self, target):
        self.target = target

    def _give_it_a_try(self):
        """Every time this method is called it will request a random resource
            the target domain. Return value is a dictionary with values as
            HTTP response code, resquest size, md5 of the content and the content
            itself. If there were a redirection it will record the new url"""
        s = []
        for n in range(0, 42):
            random.seed()
            s.append(chr(random.randrange(97, 122)))
        s = "".join(s)
        # Use urljoin to correctly handle URL concatenation, avoiding double slash issue
        target = urllib.parse.urljoin(self.target, s)

        outputscreen.success("[+] Checking with: {}".format(target))

        try:
            page = requests.get(target, headers=user_agent, verify=False,timeout=5, proxies=conf.proxy_server)
            content = page.content
            result = {
                    'target': urllib.parse.urlparse(target).netloc,
                    'code': str(page.status_code),
                    'size': len(content),
                    'md5': hashlib.md5(content).hexdigest(),
                    'content': content,
                    'location': None
                }

            if len(page.history) >= 1:
                result['location'] = page.url
            return result
        except:
            result = {
                    'target': urllib.parse.urlparse(target).netloc,
                    'code': '',
                    'size': '',
                    'md5': '',
                    'content': '',
                    'location': None
                }
            return result

    def check_this(self):
        """Get the a request and decide what to do"""
        first_result = self._give_it_a_try()

        if first_result['code'] == '404':
            #msg = '[+] Target: {} Got a nice 404, problems not expected'
            #outputscreen.success("\r{}{}".format(self.target,' '*(th.console_width-len(msg)+len(self.target)+1)))
            # Ok, resquest gave a 404 so we should not find problems
            return '', Inspector.TEST404_OK

        elif first_result['code'] == '302' or first_result['location']:
            location = first_result['location']
            return location, Inspector.TEST404_URL
        else:
            return first_result['md5'], Inspector.TEST404_MD5

        # We give up here :(
        return '', Inspector.TEST404_NONE

if __name__ == '__main__':
    i = Inspector(sys.argv[1])
    print(i.check_this())

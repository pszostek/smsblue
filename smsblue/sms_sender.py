#!/usr/bin/python
# -*- coding: utf-8 -*-

import httplib
import urllib

class SMSSender(object):
    host = "api.smsapi.pl"
    request = "/sms.do?username=%s&password=%s&to=%s&eco=%d&message=%s"
    
    def __init__(self, account, passmd5hash):
        self.account = account
        self.password = passmd5hash
    
    def send(self, number, message, eco=True):
        c = httplib.HTTPConnection(self.host)
        message = urllib.pathname2url(message)
        if eco:
            eco = 1
        else:
            eco = 0
        c.request("GET", self.request % (self.account, self.password, number, eco, message))
        r = c.getresponse()
        return r

if __name__ == "__main__":
    s = SMSSender("pawel.szostek@gmail.com", "30cca6d85c3a3e77169fcff6a9afcc58")
    r = s.send(number="886746648", message="dupa biskupa")
    print r.read()
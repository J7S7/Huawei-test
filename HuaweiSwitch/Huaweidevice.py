# -*- coding: utf-8 -*-
import telnetlib
import re

class HuaweiSwitch(object):
    def __init__(self,host=None,hostname=None,username=None,password=None,connected=False,port_lists=None):
        self.host=host
        self.hostname=hostname
        self.username=username
        self.password=password
        self.connected=connected
        self.port_lists=port_lists


    def connect(self,host=None,port=23,timeout=2):
        if host is None:
            host = self.host

        self._connection=telnetlib.Telnet(host,port,timeout)
        #self._authenticate()
        #self._get_hostname()
        self.connected = True
        a = self._connection.read_all()
        print('test:',a )
        print 'success'



    #def authenticate(self,username,password):
       # if
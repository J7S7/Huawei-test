# -*- coding: utf-8 -*-
import telnetlib
import re
from Huaweierror import *

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
        print 'connection success'

    def test(self):
        # 忽略U和P大小写情况
        idx, match, text = self._connection.expect(['sername:'], 5)
        print text

    def authenticate(self,username,password):
        idx, match, text = self.expect(['sername:', 'assword:'], 2)
        if match is None:
            raise AuthenticationError('无法获取到username或password输入提示',text)
        #无username情况
        elif match.group().count('assword'):
            self._connection.write(self.password + '\n')
            idx, match, text = self.expect(['assword', '>', '#'], 5)
            if match is not None and match.group().count('assword'):
                raise AuthenticationError("password错误")
        #有username情况
        elif match.group().count('sername'):
            if self.username is None:
                raise AuthenticationError("要求输入username，但username为空字段")
            else:
                self.write(self.username + '\n')
                idx, match, text = self.expect(['assword:'], 5)
                if match is None:
                    raise AuthenticationError("登陆异常")
                elif match.group().count('assword:'):
                    self.write(self.password + '\n')
                    idx, match, text = self.expect(['Error','>',']',':'], 5)
                    if match is None:
                        raise AuthenticationError("无反馈信息",text)
                    elif 'Error' in match.group():
                        raise AuthenticationError('登录失败，用户名或密码错误')

        else:
            raise AuthenticationError('认证有误',text)

    def expect(self, asearch, timeout=2):
        # 对需要进行read until 操作的字符进行ascii格式转换
        idx, match, result = self._connection.expect([needle.encode('ascii') for needle in asearch], timeout)
        return idx, match, result


    def write(self, text):
    #""" 将输入指令转换成设备可读的ascii格式 """
        if self._connection is None:
            self.connect()
            raise HuaweiSwitchError("未连接设备")

        self._connection.write(text.encode('ascii'))

    def







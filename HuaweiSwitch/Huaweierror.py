# -*- coding: utf-8 -*-


class HuaweiSwitchError(Exception):
    def __init__(self, value, text=''):
        self.value = value
        self.text = text

    def __str__(self):
        ret = self.value
        if self.text is not None and self.text != '':
            ret += "\n from ： " + str(self.text)
        return ret


class AuthenticationError(HuaweiSwitchError):
    pass


class InvalidCommand(HuaweiSwitchError):
    def __init__(self, cmd):
        self.cmd = cmd

    def __str__(self):
        ret = "错误命令 " + str(self.cmd)
        return ret

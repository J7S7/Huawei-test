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
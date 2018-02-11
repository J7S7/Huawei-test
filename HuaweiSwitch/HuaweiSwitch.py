# -*- coding: utf-8 -*-
import telnetlib
import re
from Huaweierror import *


class HuaweiSwitch(object):
    def __init__(self, host=None, hostname=None, username=None, super_password=None, password=None, connected=False, port_lists=None):
        self.host = host
        self.hostname = hostname
        self.username = username
        self.password = password
        self.connected = connected
        self.super_password = super_password
        self._connection = None
        self.port_lists = port_lists

    def connect(self, host=None, port=23, timeout=2):
        if host is None:
            host = self.host

        self._connection = telnetlib.Telnet(host, port, timeout)
        self._authenticate()
        self._get_hostname()
        self._super()
        self.cmd("screen-length 0 temporary")
        self.connected = True
        print 'connection success'

    def _authenticate(self):
        idx, match, text = self.expect(['sername:', 'assword:'], 2)
        if match is None:
            raise AuthenticationError('无法获取到username或password输入提示',text)
        # 无username情况
        elif match.group().count('assword'):
            self._connection.write(self.password + '\n')
            idx, match, text = self.expect(['assword', '>', '#'], 5)
            if match is not None and match.group().count('assword'):
                raise AuthenticationError("password错误")
        # 有username情况
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
                    idx, match, text = self.expect(['Error', '>', ']', ':'], 5)
                    if match is None:
                        raise AuthenticationError("无反馈信息", text)
                    elif 'Error' in match.group():
                        raise AuthenticationError('登录失败，用户名或密码错误')
        else:
            raise AuthenticationError('认证有误', text)

    def expect(self, asearch, timeout=2):
        # 对需要进行read until 操作的字符进行ascii格式转换
        idx, match, result = self._connection.expect([needle.encode('ascii') for needle in asearch], timeout)
        return idx, match, result

    def write(self, text):
        # """ 将输入指令转换成设备可读的ascii格式 """
        if self._connection is None:
            self.connect()
            raise HuaweiSwitchError('未连接设备')
        self._connection.write(text.encode('ascii'))

    def read_until_prompt(self, prompt=None, timeout=5):
        # 命令结束标示
        thost = self.hostname
        if thost is None:
            raise HuaweiSwitchError("设备未命名", text=None)
        if prompt is None:
            expect = [thost + ">"]
        else:
            expect = [thost + prompt]
        idx, match, ret_text = self.expect(expect, timeout)
        return ret_text

    def _get_hostname(self):
        # 获取设备名
        self.write("\n")
        idx, match, text = self.expect(['>'], 2)
        if match is not None:
            tmp = text.replace('<', ' ').strip()
            self.hostname = tmp.replace('>', '').strip()
        else:
            raise HuaweiSwitchError('无法获得设备名')

    def cmd(self, cmd_text):
        # 输入命令并得到反馈结果
        self.write(cmd_text + '\n')
        text = self.read_until_prompt()
        ret_text = ''
        # 去除多余回车
        for a in text.split('\n')[:-1]:
            ret_text += a + '\n'
        # 获取当前设备名称
        if 'hostname' in cmd_text:
            self._get_hostname()
        if 'rejected' in ret_text:
            raise InvalidCommand(cmd_text)
        return ret_text

    def _super(self, password=None):
        if password is not None:
            self.super_password = password
        self.write('\n')
        self.read_until_prompt()
        self.write("super" + '\n')
        idx, match, text = self.expect(['>', 'assword:'], 1)
        if match is None:
            raise HuaweiSwitchError("无法进入特权模式")
        else:
            # 无super密码情况
            if 'privilege is 3' in text:
                return
            # 需要super密码，输入密码
            elif 'assword' in text:
                self.write(self.super_password + "\n")
        idx, match, text = self.expect([">", 'assword:'], 1)
        # 打印所有匹配到的对象
        print match.group()
        if match is None:
            raise HuaweiSwitchError("尝试super模式时，无法获得反馈", text=None)
        elif match.group().count('assword') > 0:
            self.write("\n\n\n")
            raise HuaweiSwitchError("password错误")
        elif 'privilege is 3' in text:
            return

    def get_portlists(self):
        # 获取端口列表
        portlists = []
        result = self.cmd('display interface brief')
        print result
        pattern = re.compile(r'(.*)ethernet(.*)|(.*)trunk(\d+)|loopback(\d+)', re.I)
        for a in result.split():
            b = pattern.match(a)
            if b is not None:
                c = b.group()
                portlists.append(c)
        return portlists

    def get_port_info(self, port_lists):
        # 获取端口配置信息
        port_info_lists = []
        for b in port_lists:
            info = self.cmd('display current-configuration interface ' + b + ' | exclude ' + 'interface')
            infe = info.replace('\n', '')
            print infe
            pattern = re.compile(r'#.*#', re.I)
            result = pattern.findall(infe)
            print result
            port_info_lists.append({
                "portlist": b,
                "info": result
            })

        return port_info_lists

    def get_port_status(self, port_info_lists):
        port_status_lists = []

        for a in port_info_lists:
            info = str(a.get('info'))
            portlist = a.get('portlist')
            # 关闭
            if info.count('shutdown') > 0:
                port_status_lists.append({
                    "portlist": portlist,
                    "status": 0
                })
            # trunk口
            elif info.count('trunk') > 0:
                port_status_lists.append({
                    "portlist": portlist,
                    "status": 1
                })
            # 准入口
            elif info.count('dot1x') > 6:
                port_status_lists.append({
                    "portlist": portlist,
                    "status": 2
                })
            # 例外口
            elif info.count('mac-address') > 0:
                port_status_lists.append({
                    "portlist": portlist,
                    "status": 3
                })
            # 问题口
            else:
                port_status_lists.append({
                    "portlist": portlist,
                    "status": 4
                })

        return port_status_lists



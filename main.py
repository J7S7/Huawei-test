from HuaweiSwitch.HuaweiSwitch import *


test = HuaweiSwitch()
test.host = '10.242.207.11'
test.username = 'localadmin'
test.password = 'wlkjhj2018'
test.super_password = 'huaweijhj2018'
test.connect()
portlists = test.get_portlists()
print portlists
portinfo = test.get_port_info(portlists)
print portinfo
portstat = test.get_port_status(portinfo)
print portstat
portmaclists = test.get_port_mac(portstat)
print portmaclists





from HuaweiSwitch.HuaweiSwitch import *


test = HuaweiSwitch()
test.host = '10.242.207.11'
test.username = 'localadmin'
test.password = 'wlkjhj2018'
test.connect()
portlists = test.get_portlists()
print portlists



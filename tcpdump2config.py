# capture config data send by another tool
# try something like:
#
# $ sudo tcpdump -n -s 650 -l | grep .1.3.6.1.4.1.762.2.3.1.1. | grep SetRequest | python tcpdump2config.py > config.dat
#
# --drt@un.bewaff.net - http://c0re.jp/

import sys

for x in sys.stdin.xreadlines():
    if x[-1] == '\n':
        x = x[:-1]
    pos = x.rfind('=')
    if pos != -1:
        x = x[pos+1:]
    bytes = x.split('_')
    bytes = map(lambda b: chr(int(b, 16)), bytes)
    sys.stdout.write(''.join(bytes))

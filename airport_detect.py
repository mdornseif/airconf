""" $Id: airport_detect.py,v 1.1 2002/01/22 01:07:00 drt Exp $

Find all Apple Airport APs on a subnet.

This is done by sending a UDP packet containing ('\001' + ('\000' *
115)) to the local subnet broadcast address and listening for
replies. If no reply is recived for more than 2 seconds this module
stops listening.

You might be able to find more Information at http://c0re.jp/

--drt@un.bewaff.net

"""

import socket
import struct
import select

# this has to be the Broadcast address or the address of a known airport 
broadcast = '172.17.0.255'

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
s.sendto('\001' + ('\000' * 115), (broadcast, 192))

while 1:
    (iwtd, owtd, ewtd) = select.select([s], [], [], 2)
    if len(iwtd) == 0:
        break
    (data, addr) = s.recvfrom(128)

    # parse reply
    ip = addr[0]
    if len(data) != 116:
        print "%s, weird len %d (%r)\n" % (ip, len(data), data)

    ap_name = []
    for c in data[0x30:]:
        if c == '\0':
            break
        ap_name.append(c)
    ap_name = ''.join(ap_name)
    
    vendor = []
    for c in data[0x54:]:
        if c == '\0':
            break
        vendor.append(c)
    vendor = ''.join(vendor)

    mac = []
    for c in data[0x24:0x2a]:
        mac.append(hex(ord(c))[2:])
    mac = ':'.join(mac)

    print repr(ap_name), repr(vendor), repr(mac)

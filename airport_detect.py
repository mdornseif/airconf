""" $Id: airport_detect.py,v 1.4 2002/01/24 21:27:16 drt Exp $

Find all Apple Airport APs on a subnet.

This is done by sending a UDP packet containing ('\001' + ('\000' *
115)) to the local subnet broadcast address and listening for
replies. If no reply is recived for more than 2 seconds this module
stops listening.

Based on osubcast.c by Bill Fenner <fenner@research.att.com>.

Rop writes:

Discovery of Base Stations

Discovery is done by the configuration program by sending a broadcast
UDP packet to port 192. The packet should contains 0x01, followed by
115 times 0x00, making a total of decimal 116 bytes (hex 74)

The Base Stations then respond with a UDP packet from port 192, back
to the originating IP-number and port. This packet is built as
follows:

 
offset(hex)     length          meaning 
00              1               always 01 
01              1               always 01 
03              1               00 means normal mode,  
                                01 means virgin 
24              6               MAC-address of Base 
2C              4               IP-number of Base 
30              ?               Name of Base,  
                                zero padded at right 
50              4               1/100th of seconds since  
                                boot 
54              ?               Version and serial no. of 
                                Base Station, zero  
                                terminated, maximum 20 hex 
                                bytes. 

The name of a virgin base station is always XX-XX-XX-XX-XX-XX, where
the Xs are replaced with the MAC-address of the Base.


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

    print addr[1], repr(ap_name), repr(vendor), repr(mac)

# $Id: airport.py,v 1.3 2002/02/02 17:27:23 drt Exp $

"""Handling of Communication with Apple Airport Base Station 1 (Graphite).

  --drt@un.bewaff.net - http://c0re.jp/c0de/airconf/
"""

import sys, socket, select
import pprint
from pysnmp import session

# OIDs used by the Base
karl = '.1.3.6.1.4.1.762'
conf = karl + ".2.3.1.1"

# various helper functions to mangle data
def ip4(s):
    '''Convert bitstring to an dotted-quard IP address.'''
    return '.'.join(map(str, map(ord, s)))

def string0(s):
    '''Convert 0-padded fixed length string to a python string.'''
    if len(s) == 0:
        return ''
    if s[-1] == '\x00':
        return string0(s[:-1])
    return s
    
def short(s):
    '''Convert char to a unsigned short value.'''
    return ord(s)

def litteendianint(s):
    '''Convert little-endian notation bitstring to an integer.'''
    return ord(s[0]) + (ord(s[1]) << 8)

def mac(s):
    '''Convert bitstring to ethernet MAC address.'''
    l = map(lambda x: hex(ord(x))[2:], list(s))
    return ':'.join(l)

def raw(s):
    '''Return data unaltered'''
    return s


# various helper functions

def macstrtobin(s):
    '''Convert a MAC in "XX:XX:XX:XX:XX:XX" format to binary representation.'''
    try:
        bytes = s.split(':')
        if len(bytes) != 6:
            raise
        bytes = map(lambda x: chr(int(x, 16)), bytes)
    except:
        raise ValueError, 'A MAC address must consist of exactly 6 Hex Numbers (48 bits), like "FF:FF:FF:FF:FF:FF", 2%r" does not qualify' % (s)
    return ''.join(bytes)


'''http://edge.mcs.drexel.edu/GICL/people/sevy/airport/source/info.zip

Airport Base Station Information Organization

Have 68 relevant object identifiers, which each transmits/receives a
256 byte octet string, with the resulting 68 256 byte blocks
comprising a 17k memory block. Pertinent data is located at various
positions and orientations within this block (sometimes crossing the
sub-block boundaries). The 256-byte sub-blocks are best viewed as
16-row blocks of 16 bytes; the data locations are communicated
relative to this organization. Thus a data item listed under
identifier .1.3.6.1.4.1.762.2.3.1.1.A at position B*16 + C begins at
absolute byte index (A-1)*256 + B*16 + C (using the C/Java-standard
initial index of 0).

'''


# definition of the raw configuration memory block
# this is {name: (position, length, possible values, formatting, description, user editable)}
EDITABLE = 1
NOTEDITABLE = 0

image = {'copyright': (6, 68, {}, string0, "", NOTEDITABLE),
         'public': (7 * 16 + 6, 6, {}, string0, "", NOTEDITABLE),
         'set password (?)': (9 * 16 + 6, 9, {}, string0, "", NOTEDITABLE),
         'Ethernet DHCP switch': (256 +  1 * 16 + 7, 1,
                                  {0x00: "don't provide addresses on Ethernet",
                                   0x40: "provide addresses on Ethernet / configure base station manually",
                                   0x60: "configure base station using DHCP"}, short, """TODO""", EDITABLE),
         'Ethernet/Modem switch 1': (256 + 10, 1,
                                     {0x62: 'modem',
                                      0x60: 'ethernet'}, short, """TODO""", EDITABLE),
         'Ethernet/Modem switch 2': (256 * 5 + 6 * 16, 1,
                                     {0x03: 'modem',
                                      0x00: 'Ethernet'}, short, """TODO""", EDITABLE),
         'Wireless channel': (256 + 7*16 + 8, 1, {}, short,
                              """Frequency at which the base station should operate.
                              Something between 1 and 13 depending on your region.
                              1-13 is OK in the EU.""", EDITABLE),
         'Network name 1': (256 + 12 * 16 + 8, 2, {}, string0, "", NOTEDITABLE),
         'Network name 2': (256 + 13 * 16 + 8, 2, {}, string0, "", NOTEDITABLE),
         'Network name 3': (256 + 14 * 16 + 8, 2, {}, string0, "", NOTEDITABLE),
         'Network name 4': (256 + 15 * 16 + 8, 2, {}, string0, "", NOTEDITABLE),
         'Network name 5': (256 + 16 * 16 + 8, 2, {}, string0, "", NOTEDITABLE),
         'Network name 6': (256 + 17 * 16 + 8, 2, {}, string0, "", NOTEDITABLE),
         'Network name 7': (256 + 18 * 16 + 8, 2, {}, string0, "", NOTEDITABLE),
         'Network name 8': (256 + 19 * 16 + 8, 2, {}, string0, "", NOTEDITABLE),
         'Network name 9': (256 + 20 * 16 + 8, 2, {}, string0, "", NOTEDITABLE),
         'Network name 10': (256 + 21 * 16 + 8, 2, {}, string0, "", NOTEDITABLE),
         'Network name 11': (256 + 22 * 16 + 8, 2, {}, string0, "", NOTEDITABLE),
         'Network name 12': (256 + 23 * 16 + 8, 2, {}, string0, "", NOTEDITABLE),
         'Network name 13': (256 + 24 * 16 + 8, 2, {}, string0, "", NOTEDITABLE),
         'Network name 14': (256 + 25 * 16 + 8, 2, {}, string0, "", NOTEDITABLE),
         'Network name 15': (256 + 26 * 16 + 8, 2, {}, string0, "", NOTEDITABLE),
         'Network name 16': (256 + 27 * 16 + 8, 2, {}, string0, "", NOTEDITABLE),
         'DHCP/NAT switch': (4 * 256 + 4 * 16 + 9, 1, 
                             {0x00: 'none (act as transparent bridge)',
                              0x80: 'DHCP on, using specified range of IP addresses', 
                              0x82: 'DHCP plus NAT on, using default range of IP addresses', 
                              0x84: 'DHCP only, plus port mapping (firewall functionality?)',
                              0x86: 'DHCP and NAT, with port-mapping'}, short, """TODO""", EDITABLE),
         'Base station IP address': (4 * 256 + 6 * 16 + 10, 4, {}, ip4, """TODO""", EDITABLE),
         'Base station partial mask': (4 * 256 + 6 * 16 + 14, 2, {}, raw, """TODO""", NOTEDITABLE),
         'Router IP address': (4 * 256 + 7 * 16, 4, {}, ip4,  """TODO""", EDITABLE),
         'Router Netmask': (4 * 256 + 7 * 16 + 4, 4, {}, ip4, """TODO""", EDITABLE),
         'Contact person name': (4 * 256 + 8 * 16 + 12, 64, {}, string0,  """TODO""", EDITABLE),
         'Base station name':  (4 * 256 + 12 * 16 + 12, 64, {}, string0, """TODO""", EDITABLE),
         'Location string': (5 * 256 + 12, 64, {}, string0, """""", EDITABLE),
         'DHCP address range start': (12 * 256 + 15*16 + 2, 4, {}, ip4,  
                             """First address which should be given out by DHCP if DHCP is enabled.
                             See also 'DHCP/NAT switch'.""", EDITABLE),
         'DHCP address range end': (12 * 256 + 15*16 + 6, 4, {}, ip4, 
                                    """Last address which should be given out by DHCP.""", EDITABLE),
         'Primary DNS 1': (12 * 256 + 15*16 + 10, 2, {}, raw,  """""", NOTEDITABLE),
         'Secondary DNS 1': (12 * 256 + 15*16 + 12, 2, {}, raw, """""", NOTEDITABLE),
         'Primary DNS 2': (12 * 256 + 16*16, 2, {}, raw, """""", NOTEDITABLE),
         'Secondary DNS 2': (12 * 256 + 15*16 + 2, 2, {}, raw, """""", NOTEDITABLE),
         'Domain name': (13 * 256 + 10, 32, {}, string0, 
                         """Your local domain name. Use 'yourname.invalid' if you don't have one.""", EDITABLE),
         'Wireless LAN IP address when NAT enabled': (13 * 256 + 2*16 + 10, 4, {}, ip4, """""", EDITABLE),
         'IP address when connected through Ethernet': (13 * 256 +4*16 + 10, 4, {}, ip4, """""", EDITABLE),
         'Mac addresses access control count': (15 * 256 + 8*16 + 8, 2, {}, litteendianint,
                                                """The nummer of Addresses in the ACL.""", NOTEDITABLE), 
         'Mac addresses access control addresses': (15 * 256 + 8*16 + 10, 497 * 6, {}, raw,
                                                    """MAC Addresses in the ACL.""", NOTEDITABLE),
         'Host names for access control': (0x1cc8, 497 * 20, {}, raw, 
                                           """Hostnames in the ACL.""", NOTEDITABLE),
         'Checksum 1':  (256 * 67 + 11*16 + 6, 2, {}, raw,  "", EDITABLE),
         'Checksum 2':  (256 * 67 + 11*16 + 8, 2, {}, raw, "", EDITABLE)
}

# table to fix entries scattered arround in the configuration block
fixups = {'Network Name': (['Network name 1', 'Network name 2',
                           'Network name 3', 'Network name 4',
                           'Network name 5', 'Network name 6',
                           'Network name 7', 'Network name 8',
                           'Network name 9', 'Network name 10',
                           'Network name 11', 'Network name 12',
                           'Network name 13', 'Network name 14',
                           'Network name 15', 'Network name 16'], raw,
                           """Name of your wireless Network.""", EDITABLE),
          'Primary DNS': (['Primary DNS 1', 'Primary DNS 2'], ip4,
                          """Your Primary DNS server.""", EDITABLE),
          'Secondary DNS': (['Secondary DNS 1', 'Secondary DNS 2'], ip4,
                            """Your Secondary DNS Server (optional).""", EDITABLE)}


# when first importing this module be bouild a dictionary out of the various descriptions

documentation = {'Access Control': ('TODO', EDITABLE)}
for k in image.keys():
    (pos, length, desc, func, doc, show) = image[k]
    documentation[k] = (doc, show)
for k in fixups.keys():
    (fixuplist, func, doc, show) = fixups[k]
    documentation[k] = (doc, show)

# This should be incoperated above but I myself don't really need it:
'''
.1.3.6.1.4.1.762.2.3.1.1.63Username@domain, password
byte 10*16 + 10: character count of dial-up username, username, character count of dial-up password, password.
Encryption flag fields: 
byte 5*16 + 8
00 = no encryption
08 = use encryption
byte 6*16 + 8
12 = no encryption
92 = use encryption
Modem timeout, in 10-second chunks: byte 7*16 + 10
Dialing type: byte 7*16 + 11
0D = tone
04 = pulse
Modem init string length: byte 8*16 + 9
Phone number lengths:
primary: byte 8*16 + 10;  secondary: byte 8*16 + 11
Phone country code: byte 11*16 + 10,11: 
US standard = 32 32
Singapore = 34 37
Switzerland = 31 35
Modem initialization string and phone numbers: byte 12*16 + 10,
continuation in columns 10 and 11 of subsequent rows
phone numbers use BCD, with D for space/paren and E for dash
primary number immediately follows modem init string; secondary number immediately follows primary number
.1.3.6.1.4.1.762.2.3.1.1.3Extension of 2, plus:
Encryption flag field: byte 12*16 + 8
00 = no encryption
01 = use encryption
.1.3.6.1.4.1.762.2.3.1.1.4Encryption: 
number of bytes: byte 7*16 + 4
00 for no encryption
05 for 40-bit encryption
key: byte 7*16 + 6
Port mapping functions: 
count of port mappings: byte 6*16 + 2
public port numbers: byte 12*16 + 2, in 2-byte pairs (?)
first two octets of private IP addresses: byte 14*16 + 10,
 in 2-byte pairs (?)
.1.3.6.1.4.1.762.2.3.1.1.15Port mapping functions: 
last two octets of private IP addresses: byte 1*16 + 2,
 in 2-byte pairs (?)
private port numbers: byte 3*16 + 10, in 2-byte pairs (?)
.1.3.6.1.4.1.762.2.3.1.1.16Login info to transmit, if selected (username, password, perhaps "ppp"), plus weird separators: byte 8
'''

def readconf(host, community):
    '''Read  configuration data from Airport.

    Rop writes:
    Reading from flash
    
    Reading is done by issuing SNMP get-requests for
    1.3.6.1.4.1.762.2.2.1.1.n. This request will then return a string
    containing a 256 byte block having offset (n - 1) * 256. Example:
    to read the configuration block, one would issue SNMP get-requests
    for 1.3.6.1.4.1.762.2.2.1.1.1 through 1.3.6.1.4.1.762.2.2.1.1.68.
    '''

    s = session.session (host, community)
    data = ''

    # We could be faster if we dont wait for each response before
    # sending the next one. The apple tool does so.
    for i in range(1, 69):
        encoded_objid = s.encode_oid ([1, 3, 6, 1, 4, 1, 762, 2, 2, 1, 1, i])
        question = s.encode_request('GETREQUEST', [encoded_objid], [])
        answer = s.send_and_receive(question)
        (encoded_objids, encoded_values) = s.decode_response(answer)
        values = map (s.decode_value, encoded_values)
        data += values[0]

    s.close()
    del(s)
    return data



def calcchecksum(data):
    '''Calculate the checksum for a given data block
    and return a copy of the block with the checksum insered.'''
    
    datal = list(data)
    # delete data "after the end" and calculate checksum
    datal[0x43ba:] = ['\0'] * 70 
    checksum1 = 0
    for x in data[:0x43b6]:
        checksum1 += ord(x)
    checksum2 = checksum1 + ((checksum1 >> 8) & 0xff) + (checksum1 & 0xff)
    # uh, checksum 1 seems to be useless ... strange
    # other people have different opinoions about the right way to
    # calculate this - this way works for me.
    #datal[0x43b6] = chr(checksum1 & 0xff)
    #datal[0x43b7] = chr((checksum1 >> 8) & 0xff)
    checksum2 = 0
    for x in datal[:0x43b8]:
        checksum2 += ord(x)
    datal[0x43b8] = chr(checksum2 & 0xff)
    datal[0x43b9] = chr((checksum2 >> 8) & 0xff)
    return ''.join(datal)


def updateacl(data, acl):
    '''Update the ACL in a configuration block.'''

    countpos = image['Mac addresses access control count'][0]
    macpos = image['Mac addresses access control addresses'][0]
    maclen = image['Mac addresses access control addresses'][1]
    hostpos = image['Host names for access control'][0]
    hostlen = image['Host names for access control'][1]
    datal = list(data)
    newcount = len(acl)
    if newcount > maclen:
        raise ValueError, "ACLs can't be longer than %d entries." % (maclen)
    newmac = []
    newname = []
    for (mac, name) in acl:
        newmac.extend(macstrtobin(mac))
        if len(name) > 19:
            raise ValueError, "Names for ACL entries must be no longer than 19 characters."
        name = list(name)
        name.extend(['\0'] * 20)
        newname.extend(name[:20])
    # zero out data areas in configuration area
    datal[macpos:macpos+maclen] = ['\0'] * maclen
    datal[hostpos:hostpos+hostlen] = ['\0'] * hostlen
    # write our new data into configuration block
    datal[macpos:macpos+(newcount*6)] = newmac
    datal[hostpos:hostpos+(newcount*20)] = newname
    datal[countpos] = chr(newcount & 0xff)
    datal[countpos+1] = chr((newcount >> 8) & 0xff)
    return ''.join(datal)

def parseconf(data):
    '''Parse the configuration block into a python dictionary.'''
    
    airport = {}
    for k in image.keys():
        (pos, length, desc, func, doc, show) = image[k]
        airport[k] = apply(func, [data[pos:pos + length]])

    # fix scattered values
    for k in fixups.keys():
        val = ''
        (fixuplist, func, doc, show) = fixups[k]
        for x in fixuplist:
            val += airport[x]
            del(airport[x])
        airport[k] = apply(func, [val])

    # mangle access control lists into something more readable
    count = airport['Mac addresses access control count']
    macs = airport['Mac addresses access control addresses'][:6*count]
    names = airport['Host names for access control'][:20*count]
    del(airport['Mac addresses access control addresses']) 
    del(airport['Host names for access control'])
    airport['Access Control'] = []
    for i in range(count):
        airport['Access Control'].append((mac(macs[6*i:(6*i)+6]), string0(names[20*i:(20*i)+20])))
    return airport


def printconf(airport):
    '''Return the configuration in a human and machine readable format.'''
    
    l = airport.keys()
    l.sort()
    pp = pprint.PrettyPrinter()
    out = []
    for k in l:
        out.append("%s: %s" % (k, pp.pformat(airport[k])))
    return "config = {%s}" % ',\n'.join(out)

def writeconf(host, community, data):
    '''Write configuration Data to an Airport.

    Rop writes:

    Writing to flash

    Writing to flash is done by writing to
    1.3.6.1.4.1.762.2.3.1.1.n, writing the 256 bytes starting at
    position (n - 1) * 256. The write is not actually done until the
    entire block to be written is received, and the length of the
    block is written as an integer to 1.3.6.1.4.1.762.2.1.2.0 and
    1.3.6.1.4.1.762.2.1.3.0. The unit then checks a checksum in the
    data, encoded as two bytes directly after the last byte. This
    checksum is the lowest 16 bits of the sum of all the bytes to be
    written, LSB first. If the checksum matches, the appropriate part
    of the flash is overwritten with the new data, and the unit
    reboots.

    Both flash-reads and writes need to be done with the read/write
    community. An attempt to read them with 'public' fails on a 'no
    such name' error.
    '''

    s = session.session (host, community)
    for i in range(0, 68):
        encoded_objid = s.encode_oid ([1, 3, 6, 1, 4, 1, 762, 2, 3, 1, 1, i+1])
        encoded_value = s.encode_string(data[i*256:(i+1)*256])
        question = s.encode_request('SETREQUEST', [encoded_objid], [encoded_value])
        answer = s.send_and_receive (question)
        # we don't need this - do we?
        (encoded_objids, encoded_values) = s.decode_response (answer)
        objids = map (s.decode_value, encoded_objids)
        values = map (s.decode_value, encoded_values)

    # "writing to flash"
    encoded_objid = s.encode_oid ([1,3,6,1,4,1,762,2,1,2,0])
    encoded_value = s.encode_integer(17336)
    question = s.encode_request('SETREQUEST', [encoded_objid], [encoded_value])
    answer = s.send_and_receive (question)

    # unneeded
    (encoded_objids, encoded_values) = s.decode_response (answer)
    objids = map (s.decode_value, encoded_objids)
    values = map (s.decode_value, encoded_values)

    encoded_objid = s.encode_oid ([1,3,6,1,4,1,762,2,1,3,0])
    encoded_value = s.encode_integer(17336)
    question = s.encode_request('SETREQUEST', [encoded_objid], [encoded_value])
    answer = s.send_and_receive (question)

    # unneeded
    (encoded_objids, encoded_values) = s.decode_response (answer)
    objids = map (s.decode_value, encoded_objids)
    values = map (s.decode_value, encoded_values)
    

def scanforbases(broadcast):
    """Takes a broadcast addresses and returns a list of Base Stations in this Network.

    We return a list of tuples consisting of (IP Address, Access Point
    Name, Vendor Name, MAC Address).

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

   """
  
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    s.sendto('\001' + ('\000' * 115), (broadcast, 192))

    ret = []
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
    
        ret.append((addr[0], ap_name, vendor, mac))
    
    return ret

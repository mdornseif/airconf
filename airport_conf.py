from pysnmp import session

karl = '.1.3.6.1.4.1.762'
conf = karl + ".2.3.1.1"


def ip4(s):
    return '.'.join(map(str, map(ord, s)))


def string0(s):
    if len(s) == 0:
        return ''
    if s[-1] == '\x00':
        return string0(s[:-1])
    return s

    
def short(s):
    return ord(s)


def raw(s):
    return s


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

    
image = {'copyright': (6, 68, {}, string0),
         'public': (7 * 16 + 6, 6, {}, string0),
         'set password (?)': (9 * 16 + 6, 9, {}, string0),
         'Ethernet DHCP switch': (256 +  1 * 16 + 7, 1,
                                  {0x00: "don't provide addresses on Ethernet",
                                   0x40: "provide addresses on Ethernet / configure base station manually",
                                   0x60: "configure base station using DHCP"}, short),
         'Ethernet/Modem switch 1': (256 + 10, 1,
                                     {0x62: 'modem',
                                      0x60: 'ethernet'}, short),
         'Ethernet/Modem switch 2': (256 * 5 + 6 * 16, 1,
                                     {0x03: 'modem',
                                      0x00: 'Ethernet'}, short),
         'Wireless channel': (256 + 7*16 + 8, 1, {}, short),
         'Network name 1': (256 + 12 * 16 + 8, 2, {}, string0),
         'Network name 2': (256 + 13 * 16 + 8, 2, {}, string0),
         'Network name 3': (256 + 14 * 16 + 8, 2, {}, string0),
         'Network name 4': (256 + 15 * 16 + 8, 2, {}, string0),
         'Network name 5': (256 + 16 * 16 + 8, 2, {}, string0),
         'Network name 6': (256 + 17 * 16 + 8, 2, {}, string0),
         'Network name 7': (256 + 18 * 16 + 8, 2, {}, string0),
         'Network name 8': (256 + 19 * 16 + 8, 2, {}, string0),
         'Network name 9': (256 + 20 * 16 + 8, 2, {}, string0),
         'Network name 10': (256 + 21 * 16 + 8, 2, {}, string0),
         'Network name 11': (256 + 22 * 16 + 8, 2, {}, string0),
         'Network name 12': (256 + 23 * 16 + 8, 2, {}, string0),
         'Network name 13': (256 + 24 * 16 + 8, 2, {}, string0),
         'Network name 14': (256 + 25 * 16 + 8, 2, {}, string0),
         'Network name 15': (256 + 26 * 16 + 8, 2, {}, string0),
         'Network name 16': (256 + 27 * 16 + 8, 2, {}, string0),
         'DHCP/NAT switch': (4 * 256 + 4 * 16 + 9, 1, 
                             {0x00: 'none (act as transparent bridge)',
                              0x80: 'DHCP on, using specified range of IP addresses', 
                              0x82: 'DHCP plus NAT on, using default range of IP addresses', 
                              0x84: 'DHCP only, plus port mapping (firewall functionality?)',
                              0x86: 'DHCP and NAT, with port-mapping'}, short),
         'Base station IP address': (4 * 256 + 6 * 16 + 10, 4, {}, ip4),
         'Base station partial mask': (4 * 256 + 6 * 16 + 14, 2, {}, repr),
         'Router IP address': (4 * 256 + 7 * 16, 4, {}, ip4),
         'Router Netmask': (4 * 256 + 7 * 16 + 4, 4, {}, ip4),
         'Contact person name': (4 * 256 + 8 * 16 + 12, 64, {}, string0),
         'Base station name':  (4 * 256 + 12 * 16 + 12, 64, {}, string0),
         'Location string': (5 * 256 + 12, 64, {}, string0),
         'DHCP address range start': (12 * 256 + 15*16 + 2, 4, {}, ip4),
         'DHCP address range end': (12 * 256 + 15*16 + 6, 4, {}, ip4),
         'Primary DNS 1': (12 * 256 + 15*16 + 10, 2, {}, raw),
         'Secondary DNS 1': (12 * 256 + 15*16 + 12, 2, {}, raw),
         'Primary DNS 2': (12 * 256 + 16*16, 2, {}, raw),
         'Secondary DNS 2': (12 * 256 + 15*16 + 2, 2, {}, raw),
         'Domain name (from DNS setting window)': (13 * 256 + 10, 32, {}, string0),
         'Wireless LAN IP address when NAT enabled': (13 * 256 + 2*16 + 10, 4, {}, ip4),
         'IP address when connected through Ethernet': (13 * 256 +4*16 + 10, 4, {}, ip4),
         'Mac addresses access control count': (15 * 256 + 8*16 + 7, 3, {}, repr), 
         'Mac addresses access control addresses': (15 * 256 + 8*16 + 10, 497 * 6, {}, repr),
         'Host names for access control': (28 * 256 + 12*16 + 8, 497 * 20, {}, repr),
         'Checksum 1':  (256 * 67 + 11*16 + 6, 2, {}, repr),
         'Checksum 2':  (256 * 67 + 11*16 + 8, 2, {}, repr)
}

# table to fix entries scattered arroubd
fixups = {'Network Name': (['Network name 1', 'Network name 2',
                           'Network name 3', 'Network name 4',
                           'Network name 5', 'Network name 6',
                           'Network name 7', 'Network name 8',
                           'Network name 9', 'Network name 10',
                           'Network name 11', 'Network name 12',
                           'Network name 13', 'Network name 14',
                           'Network name 15', 'Network name 16'], raw),
          'Primary DNS': (['Primary DNS 1', 'Primary DNS 2'], ip4),
          'Secondary DNS': (['Secondary DNS 1', 'Secondary DNS 2'], ip4)}


'''
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



.1.3.6.1.4.1.762.2.3.1.1.63Username@domain, password
byte 10*16 + 10: character count of dial-up username, username, character count of dial-up password, password.

.1.3.6.1.4.1.762.2.3.1.1.68Checksum 1: bytes 11*16 + 6,7: sum of all previous bytes (treated as unsigned shorts), with result bytes reversed (i.e., little-endian)
Checksum 2: bytes 11*16 + 8,9:  sum of all previous bytes, including preceding checksum, with result bytes reversed (i.e., little-endian) - special thanks to Bill Fenner for figuring this one out!

'''

s = session.session ('172.17.0.8', 'public')
encoded_objid = s.encode_oid ([1, 3, 6, 1, 2, 1, 1, 1, 0])
print encoded_objid 
question = s.encode_request ('GETREQUEST', [encoded_objid], [])
answer = s.send_and_receive (question)
(encoded_objids, encoded_values) = s.decode_response (answer)
objids = map (s.decode_value, encoded_objids)
print objids

values = map (s.decode_value, encoded_values)
print values

s = session.session ('172.17.0.8', '2407')
data = ''
for i in range(1, 69):
    encoded_objid = s.encode_oid ([1, 3, 6, 1, 4, 1, 762, 2, 2, 1, 1, i])
    question = s.encode_request ('GETREQUEST', [encoded_objid], [])
    answer = s.send_and_receive (question)
    (encoded_objids, encoded_values) = s.decode_response (answer)
    objids = map (s.decode_value, encoded_objids)
    values = map (s.decode_value, encoded_values)
    data += values[0]


datal = list(data)
# 'Mac addresses access control count'
datal[15 * 256 + 8*16 + 7] = chr(128)
# Mac addresses access control addresses'
datal[15*256+8*16+10:15*256+8*16+10+(128*6)] = ['A'] * (128*6)
# 'Host names for access control'
datal[28*256+12*16+8:28*256+12*16+8+(128*20)] = ['A'] * (128*20)
data = ''.join(datal)

checksum1 = 0
for x in data[:0x43b6]:
    checksum1 += ord(x)
checksum2 = checksum1 + ((checksum1 >> 8) & 0xff) + (checksum1 & 0xff)
#data[0x43b6] = checksum1 & 0xff
#data[0x43b7] = (checksum1 >> 8) & 0xff
#data[0x43b8] = checksum2 & 0xff;
#data[0x43b9] = (checksum2 >> 8) & 0xff;
    
# read items out of data
airport = {}
for k in image.keys():
    (pos, length, desc, func) = image[k]
    airport[k] = apply(func, [data[pos:pos + length]])


for l in fixups.keys():
    val = ''
    (fixuplist, func) = fixups[l]
    for x in fixuplist:
        val += airport[x]
        del(airport[x])
    airport[l] = apply(func, [val])

for k in airport.keys():
    print "%s: %s" % (k, airport[k])

   def run (self, objids, values):
        """Pass SNMP agent for one or more Object ID's. The objid
           argument should be a list of strings where each string
           represents a Object ID in dotted numbers notation (e.g.
           ['.1.3.6.1.4.1.307.3.2.1.1.1.4.1']).
        """   
        # Convert string type Object ID's into numeric representation
        numeric_objids = map (self.str2nums, objids)

        # BER encode SNMP Object ID's to query
        encoded_objids = map (self.encode_oid, numeric_objids)

        # BER encode the values of MIB variables (assuming they are strings!)
        encoded_values = map (self.encode_string, values)

        # Build a complete SNMP message of type 'SETREQUEST', pass it lists
        # of BER encoded Object ID's and MIB variables' values associated
        # with these Object ID's to set at SNMP agent.
        question = self.encode_request ('SETREQUEST', encoded_objids, encoded_values)

        # Try to send SNMP message to SNMP agent and receive a response.
        answer = self.send_and_receive (question)

        # As we get a response from SNMP agent, try to disassemble SNMP reply
        # and extract two lists of BER encoded SNMP Object ID's and 
        # associated values).
        (encoded_objids, encoded_values) = self.decode_response (answer)

        # Decode BER encoded Object ID.
        objids = map (self.decode_value, encoded_objids)

        # Decode BER encoded values associated with Object ID's.
        values = map (self.decode_value, encoded_values)

        # Return a tuple of two lists holding Object ID's and associated
        # values extracted from SNMP agent reply.
        return (objids, values)


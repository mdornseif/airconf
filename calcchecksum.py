# $Id: calcchecksum.py,v 1.2 2002/01/26 16:15:03 drt Exp $

'''Read Configuration Block from stdin, calculate checksum and write it to stdout.

  --drt@un.bewaff.net - http://c0re.jp/c0de/airconf
'''

import sys
import airport

data = sys.stdin.read() 
sys.stdout.write(airport.calcchecksum(data))

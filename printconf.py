# $Id: printconf.py,v 1.2 2002/01/26 16:15:27 drt Exp $

'''Read Configuration Block from stdin and output it in a human readable Way to stdout.

  --drt@un.bewaff.net - http://c0re.jp/c0de/airconf
'''

import sys
import airport

data = sys.stdin.read()
print airport.printconf(airport.parseconf(data)) 

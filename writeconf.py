# $Id: writeconf.py,v 1.2 2002/01/26 16:16:53 drt Exp $

'''Read Configuration Block from stdin and write it to an Airport Basestation.

  --drt@un.bewaff.net - http://c0re.jp/c0de/airconf
'''

import sys
import airport

if len(sys.argv) != 3:
    print >>sys.stderr, "usage: %s <agent> <community>\ne.g.: %s 172.17.0.1 public" % (sys.argv[0],sys.argv[0])
    sys.exit(1)
    
data = sys.stdin.read() 
print len(data)
airport.writeconf(sys.argv[1], sys.argv[2], data)

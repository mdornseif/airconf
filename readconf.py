# $Id: readconf.py,v 1.2 2002/01/26 16:16:02 drt Exp $

'''Read Configuration from an Airport Basestation and write it to stdout.

  --drt@un.bewaff.net - http://c0re.jp/c0de/airconf
'''

import sys
import airport

if len(sys.argv) != 3:
    print >>sys.stderr, "usage: %s <agent> <community>\ne.g.: %s 172.17.0.1 public" % (sys.argv[0],sys.argv[0])
    sys.exit(1)
    
sys.stdout.write(airport.readconf('172.17.0.8', '2407')) 

# $Id: airport_detect.py,v 1.5 2002/01/25 21:31:59 drt Exp $

"""You might be able to find more Information at http://c0re.jp/

--drt@un.bewaff.net - http://c0re.jp/

"""

import sys
import pprint
import airport

if len(sys.argv) != 2:
    print >>sys.stderr, "usage: %s <agent>\ne.g.: %s 172.17.0.1" % (sys.argv[0],sys.argv[0])
    sys.exit(1)

bases = airport.scanforbases(sys.argv[1])
for (ip, name, vendor, mac) in bases:
    print "%s|%s|%s|%s" % (ip, name, vendor, mac)

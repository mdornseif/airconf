# $Id: printconf.py,v 1.3 2002/02/02 17:27:23 drt Exp $

'''Read Configuration Block from stdin and output it in a human readable Way to stdout.

  --drt@un.bewaff.net - http://c0re.jp/c0de/airconf
'''

import sys
import airport

data = sys.stdin.read()
conf = airport.parseconf(data)

keys = conf.keys()
keys.sort()
for k in keys:
    if airport.documentation[k][1] == airport.EDITABLE:
        doc = airport.documentation[k][0]
        if len(doc) > 0:
            doc = '\n'.join(['# ' + x.strip() for x in doc.split('\n')])
            print doc
        print "%s: %r" % (k, conf[k])


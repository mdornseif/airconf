import sys
import airport

data = sys.stdin.read()
print airport.printconf(airport.parseconf(data)) 

import sys
import airport

data = sys.stdin.read() 
print len(data)
airport.writeconf('172.17.0.8', '2407', data)

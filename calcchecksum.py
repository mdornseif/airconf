import sys
import airport

data = sys.stdin.read() 
sys.stdout.write(airport.calcchecksum(data))

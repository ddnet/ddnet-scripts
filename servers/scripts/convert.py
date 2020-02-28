#!/usr/bin/env python2
import sys
s = 'broadcast "'
for line in sys.stdin:
  s += line.replace(' ','  ').rstrip('\n') + '\\n'
s = s[:-2]
s += '"'
print(s)

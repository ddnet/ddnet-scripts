#!/usr/bin/env python3
import sys
s = 'broadcast "'
for line in sys.stdin:
  s += line.replace(' ','  ').rstrip('\n') + '\\n'
s = s[:-2]
s += '"'
print(s)

#!/usr/bin/env python
import sys
ourServer = False
with open('all') as f:
  for line in f:
    if 'server id 10' in line:
      ourServer = True
    elif 'server id ' in line:
      ourServer = False
    elif ourServer:
      sys.stdout.write(line)

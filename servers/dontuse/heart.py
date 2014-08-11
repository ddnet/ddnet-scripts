#!/usr/bin/python
# -*- coding: utf-8 -*-
import time
import sys
l = 200
m = 180

def truncate(s, length, encoding='utf-8'):
  encoded = s.encode(encoding)[:length]
  return encoded.decode(encoding, 'ignore')

for x in range(m):
  print ('broadcast "' + x * ' ' + (u'♥') + ' ' * (l - x) + '"').encode('utf-8')
  sys.stdout.flush()
  time.sleep(0.05)

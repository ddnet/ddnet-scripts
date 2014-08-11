#!/usr/bin/python
# -*- coding: utf-8 -*-
import time
import sys
s = u'._.:*~*:'
x = 0

while True:
  print ('broadcast "' + (s * 15)[x:] + '"').encode('utf-8')
  sys.stdout.flush()
  time.sleep(0.2)
  x = (x + 1) % 8

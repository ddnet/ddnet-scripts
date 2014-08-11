#!/usr/bin/python
# -*- coding: utf-8 -*-
import time
import sys
l = 134
m = 150
for x in range(m):
  print 'broadcast "' + ' ' * (l - x) + ' '.join(sys.argv[1:]) + ' ' * x + '"'
  sys.stdout.flush()
  time.sleep(0.04)

#!/usr/bin/python
# -*- coding: utf-8 -*-
import time
import sys
l = 120
m = 100
s = u'¸.·´¯`·.¸'

def truncate(s, length, encoding='utf-8'):
  encoded = s.encode(encoding)[:length]
  return encoded.decode(encoding, 'ignore')

print ("exec dontuse/3.cfg")
sys.stdout.flush()
time.sleep(3)
print ("exec dontuse/2.cfg")
sys.stdout.flush()
time.sleep(3)
print ("exec dontuse/1.cfg")
sys.stdout.flush()
time.sleep(3)

for x in range(m):
  t = truncate(truncate(s * x, x) + u'><(((º>', 60)
  print ('sv_motd "' + 3 * (t + 10 * "\\n") + '"').encode('utf-8')
  sys.stdout.flush()
  time.sleep(0.04)

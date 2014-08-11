#!/usr/bin/env python
# coding=utf-8
import readline
import sys

f = open('/home/teeworlds/servers/scripts/asciiart').readlines()

try:
  while True:
    sys.stderr.write('bc> ')
    sys.stdout.flush()
    n = sys.stdin.readline().rstrip('\n').replace('"','\\"')

    ns = n.split('|')
    t = ""

    for i in range(len(ns)):
      if i % 2 == 0:
        t += ns[i].replace('\\|','|')
      else:
        ps = []
        for c in ns[i]:
          if c >= 'a' and c <= 'z':
            ps.append(ord(c)-97)
          elif c >= 'A' and c <= 'Z':
            ps.append(ord(c)-65)
          elif c >= '0' and c <= '9':
            ps.append(ord(c)-48+26)
          elif c == ' ':
            ps.append(36)
          elif c == '.':
            ps.append(37)
          elif c == '!':
            ps.append(38)
          elif c == '?':
            ps.append(39)

        for x in range(0,6):
          for p in ps:
            t += (f[p*6+x].rstrip('\n')).replace(' ','  ')
          if x < 5:
            t += '\\n'

    print('broadcast "' + t + '"')
    sys.stdout.flush()
except:
  pass

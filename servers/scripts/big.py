#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import readline
import sys

f = open('/home/teeworlds/servers/scripts/asciiart').readlines()

def big(ns):
  t = ""
  ps = []
  for c in ns:
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

  return t

#!/usr/bin/env python

import fileinput

lines = []

codes = {}

for line in fileinput.input():
  if "[chat-command]: " in line and " used /timeout " in line:
    nr = line[35:].split(' ')[0]
    code = line[51:]

    for line in reversed(lines):
      x = line[45:].split(':')
      if nr == x[0]:
        name = x[1].split("'")[0]
        break

    codes[name] = code
  elif "[game]: team_join player='" in line and "team=-1" in line:
    lines.append(line)

print codes
print len(codes)

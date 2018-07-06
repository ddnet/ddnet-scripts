#!/usr/bin/env python2

import sys
import re

print '<table class="settingscommands">'
print '  <tr><th>Command</th><th>Arguments</th><th>Description</th></tr>'

for line in sys.stdin:
  if sys.argv[1] not in line:
    continue

  x = re.findall(r'(?:[^\s,"]|"(?:\\.|[^"])*")+', line)
  y = line.split('"')

  result = (y[1], y[3], y[-2])

  print '  <tr><td>%s</td><td>%s</td><td>%s</td></tr>' % result

print '</table>'

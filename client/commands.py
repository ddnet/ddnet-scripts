#!/usr/bin/env python3

import sys
import re
import html

print('<table class="settingscommands">')
print('  <tr><th>Command</th><th>Arguments</th><th>Description</th></tr>')

for line in sys.stdin:
  if sys.argv[1] not in line:
    continue

  x = re.findall(r'(?:[^\s,"]|"(?:\\.|[^"])*")+', line)
  y = line.split('"')

  result = (html.escape(y[1]), html.escape(y[3]), html.escape(y[-2]))

  print('  <tr><td>%s</td><td>%s</td><td>%s</td></tr>' % result)

print('</table>')

#!/usr/bin/env python2

import sys
import re

print '<table class="settingscommands">'
print '  <tr><th>Setting</th><th>Description</th><th>Default</th></tr>'

for line in sys.stdin:
  if sys.argv[1] not in line:
    continue

  x = re.findall(r'(?:[^\s,"]|"(?:\\.|[^"])*")+', line)
  y = line.split('"')

  if "STR" in line:
    result = (x[1].lstrip(), y[-2], x[3].lstrip())
  elif "INT" in line:
    result = (x[1].lstrip(), y[-2], x[-5].lstrip())

  print '  <tr><td>%s</td><td>%s</td><td>%s</td></tr>' % result

print '</table>'

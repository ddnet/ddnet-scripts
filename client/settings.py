#!/usr/bin/env python2

import sys
import re

print '<div style="overflow: auto;"><table class="settingscommands">'
print '  <tr><th>Setting</th><th>Description</th><th>Default</th></tr>'

lastname = None

results = []

for line in sys.stdin:
  if sys.argv[1] not in line:
    continue

  x = re.findall(r'(?:[^\s,"]|"(?:\\.|[^"])*")+', line)
  y = line.split('"')
  name = x[1].lstrip()

  if lastname == name:
    # Always use the last one we find, first ones are platform specific ifdefs
    results.pop()

  lastname = name

  if "STR" in line:
    result = (name, y[-2], x[3].lstrip())
  elif "INT" in line:
    result = (name, y[-2], x[-5].lstrip())

  results.append('  <tr><td>%s</td><td>%s</td><td>%s</td></tr>' % result)

for line in results:
  print line

print '</table></div>'

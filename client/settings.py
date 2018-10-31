#!/usr/bin/env python2

import sys
import re

print '<div style="overflow: auto;"><table class="settingscommands">'
print '  <tr><th>Setting</th><th>Description</th><th>Default</th></tr>'

names = {}
results = []

for line in sys.stdin:
  if sys.argv[1] not in line:
    continue

  x = re.findall(r'(?:[^\s,"]|"(?:\\.|[^"])*")+', line)
  y = line.split('"')
  name = x[1].lstrip()

  if "STR" in line:
    result = (name, y[-2], x[3].lstrip())
  elif "INT" in line:
    result = (name, y[-2], x[-5].lstrip())

  line = '  <tr><td>%s</td><td>%s</td><td>%s</td></tr>' % result

  if name in names:
    # Always use the last one we find, first ones are platform specific ifdefs
    results[names[name]] = line
  else:
    names[name] = len(results)
    results.append(line)

for line in results:
  print line

print '</table></div>'

#!/usr/bin/env python3

import sys
import re
import html

print('<div style="overflow: scroll;"><table class="settingscommands">')
print('  <tr><th>Setting</th><th>Description</th><th>Default</th></tr>')

names = {}
results = []

for line in sys.stdin:
  if sys.argv[1] not in line:
    continue

  x = re.findall(r'(?:[^\s,"]|"(?:\\.|[^"])*")+', line)
  y = line.split('"')
  name = x[1].lstrip()

  if "STR" in line:
    result = (html.escape(name), html.escape(y[-2]), html.escape(x[3].lstrip()))
  elif "INT" in line:
    result = (html.escape(name), html.escape(y[-2]), html.escape(x[-5].lstrip()))

  line = '  <tr><td>%s</td><td>%s</td><td>%s</td></tr>' % result

  if name in names:
    # Always use the last one we find, first ones are platform specific ifdefs
    results[names[name]] = line
  else:
    names[name] = len(results)
    results.append(line)

for line in results:
  print(line)

print('</table></div>')

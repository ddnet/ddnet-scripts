#!/usr/bin/env python2

import sys
import re

print '<table class="settingscommands">'
print '  <tr><th>Tuning</th><th>Description</th><th>Default</th></tr>'

def foo(x):
  if x.endswith("f / TicksPerSecond"):
    x = x.rstrip("f / TicksPerSecond")
    return float(x) / 50.0
  return x.strip("f")

for line in sys.stdin:
  x = re.findall(r'(?:[^,"]|"(?:\\.|[^"])*")+', line)

  result = (x[1].strip(), x[3].strip(" )\n").split('"')[-2], foo(x[2]))

  print '  <tr><td>%s</td><td>%s</td><td>%s</td></tr>' % result

print '</table>'

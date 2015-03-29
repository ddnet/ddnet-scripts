#!/usr/bin/env python2

import sys

print '<table class="settingscommands">'
print '  <tr><th>Tuning</th><th>Description</th><th>Default</th></tr>'

for line in sys.stdin:
  x = line.split(",")

  result = (x[1].strip(), x[3].strip(" )\n").split('"')[-2], x[2].strip("f"))

  print '  <tr><td>%s</td><td>%s</td><td>%s</td></tr>' % result

print '</table>'

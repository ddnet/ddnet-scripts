#!/usr/bin/env python3

import sys
import re
import html

print('{| class="wikitable"')
print("! Command")
print("! Arguments")
print("! Description")

for line in sys.stdin:
  if sys.argv[1] not in line:
    continue

  x = re.findall(r'(?:[^\s,"]|"(?:\\.|[^"])*")+', line)
  y = line.split('"')

  result = (html.escape(y[1]), html.escape(y[3]), html.escape(y[-2]))

  print("|-")
  print("| %s\n| %s\n| %s" % result)

print('|}')

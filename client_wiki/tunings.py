#!/usr/bin/env python3

import sys
import re
import html

print('{| class="wikitable"')
print("! Tuning")
print("! Description")
print("! Default")

def foo(x):
  if x.endswith("f / TicksPerSecond"):
    x = x.rstrip("f / TicksPerSecond")
    return float(x) / 50.0
  return x.strip("f")

for line in sys.stdin:
  x = re.findall(r'(?:[^,"]|"(?:\\.|[^"])*")+', line)

  result = (html.escape(x[1].strip()), html.escape(x[3].strip(" )\n").split('"')[-2]), html.escape(str(foo(x[2]))))

  print("|-")
  print("| %s\n| %s\n| %s" % result)

print('|}')

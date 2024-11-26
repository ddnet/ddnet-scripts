#!/usr/bin/env python3
import _mysql
f = open('race')
for l in f:
  x = l.rstrip('\n').split("\t")
  x[1] = _mysql.escape_string(x[1])
  print('insert into record_race(Map, Name, Timestamp, Time, cp1, cp2, cp3, cp4, cp5, cp6, cp7, cp8, cp9, cp10, cp11, cp12, cp13, cp14, cp15, cp16, cp17, cp18, cp19, cp20, cp21, cp22, cp23, cp24, cp25) VALUES ("%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s");' % tuple(x))

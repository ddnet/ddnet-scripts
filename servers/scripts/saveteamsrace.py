#!/usr/bin/env python2
import _mysql
f = open('teamrace')
for l in f:
  x = l.rstrip('\n').split("\t")
  x[1] = _mysql.escape_string(x[1])
  print 'insert into record_teamrace(Map, Name, Timestamp, Time, ID) VALUES ("%s", "%s", "%s", "%s", "%s");' % tuple(x)

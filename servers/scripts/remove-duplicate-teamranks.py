#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ddnet import *
import sys
import os

reload(sys)
sys.setdefaultencoding('utf8')

con = mysqlConnect()

with con:
  cur = con.cursor()
  cur.execute("set names 'utf8mb4';")

  cur.execute("select group_concat(ID order by Time asc separator '|') as IDs from (select Map, group_concat(to_base64(Name) separator '|') as Names, Timestamp, Time, ID from record_teamrace group by ID) as l group by Map, Names having count(*) > 1;");
  rows = cur.fetchall()

  ids = []
  for row in rows:
      ids.extend(row[0].split('|')[1:])
  print "Deleting:", ids
  cur.execute("delete from record_teamrace where ID in (%s)" % (','.join(['"%s"' % i for i in ids])))

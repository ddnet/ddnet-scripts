#!/usr/bin/env python2
# -*- coding: utf-8 -*-
from ddnet import *
import re

reload(sys)
sys.setdefaultencoding('utf-8')

con = mysqlConnect()

maxNode = 0
nodes = {}
#edges = []

def escape(s):
  return re.escape(s)

with con:
  cur = con.cursor()
  cur.execute("set names 'utf8mb4';")

  print('Creator "Dennis Felsing"')
  print('graph')
  print('[')

  cur.execute("select distinct Name from record_teamrace;")
  rows = cur.fetchall()
  for row in rows:
    id0 = maxNode
    maxNode += 1
    nodes[row[0]] = id0

    print('node [')
    print('id ' + str(id0))
    print('label "' + escape(row[0]) + '"')
    print(']')

    name = row[0]

    cur.execute("select Name, count(*) from record_teamrace as l inner join (select ID from record_teamrace where Name = %s) as r on l.id = r.id where Name != %s group by Name;", (name, name)) # TODO: fails
    rows = cur.fetchall()
    for row in rows:
      if row[0] in nodes.keys():
        id1 = nodes[row[0]]
        if id1 > id0:
          #edges.append((id0, id1, row[1]))

          print('edge [')
          print('source ' + str(id0))
          print('target ' + str(id1))
          print('value ' + row[1])
          print(']')

  print(']')

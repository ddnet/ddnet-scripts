#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from ddnet import *
import sys
import os
from contextlib import nullcontext

con = mysqlConnect()

# mysqlclient 2.x (py3) dropped the Connection context-manager protocol that
# py2 MySQLdb had (it committed on exit). Autocommit is off, so commit explicitly.
with nullcontext():
  cur = con.cursor()
  cur.execute("set names 'utf8mb4';")
  cur.execute("SET SESSION max_statement_time=0")  # batch job: allow long queries (global 60s net stays for web/game)

  cur.execute("select group_concat(to_base64(ID) order by Time asc separator '|') as IDs from (select Map, group_concat(to_base64(Name) separator '|') as Names, Timestamp, Time, ID from record_teamrace group by ID) as l group by Map, Names having count(*) > 1;");
  rows = cur.fetchall()

  ids = []
  for row in rows:
    ids.extend(row[0].split('|')[1:])
  print("Deleting:", ids)
  if ids:
    cur.execute("delete from record_teamrace where ID in (%s)" % (','.join(['from_base64("%s")' % con.escape_string(i).decode("utf-8") for i in ids])))

  cur.execute('DELETE r1 FROM record_race r1 JOIN record_race r2 ON r1.name = r2.name AND r1.map = "Flappy Bird" AND r2.map = "Flappy Bird" AND r1.time > r2.time;')
  cur.execute('DELETE r1 FROM record_race r1 JOIN record_race r2 ON r1.name = r2.name AND r1.map = "Edge Jump Pro" AND r2.map = "Edge Jump Pro" AND r1.time > r2.time;')
  con.commit()

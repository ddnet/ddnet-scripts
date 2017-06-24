#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ddnet import *
import datetime
import sys
import random

reload(sys)
sys.setdefaultencoding('utf8')

def postRecord(row, names):
  # TODO: markdown escape
  if not row[4].startswith("top"):
    oldTimeString = "%d points" % row[7]
  elif not row[6]:
    oldTimeString = "first finish"
  else:
    oldTimeString = "last record: %s" % formatTimeExact(row[6])
  postDiscord("New %s on \[[%s](https://ddnet.tw/ranks/%s/)\] [%s](https://ddnet.tw/ranks/%s/#map-%s): %s %s (%s)" % (row[4], row[5], row[5].lower(), row[1], row[5].lower(), normalizeMapname(row[1]), formatTimeExact(row[2]), names, oldTimeString))

os.chdir("/home/teeworlds/servers/")

con = mysqlConnect()

with con:
  cur = con.cursor()
  cur.execute("set names 'utf8';");

  with open("scripts/discord-ranks-last", 'r+') as f:
    startTime = datetime.datetime.strptime(f.read().rstrip(), "%Y-%m-%d %H:%M:%S")
    endTime = datetime.datetime.now() - datetime.timedelta(minutes=1)
    f.seek(0)
    f.write(formatDateExact(endTime))
    f.truncate()

  cur.execute("""
  select Name, lll.Map, Time, min(lll.Timestamp), max(Type), Server, max(OldTime), Points from
  (
  select Name, Map, Time, Timestamp, "top 1 rank" as Type, (select Time from record_race where Map = l.map and Timestamp < "{0}" order by Time limit 1) as OldTime from (select Timestamp, Name, Map, Time from record_race where Timestamp >= "{0}" and Timestamp < "{1}") as l where Time <= (select min(Time) from record_race where Map = l.Map)
  union all
  select Name, Map, Time, Timestamp, "top 1 teamrank" as Type, OldTime from (select ID, (select Time from record_teamrace where Map = l.Map and ID != l.ID and Timestamp < "{0}" order by Time limit 1) as OldTime from (select distinct ID, Map, Time from record_teamrace where Timestamp >= "{0}" and Timestamp < "{1}") as l left join (select Map, min(Time) as minTime from record_teamrace group by Map) as r on l.Map = r.Map where Time = minTime) as ll inner join record_teamrace as rr on ll.ID = rr.ID
  union all
  select Name, record_race.Map as Map, Time, record_race.Timestamp as Timestamp, "rank" as Type, NULL as OldTime from record_race join record_maps on record_race.Map = record_maps.Map where record_race.Timestamp >= "{0}" and record_race.Timestamp < "{1}" and record_maps.Points >= 30
  union all
  select Name, record_teamrace.Map as Map, Time, record_teamrace.Timestamp as Timestamp, "teamrank" as Type, NULL as OldTime from record_teamrace join record_maps on record_teamrace.Map = record_maps.Map where record_teamrace.Timestamp >= "{0}" and record_teamrace.Timestamp < "{1}" and record_maps.Points >= 30
  ) as lll join record_maps on lll.Map = record_maps.Map
  where lll.Map != "DontMove" and lll.Map != "Nyan Cat" group by Name, Map, Time order by lll.Timestamp;
  """.format(formatDateExact(startTime), formatDateExact(endTime)))
  rows = cur.fetchall()

  countFinishes = len(rows)
  currentRank = 0
  currentPosition = 0
  lastTime = 0
  skips = 1

  names = []

  for i, row in enumerate(rows):
    if row[4] == "teamrank" or row[4] == "top 1 teamrank":
      names.append("[%s](https://ddnet.tw%s)" % (row[0], playerWebsite(row[0])))
      if i+1 >= len(rows) or rows[i+1][1] != row[1] or rows[i+1][2] != row[2]:
        postRecord(row, makeAndString(names))
        names = []
    else:
      postRecord(row, "[%s](https://ddnet.tw%s)" % (row[0], playerWebsite(row[0])))

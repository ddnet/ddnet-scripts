#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from ddnet import *
import datetime
import sys
import random
import re

reload(sys)
sys.setdefaultencoding('utf8')

countryCodeMapping = {
    'GER': '🇩🇪',
    'RUS': '🇷🇺',
    'CHL': '🇨🇱',
    'BRA': '🇧🇷',
    'MEX': '🇲🇽',
    'PER': '🇵🇪',
    'USA': '🇺🇸',
    'CAN': '🇨🇦',
    'ZAF': '🇿🇦',
    'CHN': '🇨🇳'
}

def escapeMarkdown(name):
    return re.sub(r'([`~_\*:])', r'\\\1', name)

def postRecord(row, names):
  if not row[4].startswith("Top"):
    oldTimeString = "%d points" % row[7]
  elif not row[6]:
    oldTimeString = "first finish"
  elif row[6] == row[2]:
    oldTimeString = "new tie!"
  else:
    oldTimeString = "next best time: %s" % formatTimeExact(row[6])
  postDiscordRecords("%s %s on \[[%s](<https://ddnet.org/ranks/%s/>)\] [%s](<https://ddnet.org%s>): %s %s (%s)" % (countryCodeMapping.get(row[8], ''), row[4], row[5], row[5].lower(), row[1], mapWebsite(row[1]), formatTimeExact(row[2]), names, oldTimeString))

os.chdir("/home/teeworlds/servers/")

con = mysqlConnect()

with con:
  cur = con.cursor()
  cur.execute("set names 'utf8mb4';");

  with open("scripts/discord-ranks-last", 'r+') as f:
    startTime = datetime.datetime.strptime(f.read().rstrip(), "%Y-%m-%d %H:%M:%S")
    # give mysql replication 1 minute to get the rank over to us, otherwise we
    # won't see it here
    endTime = datetime.datetime.now() - datetime.timedelta(minutes=2)
    f.seek(0)
    f.write(formatDateExact(endTime))
    f.truncate()

  cur.execute("""
select Name, lll.Map, Time, min(lll.Timestamp), max(Type), Server, max(OldTime), Points, Country from
(
select Name, Map, Time, Timestamp, "Top 1 rank" as Type, (select Time from record_race where Map = l.map and Timestamp < "{0}" order by Time limit 1) as OldTime, Country from (select Timestamp, Name, Map, Time, Server as Country from record_race where Timestamp >= "{0}" and Timestamp < "{1}") as l where Time <= (select min(Time) from record_race where Map = l.Map)
union all
select record_teamrace.Name, record_teamrace.Map, record_teamrace.Time, record_teamrace.Timestamp, "Top 1 team rank" as Type, OldTime, record_race.Server as Country from (select ID, (select Time from record_teamrace where Map = l.Map and ID != l.ID and Timestamp < "{0}" order by Time limit 1) as OldTime from (select distinct ID, Map, Time from record_teamrace where Timestamp >= "{0}" and Timestamp < "{1}") as l left join (select Map, min(Time) as minTime from record_teamrace group by Map) as r on l.Map = r.Map where Time = minTime) as ll inner join record_teamrace on ll.ID = record_teamrace.ID join record_race on record_teamrace.Map = record_race.Map and record_teamrace.Name = record_race.Name and record_teamrace.Time = record_race.Time and record_teamrace.Timestamp = record_race.Timestamp
union all
select Name, record_race.Map as Map, Time, record_race.Timestamp as Timestamp, "Finish" as Type, NULL as OldTime, record_race.Server as Country from record_race join record_maps on record_race.Map = record_maps.Map where record_race.Timestamp >= "{0}" and record_race.Timestamp < "{1}" and (record_maps.Points >= 30 or (record_maps.Points >= 20 and record_maps.Server = "Solo") or (record_maps.Points >= 10 and record_maps.Server = "Race"))
union all
select record_teamrace.Name, record_teamrace.Map as Map, record_teamrace.Time, record_teamrace.Timestamp as Timestamp, "Team finish" as Type, NULL as OldTime, record_race.Server as Country from record_teamrace join record_maps on record_teamrace.Map = record_maps.Map join record_race on record_teamrace.Map = record_race.Map and record_teamrace.Name = record_race.Name and record_teamrace.Time = record_race.Time and record_teamrace.Timestamp = record_race.Timestamp where record_teamrace.Timestamp >= "{0}" and record_teamrace.Timestamp < "{1}" and (record_maps.Points >= 30 or (record_maps.Points >= 20 and record_maps.Server = "Solo") or (record_maps.Points >= 10 and record_maps.Server = "Race"))
) as lll join record_maps on lll.Map = record_maps.Map
where lll.Map != "Nyan Cat" group by Name, Map, Time order by lll.Timestamp;
  """.format(formatDateExact(startTime), formatDateExact(endTime)))
  rows = cur.fetchall()

  countFinishes = len(rows)
  currentRank = 0
  currentPosition = 0
  lastTime = 0
  skips = 1

  names = []

  for i, row in enumerate(rows):
    if row[4] == "Team finish" or row[4] == "Top 1 team rank":
      names.append("[%s](<https://ddnet.org%s>)" % (escapeMarkdown(row[0]), playerWebsite(row[0])))
      if i+1 >= len(rows) or rows[i+1][1] != row[1] or rows[i+1][2] != row[2]:
        postRecord(row, makeAndString(names))
        names = []
    else:
      postRecord(row, "[%s](<https://ddnet.org%s>)" % (escapeMarkdown(row[0]), playerWebsite(row[0])))

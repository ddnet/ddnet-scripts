#!/usr/bin/env python3

from ddnet import *
import sys
import os

con = mysqlConnect()

with con:
  cur = con.cursor()
  cur.execute("set names 'utf8mb4';")

  cur.execute("delete from record_achievements_tmp;")

  # Tournament winners
  f = open("tournament-winners")
  for line in f:
    words = line.rstrip('\n').split('|')

  cur.execute("rename table record_achievements to record_achievements_tmp, record_achievements_tmp to record_achievements;")

# Bronze Finisher
# 100 maps finished
# select Name, count(distinct Map) as Finishes from record_race group by Name having Finishes between 100 and 499 order by Finishes;

# Silver Finisher
# 500 maps finished
# select Name, count(distinct Map) as Finishes from record_race group by Name having Finishes between 500 and 999 order by Finishes;

# Gold Finisher
# 1000 maps finished
# select Name, count(distinct Map) as Finishes from record_race group by Name having Finishes >= 1000 order by Finishes;

# Perfect Hour
# Finish with 60:00.00
# select Map, Name, Time from record_race where Time between 3599.99 and 3600.01;

# Half a Day
# 12 hours spent on a rank
# select Map, Name, Time from record_race where Time >= 43200;

# Bronze First to Finish
# First player to finish a map after its release
# select l.Map, minTimestamp, Name from (select Map, min(Timestamp) as minTimestamp from record_race group by Map) as l left join record_race as r on l.Map = r.Map and l.minTimestamp >= r.Timestamp;

# Silver First to Finish
# First player to finish 5 maps after their release

# Gold First to Finish
# First player to finish 10 maps after their release

# From ranks.py:

# Bronze Map Lover
# 10 finishes on a single map

# Silver Map Lover
# 50 finishes on a single map

# Gold Map Lover
# 100 finishes on a single map

# Bronze Speed Record
# Fastest finish on 10 maps

# Silver Speed Record
# Fastest finish on 50 maps

# Gold Speed Record
# Fastest finish on 100 maps

# Bronze Big Team Lover
# Finish in a team of 10 players

# Silver Big Team Lover
# Finish in a team of 20 players

# Gold Big Team Lover
# Finish in a team of 30 players

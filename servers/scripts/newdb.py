#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from ddnet import *
import sys
import os
from cgi import escape
from urllib import quote_plus
from time import sleep
from datetime import datetime, timedelta

reload(sys)
sys.setdefaultencoding('utf8')

con = mysqlConnect()

rankLadder = {}
teamrankLadder = {}
pointsLadder = {}
recentPointsLadder = {}
players = {}
maps = {}
lastSQLString = ""
totalPoints = 0
serverRanks = {}
types = sys.argv[1:]

with con:
  cur = con.cursor()
  cur.execute("set names 'utf8mb4';")

  cur.execute("CREATE TABLE IF NOT EXISTS record_race (Map VARCHAR(128) BINARY NOT NULL, Name VARCHAR(16) BINARY NOT NULL, Timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP , Time FLOAT DEFAULT 0, cp1 FLOAT DEFAULT 0, cp2 FLOAT DEFAULT 0, cp3 FLOAT DEFAULT 0, cp4 FLOAT DEFAULT 0, cp5 FLOAT DEFAULT 0, cp6 FLOAT DEFAULT 0, cp7 FLOAT DEFAULT 0, cp8 FLOAT DEFAULT 0, cp9 FLOAT DEFAULT 0, cp10 FLOAT DEFAULT 0, cp11 FLOAT DEFAULT 0, cp12 FLOAT DEFAULT 0, cp13 FLOAT DEFAULT 0, cp14 FLOAT DEFAULT 0, cp15 FLOAT DEFAULT 0, cp16 FLOAT DEFAULT 0, cp17 FLOAT DEFAULT 0, cp18 FLOAT DEFAULT 0, cp19 FLOAT DEFAULT 0, cp20 FLOAT DEFAULT 0, cp21 FLOAT DEFAULT 0, cp22 FLOAT DEFAULT 0, cp23 FLOAT DEFAULT 0, cp24 FLOAT DEFAULT 0, cp25 FLOAT DEFAULT 0, KEY Name (Name)) CHARACTER SET utf8 ;")
  cur.execute("CREATE TABLE IF NOT EXISTS record_teamrace (Map VARCHAR(128) BINARY NOT NULL, Name VARCHAR(16) BINARY NOT NULL, Timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, Time FLOAT DEFAULT 0, ID VARBINARY(16) NOT NULL, KEY Name (Name)) CHARACTER SET utf8 ;")
  cur.execute("CREATE TABLE IF NOT EXISTS record_maps (Map VARCHAR(128) BINARY NOT NULL, Server VARCHAR(32) BINARY NOT NULL, Points INT DEFAULT 0, KEY Map (Map)) CHARACTER SET utf8 ;")

  for type in types:
    f = open("types/%s/maps" % type, 'r')
    for line in f:
      words = line.rstrip('\n').split('|')
      if len(words) == 0 or not words[0].isdigit():
        continue

      stars = int(words[0])
      points = globalPoints(type, stars)

      mapName = words[1]
      if len(words) > 2:
        mapperName = words[2]
      else:
        mapperName = ""

      oldMapName = normalizeMapname(mapName)

      cur.execute("INSERT IGNORE INTO record_maps(Map, Server, Points) VALUES ('%s', '%s', '%d');" % (con.escape_string(mapName), con.escape_string(type), points))

      try:
        cur.execute("select * from record_%s_teamrace;" % oldMapName)
        rows = cur.fetchall()
        cur.execute("drop table record_%s_teamrace;" % oldMapName)

        for row in rows:
          cur.execute("INSERT IGNORE INTO record_teamrace(Map, Name, Timestamp, time, ID) VALUES ('%s', '%s', '%s', '%s', '%s');" % (con.escape_string(mapName), con.escape_string(row[0]), row[1], row[2], con.escape_string(row[3])))
      except:
        pass

      try:
        cur.execute("select * from record_%s_race;" % oldMapName)
        rows = cur.fetchall()
        cur.execute("drop table record_%s_race;" % oldMapName)

        for row in rows:
          cur.execute("INSERT IGNORE INTO record_race(Map, Name, Timestamp, Time, cp1, cp2, cp3, cp4, cp5, cp6, cp7, cp8, cp9, cp10, cp11, cp12, cp13, cp14, cp15, cp16, cp17, cp18, cp19, cp20, cp21, cp22, cp23, cp24, cp25) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s');" % (con.escape_string(mapName), con.escape_string(row[0]), row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18], row[19], row[20], row[21], row[22], row[23], row[24], row[25], row[26], row[27]))
      except:
        pass

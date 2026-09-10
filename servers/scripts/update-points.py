#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from ddnet import *
import sys
import os
from html import escape
from urllib.parse import quote_plus
from time import sleep
from datetime import datetime, timedelta
from contextlib import nullcontext

sys.stdout.reconfigure(encoding='utf-8')

con = mysqlConnect()

types = sys.argv[1:]

releases = []
with open("releases") as f:
  for line in f:
    words = line.rstrip('\n').split('\t')
    releases.append(tuple(words))

# mysqlclient 2.x (py3) dropped the Connection context-manager protocol that
# py2 MySQLdb had (it committed on exit). Autocommit is off, so commit explicitly.
with nullcontext():
  cur = con.cursor()
  cur.execute("set names 'utf8mb4';")

  cur.execute("CREATE TABLE IF NOT EXISTS record_mapinfo (Map VARCHAR(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL, Width int(11) default 0, Height int(11) default 0, %s, primary key (Map)) default charset=utf8mb4;" % (", ".join([x + " tinyint(1) default 0" for x in all_tiles])))

  for type in types:
    f = open("types/%s/maps" % type.lower(), 'r')
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
        mapperName = "Unknown Mapper"

      realDate = None

      for x in releases:
        try:
          dateString, server, y = x
          date = datetime.strptime(dateString, '%Y-%m-%d %H:%M')
          try:
            stars2, origMapName, mapperName2 = y.split('|')
          except ValueError:
            stars2, origMapName = y.split('|')
            mapperName2 = ""

          if mapName == origMapName and date >= datetime(2013,10,15):
            realDate = dateString
            break
        except:
          pass

      cur.execute("INSERT INTO record_maps(Map, Server, Mapper, Points, Stars, Timestamp) VALUES ('%s', '%s', '%s', '%d', '%d', %s) ON duplicate key UPDATE Server=VALUES(Server), Mapper=VALUES(Mapper), Points=VALUES(Points), Stars=VALUES(Stars), Timestamp=VALUES(Timestamp);" % (con.escape_string(mapName).decode('utf-8'), con.escape_string(type).decode('utf-8'), con.escape_string(mapperName).decode('utf-8'), points, stars, "'" + realDate + "'" if realDate else "0"))

      with open('maps/%s.msgpack' % mapName, 'rb') as inp:
        try:
          unpacker = msgpack.Unpacker(inp)
          width = unpacker.unpack()
          height = unpacker.unpack()
          ts = unpacker.unpack()
          cur.execute("REPLACE INTO record_mapinfo (Map, Width, Height, %s) VALUES ('%s', %d, %d, %s);" % (", ".join(all_tiles), con.escape_string(mapName).decode('utf-8'), width, height, ", ".join([str(ts.get(tile, False)) for tile in all_tiles])))
        except:
          print("Failed to insert " + mapName)

  con.commit()

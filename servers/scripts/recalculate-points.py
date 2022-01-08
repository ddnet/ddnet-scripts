#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from ddnet import *
import sys
import os
from cgi import escape
from urllib import quote_plus
from time import sleep
from datetime import datetime, timedelta
import msgpack
import cStringIO

reload(sys)
sys.setdefaultencoding('utf8')

lastModified = datetime.fromtimestamp(os.path.getmtime('%s/players.msgpack' % webDir))
#print('Points last updated: %s' % lastModified.strftime('%m-%d-%Y %H:%M:%S'))

types = None
maps = None
totalPoints = None
pointsRanks = None
weeklyPointsRanks = None
monthlyPointsRanks = None
yearlyPointsRanks = None
teamrankRanks = None
rankRanks = None
serverRanks = None

with open('%s/players.msgpack' % webDir, 'rb') as inp:
  unpacker = msgpack.Unpacker(inp)
  types = unpacker.unpack()
  maps = unpacker.unpack()
  totalPoints = unpacker.unpack()
  pointsRanks = unpacker.unpack()
  weeklyPointsRanks = unpacker.unpack()
  monthlyPointsRanks = unpacker.unpack()
  yearlyPointsRanks = unpacker.unpack()
  teamrankRanks = unpacker.unpack()
  rankRanks = unpacker.unpack()
  serverRanks = unpacker.unpack()

con = mysqlConnect()

with con:
  cur = con.cursor()
  cur.execute("set names 'utf8mb4';")

  cur.execute("DELETE FROM record_points;")

  for r in pointsRanks:
    cur.execute("INSERT INTO record_points(Name, Points) VALUES ('%s', '%d') ON duplicate key UPDATE Name=VALUES(Name), Points=VALUES(Points);" % (con.escape_string(r[0]), r[1]))

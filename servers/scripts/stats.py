#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ddnet import *
import sys
import msgpack
import locale
from cgi import escape
from datetime import datetime, timedelta
from collections import defaultdict, OrderedDict

def strfdelta(tdelta, fmt):
  d = {}
  d["years"], d["days"] = divmod(tdelta.days, 365)
  d["hours"], rem = divmod(tdelta.seconds, 3600)
  d["minutes"], d["seconds"] = divmod(rem, 60)
  return fmt.format(**d)

locale.setlocale(locale.LC_ALL, 'en_US')
reload(sys)
sys.setdefaultencoding('utf8')

startDate = datetime.today() - timedelta(weeks = 4)

# Finishes
con = mysqlConnect()
with con:
  cur = con.cursor()
  cur.execute("set names 'utf8';");

  cur.execute("select count(*) from record_maps;")
  rows = cur.fetchall()
  nrMaps = locale.format("%d", int(rows[0][0]), grouping=True)

  cur.execute("select count(*) from (select Name from record_race group by Name) as l;")
  rows = cur.fetchall()
  nrPlayers = locale.format("%d", int(rows[0][0]), grouping=True)

  cur.execute("select count(*) from record_race;")
  rows = cur.fetchall()
  nrRanks = locale.format("%d", int(rows[0][0]), grouping=True)

  cur.execute('select sum(Time) from record_race where Map != "Flappy Bird";')
  rows = cur.fetchall()
  timeRanks = strfdelta(timedelta(seconds = rows[0][0]), "{years} years, {days} days and {hours} hours")

  yesterday = datetime.now() - timedelta(days=1)
  cur.execute('select sum(Time) from record_race where Map != "Flappy Bird" and DATE(Timestamp) = "%s";' % yesterday.strftime("%Y-%m-%d"))
  rows = cur.fetchall()
  timeRanksYesterday = strfdelta(timedelta(seconds = rows[0][0]), "{days} days and {hours} hours")

  cur.execute("select year(Timestamp), month(Timestamp), day(Timestamp), count(*) from record_race group by year(Timestamp), month(Timestamp), day(Timestamp) order by Timestamp;")
  rows = cur.fetchall()
  finishes = ""
  lastDay = datetime(2014,12,28)
  for row in rows:
    currDay = datetime(row[0], row[1], row[2])
    lastDay += timedelta(days=1)
    while lastDay < currDay:
      finishes += ", 0"
      lastDay += timedelta(days=1)
    if len(finishes) > 0:
      finishes += ", "
    finishes += '%d' % row[3]
    lastDay = currDay

  # Points by country
  cur.execute("select record_race.Server, year(record_race.Timestamp), month(record_race.Timestamp), day(record_race.Timestamp), sum(Points) from record_race join record_maps on record_race.Map = record_maps.Map group by record_race.Server, year(record_race.Timestamp), month(record_race.Timestamp), day(record_race.Timestamp) order by record_race.Server, record_race.Timestamp;")
  rows = cur.fetchall()
  countryPoints = ""
  oldServer = None

  for row in rows:
    server = row[0]
    currDay = datetime(row[1], row[2], row[3])

    if server != oldServer:
      if countryPoints != "":
        countryPoints += "]}, "
      lastDay = datetime(2013,07,18)
      countryPoints += "{name: '%s', pointInterval: 24 * 3600 * 1000, pointStart: Date.UTC(%d,%d,%d), data: [" % (server, lastDay.year, lastDay.month-1, lastDay.day)
    else:
      lastDay += timedelta(days=1)

    while lastDay < currDay:
      if lastDay > datetime(2013,07,18):
        countryPoints += ", "
      countryPoints += "0"
      lastDay += timedelta(days=1)

    if lastDay > datetime(2013,07,18):
      countryPoints += ", "
    countryPoints += '%d' % row[4]
    oldServer = server

  countryPoints += "]}"

  # Points by server
  cur.execute("select record_maps.Server, year(record_race.Timestamp), month(record_race.Timestamp), day(record_race.Timestamp), sum(Points) from record_race join record_maps on record_race.Map = record_maps.Map group by record_maps.Server, year(record_race.Timestamp), month(record_race.Timestamp), day(record_race.Timestamp) order by record_maps.Server, record_race.Timestamp;")
  rows = cur.fetchall()
  serverPoints = ""
  oldServer = None

  with open("all-types") as f:
    for server in reversed(f.read().rstrip('\n').split(' ')):
      for row in rows:
        if server != row[0]:
          continue

        currDay = datetime(row[1], row[2], row[3])

        if server != oldServer:
          if serverPoints != "":
            serverPoints += "]}, "
          lastDay = datetime(2013,07,18)
          serverPoints += "{name: '%s', pointInterval: 24 * 3600 * 1000, pointStart: Date.UTC(%d,%d,%d), data: [" % (server, lastDay.year, lastDay.month-1, lastDay.day)
        else:
          lastDay += timedelta(days=1)

        while lastDay < currDay:
          if lastDay > datetime(2013,07,18):
            serverPoints += ", "
          serverPoints += "0"
          lastDay += timedelta(days=1)

        if lastDay > datetime(2013,07,18):
          serverPoints += ", "
        serverPoints += '%d' % row[4]
        oldServer = server

  serverPoints += "]}"

# Maps
releases = []
with open("releases") as f:
  for line in f:
    words = line.rstrip('\n').split('\t')
    releases.append(tuple(words))

maps = OrderedDict()
with open("all-types") as f:
  for server in reversed(f.read().rstrip('\n').split(' ')):
    maps[server] = {}

for x in releases:
  dateString, server, y = x
  date = datetime.strptime(dateString, '%Y-%m-%d %H:%M')
  if date < datetime(2013,11,01):
    continue

  for s2, vals in maps.iteritems():
    if not (date.year, date.month) in vals:
      vals[(date.year, date.month)] = 0
  maps[server][(date.year, date.month)] += 1

  try:
    stars, originalMapName, mapperName = y.split('|')
  except ValueError:
    stars, originalMapName = y.split('|')
    mapperName = ""

  stars = int(stars)

  mapName = normalizeMapname(originalMapName)

  if not mapperName:
    mbMapperName = ""
  else:
    names = splitMappers(mapperName)
    newNames = []
    for name in names:
      newNames.append('<a href="%s">%s</a>' % (mapperWebsite(name), escape(name)))

    mbMapperName = "<strong>by %s</strong><br/>" % makeAndString(newNames)

  formattedMapName = escape(originalMapName)

m = ""
for server, dates in maps.iteritems():
  if len(m) > 0:
    m += ", "
  m += "{name: '%s', data: [" % server
  n = ""
  for date, num in sorted(dates.iteritems()):
    if len(n) > 0:
      n += ", "
    n += '[Date.UTC(%d,%d), %d]' % (date[0], date[1]-1, num)
  m += n + "]}"

# Players by Country
players = OrderedDict()
startDate2 = None
with open('%s/status/csv/bycountry' % webDir) as f:
  for line in f:
    tokens = line.rstrip('\n').split(',')
    date = datetime.strptime(tokens[0], '%Y-%m-%d %H:%M')
    if not startDate2:
      startDate2 = date
    for token in tokens[1:]:
      sn = token.split(':')
      if sn[0] not in players:
        players[sn[0]] = {}
      players[sn[0]][date] = int(sn[1])

p = ""
scale = 30
for server, dates in players.iteritems():
  if len(p) > 0:
    p += ", "
  p += "{name: '%s', pointInterval: %d * 2 * 60 * 1000, pointStart: Date.UTC(%d,%d,%d,%d,%d), data: [" % (server, scale, startDate.year, startDate.month-1, startDate.day, startDate.hour, startDate.minute)
  n = ""
  pos = 1
  aggNum = 0
  lastDate = startDate
  for date, num in sorted(dates.iteritems()):
    currDate = datetime(date.year, date.month, date.day, date.hour, date.minute)
    if currDate < startDate:
      continue
    lastDate += timedelta(minutes=2)
    while lastDate < currDate:
      lastDate += timedelta(minutes=2)
      if pos == 0:
        if len(n) > 0:
          n += ", "
        n += "%s" % aggNum
        aggNum = 0
      pos = (pos + 1) % scale

    if num > aggNum:
      aggNum = num
    if pos == 0:
      if len(n) > 0:
        n += ", "
      n += "%s" % aggNum
      aggNum = 0
    pos = (pos + 1) % scale
  p += n + "]}"

p3 = ""
scale = 720
for server, dates in players.iteritems():
  if dates.keys()[0] < startDate2:
    startDate2 = dates.keys()[0]
for server, dates in players.iteritems():
  if len(p3) > 0:
    p3 += ", "
  p3 += "{name: '%s', pointInterval: %d * 2 * 60 * 1000, pointStart: Date.UTC(%d,%d,%d,%d,%d), data: [" % (server, scale, startDate2.year, startDate2.month-1, startDate2.day, startDate2.hour, startDate2.minute)
  n = ""
  pos = 1
  aggNum = 0
  lastDate = startDate2
  for date, num in sorted(dates.iteritems()):
    currDate = datetime(date.year, date.month, date.day, date.hour, date.minute)
    lastDate += timedelta(minutes=2)
    while lastDate < currDate:
      lastDate += timedelta(minutes=2)
      if pos == 0:
        if len(n) > 0:
          n += ", "
        n += "%s" % (aggNum / 30)
        aggNum = 0
      pos = (pos + 1) % scale

    aggNum += num
    if pos == 0:
      if len(n) > 0:
        n += ", "
      n += "%s" % (aggNum / 30)
      aggNum = 0
    pos = (pos + 1) % scale
  p3 += n + "]}"

# Players by Mod
players = OrderedDict()
startDate2 = None
with open('%s/status/csv/bymod' % webDir) as f:
  for line in f:
    tokens = line.rstrip('\n').split(',')
    date = datetime.strptime(tokens[0], '%Y-%m-%d %H:%M')
    if not startDate2:
      startDate2 = date
    for token in tokens[1:]:
      sn = token.split(':')
      if sn[0] not in players:
        players[sn[0]] = {}
      players[sn[0]][date] = int(sn[1])
p2 = ""
scale = 30
for server, dates in players.iteritems():
  if len(p2) > 0:
    p2 += ", "
  p2 += "{name: '%s', pointInterval: %d * 2 * 60 * 1000, pointStart: Date.UTC(%d,%d,%d,%d,%d), data: [" % (server, scale, startDate.year, startDate.month-1, startDate.day, startDate.hour, startDate.minute)
  n = ""
  pos = 1
  aggNum = 0
  lastDate = startDate
  for date, num in sorted(dates.iteritems()):
    currDate = datetime(date.year, date.month, date.day, date.hour, date.minute)
    if currDate < startDate:
      continue
    lastDate += timedelta(minutes=2)
    while lastDate < currDate:
      lastDate += timedelta(minutes=2)
      if pos == 0:
        if len(n) > 0:
          n += ", "
        n += "%s" % aggNum
        aggNum = 0
      pos = (pos + 1) % scale

    if num > aggNum:
      aggNum = num
    if pos == 0:
      if len(n) > 0:
        n += ", "
      n += "%s" % aggNum
      aggNum = 0
    pos = (pos + 1) % scale
  p2 += n + "]}"

p4 = ""
scale = 720
for server, dates in players.iteritems():
  if len(p4) > 0:
    p4 += ", "
  p4 += "{name: '%s', pointInterval: %d * 2 * 60 * 1000, pointStart: Date.UTC(%d,%d,%d,%d,%d), data: [" % (server, scale, startDate2.year, startDate2.month-1, startDate2.day, startDate2.hour, startDate2.minute)
  n = ""
  pos = 1
  aggNum = 0
  lastDate = startDate2
  for date, num in sorted(dates.iteritems()):
    currDate = datetime(date.year, date.month, date.day, date.hour, date.minute)
    lastDate += timedelta(minutes=2)
    while lastDate < currDate:
      lastDate += timedelta(minutes=2)
      if pos == 0:
        if len(n) > 0:
          n += ", "
        n += "%s" % (aggNum / 30)
        aggNum = 0
      pos = (pos + 1) % scale

    aggNum += num
    if pos == 0:
      if len(n) > 0:
        n += ", "
      n += "%s" % (aggNum / 30)
      aggNum = 0
    pos = (pos + 1) % scale
  p4 += n + "]}"

otherIncludes = '<script type="text/javascript" src="js/jquery.min.js"></script>'
with open('scripts/stats.js') as f:
  otherIncludes += '<script type="text/javascript">' + f.read() + '</script>'

menu = """<ul>
  <li><a href="/stats/">Player Statistics</a></li>
  <li><a href="/stats/server/">Server Statistics</a></li>
</ul>"""
text = header("Statistics & Charts", menu, "", False, False, otherIncludes)

with open('scripts/stats.html') as f:
  text += f.read()

# Country records
countryRecords = OrderedDict()
with open('%s/status/csv/bycountry' % webDir) as f:
  for line in f:
    tokens = line.rstrip('\n').split(',')
    date = datetime.strptime(tokens[0], '%Y-%m-%d %H:%M')
    for token in tokens[1:]:
      sn = token.split(':')
      if sn[0] not in countryRecords or countryRecords[sn[0]][0] < int(sn[1]):
        countryRecords[sn[0]] = (int(sn[1]), date)
countryRecordsString = ""
for server, item in countryRecords.iteritems():
  record = item[0]
  date = item[1]
  if len(countryRecordsString) > 0:
    countryRecordsString += ", "
  countryRecordsString += '<span title="%s">%s: %d</span>' % (date, server, record)

print text % (p, p2, p3, p4, finishes, countryPoints, serverPoints, m, nrMaps, nrPlayers, nrRanks, timeRanks, timeRanksYesterday, countryRecordsString)

print """</section>
</article>
</body>
</html>"""

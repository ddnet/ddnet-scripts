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

  # Points
  #cur.execute("select year(Timestamp), month(Timestamp), day(Timestamp), sum(Points) from record_race inner join record_maps on record_race.Map = record_maps.Map group by year(Timestamp), month(Timestamp), day(Timestamp) order by Timestamp;")
  #rows = cur.fetchall()
  #points = ""
  #for row in rows:
  #  if len(points) > 0:
  #    points+= ", "
  #  points += '[Date.UTC(%d,%d,%d), %d]' % (row[0], row[1]-1, row[2], row[3])

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
with open('%s/status/csv/bycountry' % webDir) as f:
  for line in f:
    tokens = line.rstrip('\n').split(',')
    date = datetime.strptime(tokens[0], '%Y-%m-%d %H:%M')
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

# Players by Mod
players = OrderedDict()
with open('%s/status/csv/bymod' % webDir) as f:
  for line in f:
    tokens = line.rstrip('\n').split(',')
    date = datetime.strptime(tokens[0], '%Y-%m-%d %H:%M')
    for token in tokens[1:]:
      sn = token.split(':')
      if sn[0] not in players:
        players[sn[0]] = {}
      players[sn[0]][date] = int(sn[1])
p2 = ""
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

otherIncludes = '<script type="text/javascript" src="js/jquery.min.js"></script>'
with open('scripts/stats.js') as f:
  otherIncludes += '<script type="text/javascript">' + f.read() + '</script>'

text = header("Statistics & Charts", "", "", False, False, otherIncludes)

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

print text % (p, p2, finishes, m, nrMaps, nrPlayers, nrRanks, timeRanks, timeRanksYesterday, countryRecordsString)

print """</section>
</article>
</body>
</html>"""

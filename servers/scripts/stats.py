#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from ddnet import *
import sys
import msgpack
import locale
from cgi import escape
from datetime import datetime, timedelta
from time import strftime
from collections import defaultdict, OrderedDict

def strfdelta(tdelta, fmt):
  d = {}
  d["years"], d["days"] = divmod(tdelta.days, 365)
  d["hours"], rem = divmod(tdelta.seconds, 3600)
  d["minutes"], d["seconds"] = divmod(rem, 60)
  return fmt.format(**d)

def changeStr(now, before):
    if before == 0:
        return ""
    else:
        change = 100.0 * (now - before) / before
        return ("+" if int(change) > 0 else "") + "%d%%" % change

locale.setlocale(locale.LC_ALL, 'en_US')
reload(sys)
sys.setdefaultencoding('utf8')

ignoredCountries = ("GER2",) #("KSA", "AUS", "FRA")
now = datetime.today()
startDateWeek = now - timedelta(weeks = 1)
startDateLastWeek = now - timedelta(weeks = 2)
startDateDay = now - timedelta(days = 1)
startDateLastDay = now - timedelta(days = 2)

# Finishes
con = mysqlConnect()
with con:
  cur = con.cursor()
  cur.execute("set names 'utf8mb4';")

  nrMaps = {}
  cur.execute("select Server, count(*) from record_maps group by Server;")
  rows = cur.fetchall()
  for row in rows:
      nrMaps[row[0]] = row[1]

  cur.execute("select count(*) from record_maps;")
  rows = cur.fetchall()
  nrMaps["Total"] = rows[0][0]

  with open('/home/teeworlds/servers/all-types', 'r') as f:
    types = f.read().split()

  avgTime = {}
  cur.execute('select record_maps.Server, avg(Time) from record_race inner join record_maps on record_race.Map = record_maps.Map where record_race.Map != "Flappy Bird" and record_race.Map != "Time Shop" and record_race.Map != "Bullseye" and record_race.Map != "Care for your Time" group by record_maps.Server;')
  rows = cur.fetchall()
  for row in rows:
      avgTime[row[0]] = formatTime(row[1])

  cur.execute('select avg(Time) from record_race inner join record_maps on record_race.Map = record_maps.Map where record_race.Map != "Flappy Bird" and record_race.Map != "Time Shop" and record_race.Map != "Bullseye" and record_race.Map != "Care for your Time";')
  rows = cur.fetchall()
  avgTime["Total"] = formatTime(rows[0][0])

  nrFinishesType = {}
  nrRanksType = {}
  cur.execute('select record_maps.Server, count(*), count(distinct Name) from record_race inner join record_maps on record_race.Map = record_maps.Map group by record_maps.Server;')
  rows = cur.fetchall()
  for row in rows:
      nrFinishesType[row[0]] = locale.format("%d", int(row[1]), grouping=True)
      nrRanksType[row[0]] = locale.format("%d", int(row[2]), grouping=True)

  cur.execute('select count(*), count(distinct Name) from record_race inner join record_maps on record_race.Map = record_maps.Map;')
  rows = cur.fetchall()
  nrFinishesType["Total"] = locale.format("%d", int(rows[0][0]), grouping=True)
  nrRanksType["Total"] = locale.format("%d", int(rows[0][1]), grouping=True)

  def getRanksTyp(result, start, end):
      cur.execute('select record_maps.Server, count(*) from record_race inner join record_maps on record_race.Map = record_maps.Map where record_race.Timestamp >= "%s" and record_race.Timestamp < "%s" group by record_maps.Server;' % (start.strftime("%Y-%m-%d %H:%M:%S"), end.strftime("%Y-%m-%d %H:%M:%S")))
      rows = cur.fetchall()
      for row in rows:
          result[row[0]] = row[1]

      cur.execute('select count(*) from record_race where record_race.Timestamp >= "%s" and Timestamp < "%s";' % (start.strftime("%Y-%m-%d %H:%M:%S"), end.strftime("%Y-%m-%d %H:%M:%S")))
      rows = cur.fetchall()
      result["Total"] = rows[0][0]

  ranksTypDay = {}
  ranksTypLastDay = {}
  ranksTypWeek = {}
  ranksTypLastWeek = {}
  getRanksTyp(ranksTypDay, startDateDay, now)
  getRanksTyp(ranksTypLastDay, startDateLastDay, startDateDay)
  getRanksTyp(ranksTypWeek, startDateWeek, now)
  getRanksTyp(ranksTypLastWeek, startDateLastWeek, startDateWeek)

  cur.execute('select count(*) from record_race where record_race.Timestamp >= "%s" and record_race.Timestamp < "%s";' % (startDateLastWeek.strftime("%Y-%m-%d %H:%M:%S"), startDateWeek.strftime("%Y-%m-%d %H:%M:%S")))
  rows = cur.fetchall()
  ranksTypLastWeek["Total"] = rows[0][0]

  tableTypes = ''
  for typ in types:
    ranksDay = ranksTypDay.get(typ, 0)
    ranksLastDay = ranksTypLastDay.get(typ, 0)
    ranksWeek = ranksTypWeek.get(typ, 0)
    ranksLastWeek = ranksTypLastWeek.get(typ, 0)
    tableTypes += '<tr><td style="text-align: right;"><strong>%s</strong></td><td style="text-align: right;">%s</td><td style="text-align: right;">%s</td><td style="text-align: right;">%s</td><td style="text-align: right;">%s</td><td style="text-align: right;">%s</td><td style="text-align: right;">%s</td><td style="text-align: right;">%s</td><td style="text-align: right;"><a href="/ranks/%s/">%s</a></td></tr>\n' % (typ, locale.format("%d", ranksDay, grouping=True), changeStr(ranksDay, ranksLastDay), locale.format("%d", ranksWeek, grouping=True), changeStr(ranksWeek, ranksLastWeek), locale.format("%d", nrMaps[typ], grouping=True), avgTime[typ], nrRanksType[typ], typ.lower(), nrFinishesType[typ])
  # Total
  tableTypes += '<tr style="border-top: .5em solid transparent;"><td style="text-align: right;"><strong>%s</strong></td><td style="text-align: right;">%s</td><td style="text-align: right;">%s</td><td style="text-align: right;">%s</td><td style="text-align: right;">%s</td><td style="text-align: right;"><a href="/releases/">%s</a></td><td style="text-align: right;">%s</td><td style="text-align: right;">%s</td><td style="text-align: right;"><a href="/ranks/">%s</a></td></tr>' % ("Total", locale.format("%d", ranksTypDay["Total"], grouping=True), changeStr(ranksTypDay["Total"], ranksTypLastDay["Total"]), locale.format("%d", ranksTypWeek["Total"], grouping=True), changeStr(ranksTypWeek["Total"], ranksTypLastWeek["Total"]), locale.format("%d", nrMaps["Total"], grouping=True), avgTime["Total"], nrRanksType["Total"], nrFinishesType["Total"])

  nrPlayers = {}
  cur.execute("select count(distinct Name) from record_race;")
  rows = cur.fetchall()
  nrPlayers["Total"] = locale.format("%d", int(rows[0][0]), grouping=True)

  record_race = "(select Map, Name, Timestamp, Time, case Server when 'NLD' then 'EUR' when 'GER' then 'EUR' when 'POL' then 'EUR' when 'FRA' then 'EUR' else Server end as Server from record_race) as record_race"
  cur.execute("select Server, count(distinct Name) from %s group by Server;" % record_race)
  rows = cur.fetchall()
  for row in rows:
      nrPlayers[row[0]] = locale.format("%d", int(row[1]), grouping=True)

  nrRanks = {}
  cur.execute("select count(*) from record_race;")
  rows = cur.fetchall()
  nrRanks["Total"] = locale.format("%d", int(rows[0][0]), grouping=True)

  cur.execute("select Server, count(*) from %s group by Server;" % record_race)
  rows = cur.fetchall()
  for row in rows:
      nrRanks[row[0]] = locale.format("%d", int(row[1]), grouping=True)

  todayStr = now.strftime("%Y-%m-%d")
  cur.execute('select year(Timestamp), month(Timestamp), day(Timestamp), count(*) from record_race where Timestamp < "%s" group by year(Timestamp), month(Timestamp), day(Timestamp) order by Timestamp;' % todayStr)
  rows = cur.fetchall()
  data = []
  lastDay = datetime(2014,12,28)
  for row in rows:
    currDay = datetime(row[0], row[1], row[2])
    lastDay += timedelta(days=1)
    while lastDay < currDay:
      data.append(0)
      lastDay += timedelta(days=1)
    data.append(int(row[3]))
    lastDay = currDay
  filename = "%s/stats/finishes.json" % webDir
  tmpname = "%s/stats/finishes.%d.tmp" % (webDir, os.getpid())
  with open(tmpname, 'w') as tf:
    json.dump(data, tf)
  os.rename(tmpname, filename)

  # Points by country
  cur.execute('select record_race.Server, year(record_race.Timestamp), month(record_race.Timestamp), day(record_race.Timestamp), sum(Points) from record_race join record_maps on record_race.Map = record_maps.Map where record_race.Timestamp < "%s" group by record_race.Server, year(record_race.Timestamp), month(record_race.Timestamp), day(record_race.Timestamp) order by record_race.Server, record_race.Timestamp;' % todayStr)
  rows = cur.fetchall()
  oldServer = None

  data = []
  series = None
  for row in rows:
    server = row[0]
    currDay = datetime(row[1], row[2], row[3])

    if server != oldServer:
      lastDay = datetime(2013,07,18)
      if series:
        data.append(series)
      series = {"name": server, "pointInterval": 24 * 3600 * 1000, "pointStart": int(lastDay.strftime("%s")) * 1000, "data": []}
    else:
      lastDay += timedelta(days=1)

    while lastDay < currDay:
      series["data"].append(0)
      lastDay += timedelta(days=1)

    series["data"].append(int(row[4]))
    oldServer = server

  if series:
    data.append(series)

  filename = "%s/stats/pointscountry.json" % webDir
  tmpname = "%s/stats/pointscountry.%d.tmp" % (webDir, os.getpid())
  with open(tmpname, 'w') as tf:
    json.dump(data, tf)
  os.rename(tmpname, filename)

  # Points by server
  cur.execute('select record_maps.Server, year(record_race.Timestamp), month(record_race.Timestamp), day(record_race.Timestamp), sum(Points) from record_race join record_maps on record_race.Map = record_maps.Map where record_race.Timestamp < "%s" group by record_maps.Server, year(record_race.Timestamp), month(record_race.Timestamp), day(record_race.Timestamp) order by record_maps.Server, record_race.Timestamp;' % todayStr)
  rows = cur.fetchall()
  oldServer = None

  data = []
  series = None
  with open("/home/teeworlds/servers/all-types") as f:
    for server in reversed(f.read().rstrip('\n').split(' ')):
      for row in rows:
        if server != row[0]:
          continue

        currDay = datetime(row[1], row[2], row[3])

        if server != oldServer:
          if series:
            data.append(series)
          lastDay = datetime(2013,07,18)
          series = {"name": server, "pointInterval": 24 * 3600 * 1000, "pointStart": int(lastDay.strftime("%s")) * 1000, "data": []}
        else:
          lastDay += timedelta(days=1)

        while lastDay < currDay:
          series["data"].append(0)
          lastDay += timedelta(days=1)

        series["data"].append(int(row[4]))
        oldServer = server

  if series:
    data.append(series)

  filename = "%s/stats/pointsserver.json" % webDir
  tmpname = "%s/stats/pointsserver.%d.tmp" % (webDir, os.getpid())
  with open(tmpname, 'w') as tf:
    json.dump(data, tf)
  os.rename(tmpname, filename)

# Maps
releases = []
with open("releases") as f:
  for line in f:
    words = line.rstrip('\n').split('\t')
    releases.append(tuple(words))

maps = OrderedDict()
with open("/home/teeworlds/servers/all-types") as f:
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

data = []
for server, dates in maps.iteritems():
  series = {"name": server, "data": []}
  for date, num in sorted(dates.iteritems()):
    series["data"].append([int(datetime(date[0], date[1], 1).strftime("%s")) * 1000, num])
  data.append(series)
filename = "%s/stats/mapreleases.json" % webDir
tmpname = "%s/stats/mapreleases.%d.tmp" % (webDir, os.getpid())
with open(tmpname, 'w') as tf:
  json.dump(data, tf)
os.rename(tmpname, filename)

# Players by Country
players = OrderedDict()
startDate = None
countryRecords = OrderedDict()
countryRecords["Total"] = (0, None)
countryAverages = OrderedDict()
countryAveragesLastWeek = OrderedDict()
countryAveragesDay = OrderedDict()
countryAveragesLastDay = OrderedDict()
numElementsWeek = 0
numElementsLastWeek = 0
numElementsDay = 0
numElementsLastDay = 0

with open('%s/status/csv/bycountry' % webDir) as f:
  for line in f:
    tokens = line.rstrip('\n').split(',')
    date = datetime.strptime(tokens[0], '%Y-%m-%d %H:%M')
    if not startDate:
      startDate = date
    numPlayers = 0
    for token in tokens[1:]:
      sn = token.split(':')
      if sn[0] not in players:
        players[sn[0]] = {}
      p = int(sn[1])
      numPlayers += p
      players[sn[0]][date] = p
      if sn[0] in ignoredCountries:
        continue
      if sn[0] not in countryRecords or countryRecords[sn[0]][0] < p:
        countryRecords[sn[0]] = (p, tokens[0])
      if date >= startDateWeek:
        if sn[0] not in countryAverages:
          countryAverages[sn[0]] = p
        else:
          countryAverages[sn[0]] += p
      elif date >= startDateLastWeek:
        if sn[0] not in countryAveragesLastWeek:
          countryAveragesLastWeek[sn[0]] = p
        else:
          countryAveragesLastWeek[sn[0]] += p
      if date >= startDateDay:
        if sn[0] not in countryAveragesDay:
          countryAveragesDay[sn[0]] = p
        else:
          countryAveragesDay[sn[0]] += p
      elif date >= startDateLastDay:
        if sn[0] not in countryAveragesLastDay:
          countryAveragesLastDay[sn[0]] = p
        else:
          countryAveragesLastDay[sn[0]] += p
    if date >= startDateWeek:
      numElementsWeek += 1
    elif date >= startDateLastWeek:
      numElementsLastWeek += 1
    if date >= startDateDay:
      numElementsDay += 1
    elif date >= startDateLastDay:
      numElementsLastDay += 1
    if numPlayers > countryRecords["Total"][0]:
      countryRecords["Total"] = (numPlayers, tokens[0])

scale = 30
data = []
for server, dates in players.iteritems():
  series = {"name": server, "pointInterval": scale * 2 * 60 * 1000, "pointStart": int(startDate.strftime("%s")) * 1000, "data": []}
  pos = 1
  aggNum = 0
  lastDate = startDate
  for date, num in sorted(dates.iteritems()):
    currDate = datetime(date.year, date.month, date.day, date.hour, date.minute)
    lastDate += timedelta(minutes=2)
    while lastDate < currDate:
      lastDate += timedelta(minutes=2)
      if pos == 0:
        series["data"].append(aggNum)
        aggNum = 0
      pos = (pos + 1) % scale

    if num > aggNum:
      aggNum = num
    if pos == 0:
      series["data"].append(aggNum)
      aggNum = 0
    pos = (pos + 1) % scale
  data.append(series)
filename = "%s/stats/bycountry.json" % webDir
tmpname = "%s/stats/bycountry.%d.tmp" % (webDir, os.getpid())
with open(tmpname, 'w') as tf:
  json.dump(data, tf)
os.rename(tmpname, filename)

scale = 720
data = []
for server, dates in players.iteritems():
  if dates.keys()[0] < startDate:
    startDate = dates.keys()[0]
for server, dates in players.iteritems():
  series = {"name": server, "pointInterval": scale * 2 * 60 * 1000, "pointStart": int(startDate.strftime("%s")) * 1000, "data": []}
  pos = 1
  aggNum = 0
  lastDate = startDate
  for date, num in sorted(dates.iteritems()):
    currDate = datetime(date.year, date.month, date.day, date.hour, date.minute)
    lastDate += timedelta(minutes=2)
    while lastDate < currDate:
      lastDate += timedelta(minutes=2)
      if pos == 0:
        series["data"].append(aggNum / 30)
        aggNum = 0
      pos = (pos + 1) % scale

    aggNum += num
    if pos == 0:
      series["data"].append(aggNum / 30)
      aggNum = 0
    pos = (pos + 1) % scale
  data.append(series)
filename = "%s/stats/bycountryday.json" % webDir
tmpname = "%s/stats/bycountryday.%d.tmp" % (webDir, os.getpid())
with open(tmpname, 'w') as tf:
  json.dump(data, tf)
os.rename(tmpname, filename)

# Players by Mod
players = OrderedDict()
startDate = None
with open('%s/status/csv/bymod' % webDir) as f:
  for line in f:
    tokens = line.rstrip('\n').split(',')
    date = datetime.strptime(tokens[0], '%Y-%m-%d %H:%M')
    if not startDate:
      startDate = date
    for token in tokens[1:]:
      sn = token.split(':')
      if sn[0] not in players:
        players[sn[0]] = {}
      players[sn[0]][date] = int(sn[1])

scale = 30
data = []
for server, dates in players.iteritems():
  series = {"name": server, "pointInterval": scale * 2 * 60 * 1000, "pointStart": int(startDate.strftime("%s")) * 1000, "data": []}
  n = ""
  pos = 1
  aggNum = 0
  lastDate = startDate
  for date, num in sorted(dates.iteritems()):
    currDate = datetime(date.year, date.month, date.day, date.hour, date.minute)
    lastDate += timedelta(minutes=2)
    while lastDate < currDate:
      lastDate += timedelta(minutes=2)
      if pos == 0:
        series["data"].append(aggNum)
        aggNum = 0
      pos = (pos + 1) % scale

    if num > aggNum:
      aggNum = num
    if pos == 0:
      series["data"].append(aggNum)
      aggNum = 0
    pos = (pos + 1) % scale
  data.append(series)
filename = "%s/stats/bymod.json" % webDir
tmpname = "%s/stats/bymod.%d.tmp" % (webDir, os.getpid())
with open(tmpname, 'w') as tf:
  json.dump(data, tf)
os.rename(tmpname, filename)

scale = 720
data = []
for server, dates in players.iteritems():
  series = {"name": server, "pointInterval": scale * 2 * 60 * 1000, "pointStart": int(startDate.strftime("%s")) * 1000, "data": []}
  n = ""
  pos = 1
  aggNum = 0
  lastDate = startDate
  for date, num in sorted(dates.iteritems()):
    currDate = datetime(date.year, date.month, date.day, date.hour, date.minute)
    lastDate += timedelta(minutes=2)
    while lastDate < currDate:
      lastDate += timedelta(minutes=2)
      if pos == 0:
        series["data"].append(aggNum / 30)
        aggNum = 0
      pos = (pos + 1) % scale

    aggNum += num
    if pos == 0:
      series["data"].append(aggNum / 30)
      aggNum = 0
    pos = (pos + 1) % scale
  data.append(series)
filename = "%s/stats/bymodday.json" % webDir
tmpname = "%s/stats/bymodday.%d.tmp" % (webDir, os.getpid())
with open(tmpname, 'w') as tf:
  json.dump(data, tf)
os.rename(tmpname, filename)

otherIncludes = '''<script type="text/javascript" src="js/jquery.min.js"></script>
<script type="text/javascript" src="js/charts.js"></script>'''

menu = """<ul>
  <li><a href="/stats/">Player Statistics</a></li>
  <li><a href="/stats/maps/">Map Statistics</a></li>
  <li><a href="/stats/server/">Server Statistics</a></li>
  <li><a href="https://steamdb.info/app/412220/graphs/">SteamDB</a></li>
</ul>"""
text = header("Statistics & Charts", menu, "", False, False, otherIncludes)

with open('scripts/stats.html') as f:
  text += f.read()

tableCountries = ""
sumPlayersDay = 0
sumPlayersLastDay = 0
sumPlayersWeek = 0
sumPlayersLastWeek = 0
for server, avgDay in sorted(countryAveragesDay.items(), key=lambda x: -x[1]):
    playersDay = 0 if numElementsDay == 0 else float(avgDay) / float(numElementsDay)
    sumPlayersDay += playersDay
    playersWeek = 0 if numElementsWeek == 0 else float(countryAverages.get(server, 0)) / float(numElementsWeek)
    sumPlayersWeek += playersWeek
    playersLastWeek = 0 if numElementsLastWeek == 0 else float(countryAveragesLastWeek.get(server, 0)) / float(numElementsLastWeek)
    sumPlayersLastWeek += playersLastWeek
    playersLastDay = 0 if numElementsLastDay == 0 else float(countryAveragesLastDay.get(server, 0)) / float(numElementsLastDay)
    sumPlayersLastDay += playersLastDay
    tableCountries += "<tr><td style=\"text-align: right;\"><strong>%s</strong></td><td style=\"text-align: right;\">%.2f</td><td style=\"text-align: right;\">%s</td><td style=\"text-align: right;\">%.2f</td><td style=\"text-align: right;\">%s</td><td style=\"text-align: right;\">%d&nbsp;at&nbsp;%s</td><td style=\"text-align: right;\">%s</td><td style=\"text-align: right;\"><a href=\"/ranks/%s/\">%s</a></td>\n" % (server, playersDay, changeStr(playersDay, playersLastDay), playersWeek, changeStr(playersWeek, playersLastWeek), countryRecords[server][0], countryRecords[server][1].replace(" ", "&nbsp;"), nrPlayers.get(server, 0), server.lower(), nrRanks.get(server, 0))
# Total
tableCountries += "<tr style=\"border-top: .5em solid transparent;\"><td style=\"text-align: right;\"><strong>Total</strong></td><td style=\"text-align: right;\">%.2f</td><td style=\"text-align: right;\">%s</td><td style=\"text-align: right;\">%.2f</td><td style=\"text-align: right;\">%s</td><td style=\"text-align: right;\"><a href=\"2954/\">%d&nbsp;at&nbsp;%s</a></td><td style=\"text-align: right;\"><a href=\"/players/\">%s</a></td><td style=\"text-align: right;\"><a href=\"/ranks/\">%s</a></td>" % (sumPlayersDay, changeStr(sumPlayersDay, sumPlayersLastDay), sumPlayersWeek, changeStr(sumPlayersWeek, sumPlayersLastWeek), countryRecords["Total"][0], countryRecords["Total"][1].replace(" ", "&nbsp;"), nrPlayers["Total"], nrRanks["Total"])

print text % (tableCountries, tableTypes)

print """<p class="toggle">Refreshed: %s</p>
</section>
</article>
</body>
</html>""" % strftime("%Y-%m-%d %H:%M")

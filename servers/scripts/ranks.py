#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from ddnet import *
from watchlinks import watchLinks
import sys
import os
import sqlite3
from html import escape
from urllib.parse import quote_plus
from datetime import datetime, timedelta
from collections import defaultdict
import msgpack
import traceback
from time import strftime
from contextlib import nullcontext

def printFooter():
  generatedTime = strftime("%Y-%m-%d %H:%M:%S")
  return """
  <div id="points" class="block div-ranks">
    <div class="back-up"><a href="#top">&#8593;</a></div>
    <h2>Points Calculation</h2>
    <div class="block2">
      <h3>Points</h3>
      <p>
        You earn points for finishing a map you've never finished before. Every map has a difficulty indicated by its <strong>stars</strong>. The servers have the following <strong>multiplier</strong>s and <strong>offset</strong>s:
      </p>
      <table style="width: 100%%;">
        <tr>
          <th>Server Type</th>
          <th class="multiplier">Multiplier</th>
          <th class="multiplier">Offset</th>
        </tr><tr>
          <td>Novice</td>
          <td class="multiplier">1</td>
          <td class="multiplier">0</td>
        </tr><tr>
          <td>Moderate</td>
          <td class="multiplier">2</td>
          <td class="multiplier">5</td>
        </tr><tr>
          <td>Brutal</td>
          <td class="multiplier">3</td>
          <td class="multiplier">15</td>
        </tr><tr>
          <td>Insane</td>
          <td class="multiplier">4</td>
          <td class="multiplier">30</td>
        </tr><tr>
          <td>Dummy</td>
          <td class="multiplier">5</td>
          <td class="multiplier">5</td>
        </tr><tr>
          <td>DDmaX.*</td>
          <td class="multiplier">4</td>
          <td class="multiplier">0</td>
        </tr><tr>
        </tr><tr>
          <td>Event</td>
          <td class="multiplier">4</td>
          <td class="multiplier">0</td>
        </tr><tr>
          <td>Oldschool</td>
          <td class="multiplier">6</td>
          <td class="multiplier">0</td>
        </tr><tr>
          <td>Solo</td>
          <td class="multiplier">4</td>
          <td class="multiplier">0</td>
        </tr>
        </tr><tr>
          <td>Race</td>
          <td class="multiplier">2</td>
          <td class="multiplier">0</td>
        </tr>
      </table>
      <p>
        The points you earned for a map are calculated as follows:
      </p>
      <math>
          <mrow>
              <mi>points</mi><mo>=</mo><mi>stars</mi><mo>×</mo><mi>multiplier</mi><mo>+</mo><mi>offset</mi>
          </mrow>
      </math>
    </div>
    <div class="block2">
      <h3>Team Rank</h3>
      <p>
        Join team <strong>x</strong> using <strong>/team x</strong> and finish in it to earn a team record. The global and server wide team ranks are calculated from your team ranks:
      </p>
      <table class="points">
        <tr><td>1st place</td><td>25 points</td></tr>
        <tr><td>2nd place</td><td>18 points</td></tr>
        <tr><td>3rd place</td><td>15 points</td></tr>
        <tr><td>4th place</td><td>12 points</td></tr>
        <tr><td>5th place</td><td>10 points</td></tr>
        <tr><td>6th place</td><td>8 points</td></tr>
        <tr><td>7th place</td><td>6 points</td></tr>
        <tr><td>8th place</td><td>4 points</td></tr>
        <tr><td>9th place</td><td>2 points</td></tr>
        <tr><td>10th place</td><td>1 point</td></tr>
      </table>
    </div>
    <div class="block2">
      <h3>Rank</h3>
      <p>
        Finish a map, no matter in which team, to earn a record. The global and server wide ranks are calculated from your ranks:
      </p>
      <table class="points">
        <tr><td>1st place</td><td>25 points</td></tr>
        <tr><td>2nd place</td><td>18 points</td></tr>
        <tr><td>3rd place</td><td>15 points</td></tr>
        <tr><td>4th place</td><td>12 points</td></tr>
        <tr><td>5th place</td><td>10 points</td></tr>
        <tr><td>6th place</td><td>8 points</td></tr>
        <tr><td>7th place</td><td>6 points</td></tr>
        <tr><td>8th place</td><td>4 points</td></tr>
        <tr><td>9th place</td><td>2 points</td></tr>
        <tr><td>10th place</td><td>1 point</td></tr>
      </table>
    </div>
    <br/>
  </div>
  <p class="toggle">Refreshed: <span data-type="date" data-date="%s" data-datefmt="datetime">%s</span></p>
  </section>
  </article>
  %s
  </body>
</html>""" % (generatedTime, generatedTime, printDateTimeScript())

con = mysqlConnect()
# Every rank that has a pre-generated demo, loaded once for all map sections
watchable = watchLinks()

rankLadder = defaultdict(int)
teamrankLadder = defaultdict(int)
pointsLadder = defaultdict(int)
weeklyPointsLadder = defaultdict(int)
monthlyPointsLadder = defaultdict(int)
yearlyPointsLadder = defaultdict(int)
players = {}
maps = {}
totalPoints = 0
serverRanks = {}
recordsFile = '/home/teeworlds/servers/players-records.db'
if sys.argv[1].startswith("--country="):
  country = sys.argv[1][10:]
  types = sys.argv[2:]
  if country == "OLD": # Old ranks had no country
    mbCountry = "and Server = \"\""
    mbCountry2 = "where Server = \"\""
  else:
    mbCountry = "and Server like \"%s%%%%\"" % country
    mbCountry2 = "where Server like \"%s%%%%\"" % country
else:
  country = None
  types = sys.argv[1:]
  mbCountry = ""
  mbCountry2 = ""
mbCountryInput = ('<input name="country" type="hidden" value="%s">' % country) if country else ''
mbCountryQuery = ("&country=" + country) if country else ''

menuText = '<ul>'
menuText += '<li><a href="/ranks/">Global Ranks</a> ('
for i, c in enumerate(countries):
  if i > 0:
    menuText += ', '
  menuText += '<a href="/ranks/%s/">%s</a>' % (c.lower(), c)
menuText += ')'
menuText += '</li>'
for type in types:
  if country == None:
    menuText += '<li><a href="/ranks/%s/">%s Server</a></li>\n' % (type.lower(), type)
  else:
    menuText += '<li><a href="/ranks/%s/%s/">%s %s Server</a></li>\n' % (country.lower(), type.lower(), country, type)
menuText += '<li><a href="#points">Points Calculation</a></li>\n'
menuText += '</ul>'

# mysqlclient 2.x (py3) dropped the Connection context-manager protocol that
# py2 MySQLdb had. The block below is read-only, so keep the implicit single
# transaction open for a consistent snapshot (matching the old `with con:`).
with nullcontext():
  cur = con.cursor()
  cur.execute("set names 'utf8mb4';")
  cur.execute("SET SESSION max_statement_time=0")  # batch job: allow long queries (global 60s net stays for web/game)
  #cur.execute("set profiling = 1;")

  # Map release dates fetched once for all maps (record_maps is tiny) instead of
  # one query per map. Replaces the per-map "select DATE_FORMAT(...) from record_maps".
  releasedByMap = {}
  cur.execute("select Map, DATE_FORMAT(Timestamp, '%Y-%m-%d') from record_maps;")
  for r in cur.fetchall():
    releasedByMap[r[0]] = r[1]

  # Per-(player, map) records are streamed to a temp sqlite instead of held in a
  # 30 GB in-memory dict; players-cache.py reads it sorted by player to build the
  # diskcache. Only the global (country=None) run produces the players-cache.
  recdb = None
  # Set True if any per-map records query fails (e.g. DB timeout). players-cache.py
  # only prunes stale players when the run was complete, so a partial run can't
  # empty the cache by deleting players whose queries happened to fail.
  incomplete = False
  if country == None:
    recordsTmp = recordsFile + '.tmp'
    recdb = sqlite3.connect(recordsTmp)
    recdb.execute("PRAGMA journal_mode=OFF")
    recdb.execute("PRAGMA synchronous=OFF")
    recdb.execute("DROP TABLE IF EXISTS records")
    recdb.execute("CREATE TABLE records (player TEXT, mapname TEXT, teamrank INT, rnk INT, finishes INT, firstfinish TEXT, time REAL, server TEXT)")
    reccur = recdb.cursor()

  for type in types:
    serversString1 = ""
    serversString2 = ""
    totalServerPoints = 0
    serverRankLadder = defaultdict(int)
    serverTeamrankLadder = defaultdict(int)
    serverPointsLadder = defaultdict(int)
    weeklyServerPointsLadder = defaultdict(int)
    monthlyServerPointsLadder = defaultdict(int)
    yearlyServerPointsLadder = defaultdict(int)

    f = open("types/%s/maps" % type.lower(), 'r', encoding='utf-8')

    serversString1 += '<div id="%s" class="longblock div-ranks">\n' % type
    serversString1 += '<div class="right"><form id="mapform" action="/maps/" method="get">%s<input name="map" class="typeahead" type="text" placeholder="Map search"><input type="submit" value="Map search" style="position: absolute; left: -9999px"></form><br><form id="mapperform" action="/maps/" method="get"><input id="mappersearch" name="mapper" class="typeahead" type="text" placeholder="Mapper search"><input type="submit" value="Mapper search" style="position: absolute; left: -9999px"></form><br><form id="playerform" action="/players/" method="get"><input name="player" class="typeahead" type="text" placeholder="Player search"><input type="submit" value="Player search" style="position: absolute; left: -9999px"></form></div>' % mbCountryInput
    serversString1 += '<script src="/jquery.js" type="text/javascript"></script>\n'
    serversString1 += '<script src="/typeahead.bundle.js" type="text/javascript"></script>\n'
    serversString1 += '<script src="/mapsearch.js" type="text/javascript"></script>\n'
    serversString1 += '<script src="/mappersearch.js" type="text/javascript"></script>\n'
    serversString1 += '<script src="/playersearch.js?version=2" type="text/javascript"></script>\n'
    if country == None:
      serversString1 += '<div class="block7"><h2>%s Server Ranks%%s</h2></div><br/>\n' % type
    else:
      serversString1 += '<div class="block7"><h2>%s %s Server Ranks%%s</h2></div><br/>\n' % (country, type)

    mapsStrings = ['']
    currentMapCount = 0
    subname = None
    maps[type] = []
    firstLine = True

    for line in f:
      if line.startswith('───') and line.endswith('───\n'):
        subname = line.lstrip('─ ').rstrip('\n─ ')
        if mapsStrings[-1] != '':
          mapsStrings[-1] += '<br/></div>\n'
        mapsStrings[-1] += '<div class="longblock div-ranks"><h2 id="%s">%s</h2><br/>\n' % (subname.lower().replace(' ', '-'), titleSubtype(subname))
        continue
      words = line.rstrip('\n').split('|')
      if len(words) == 0 or not words[0].isdigit():
        continue

      if not subname and firstLine:
        mapsStrings[-1] += '<div class="longblock div-ranks">\n'
        firstLine = False

      # paginate
      if currentMapCount > 25:
        if subname:
            mapsStrings.append('<div class="longblock div-ranks"><h2 id="%s">%s</h2><br/>\n' % (subname.lower().replace(' ', '-'), titleSubtype(subname)))
        else:
            mapsStrings.append('<div class="longblock div-ranks">\n')
        currentMapCount = 0
      currentMapCount += 1

      stars = int(words[0])

      totalPoints += globalPoints(type, stars)
      totalServerPoints += globalPoints(type, stars)

      originalMapName = words[1]
      if len(words) > 2:
        mapperName = words[2]
      else:
        mapperName = ""

      mapName = normalizeMapname(originalMapName)

      rows = []
      teamRanks = []
      namesOnMap = {}
      names = []
      time = 0
      currentRank = 1
      currentPosition = 1
      countTeamFinishes = 0
      skips = 1
      mapMaps = {}
      mapServers = {}

      try:
        if country == None:
          cur.execute("select distinct r.Name, r.ID, r.Time, r.Timestamp, (select substring(Server, 1, 3) from record_race where Map = r.Map and Name = r.Name and Time = r.Time limit 1) as Server, r.GameID from ((select distinct ID from record_teamrace where Map = '%s' ORDER BY Time) as l) left join (select * from record_teamrace where Map = '%s') as r on l.ID = r.ID order by r.Time, r.ID, r.Name;" % (con.escape_string(originalMapName).decode("utf-8"), con.escape_string(originalMapName).decode("utf-8")))
        else:
          cur.execute("select distinct r.Name, r.ID, r.Time, r.Timestamp, n.Server, r.GameID from ((select distinct ID from record_teamrace where Map = '%s' ORDER BY Time) as l) left join (select * from record_teamrace where Map = '%s') as r on l.ID = r.ID inner join ((select distinct Map, Name, Time, SUBSTRING(Server, 1, 3) as Server from record_race %s) as n) on r.Map = n.Map and r.Name = n.Name and r.Time = n.Time order by r.Time, r.ID, r.Name;" % (con.escape_string(originalMapName).decode("utf-8"), con.escape_string(originalMapName).decode("utf-8"), mbCountry2))
        rows = cur.fetchall()
      except:
        incomplete = True
        traceback.print_exc()
      if len(rows) > 0:
        ID = rows[0][1]

      for row in rows:
        if row[1] != ID:
          if currentPosition <= 10:
            fNames = []
            for name in names:
              fNames.append('<a href="%s">%s</a>' % (escape(playerWebsite(u'%s' % name)), escape(name)))
            teamRanks.append((currentRank, joinNames(fNames), time, timestamp, foundCountry, foundGameId))
            names = []

          countTeamFinishes += 1
          if row[2] != time:
            time = row[2]
            timestamp = row[3]
            currentRank += skips
            skips = 1
          else:
            skips += 1
          currentPosition += 1
          ID = row[1]

        if row[0] not in players:
          players[row[0]] = Player({}, {})
        if row[0] not in mapMaps:
          mapMaps[row[0]] = PlayerMap(currentRank, 0, 0, "2030-10-10 00:00:00", 0.0)

        if currentPosition <= 10:
          time = row[2]
          timestamp = row[3]
          names.append(row[0])
          foundCountry = row[4] if row[4] else 'UNK'
          foundGameId = row[5]

        if currentRank <= 10 and row[0] not in namesOnMap:
          namesOnMap[row[0]] = True

          if type != "Fun":
            teamrankLadder[row[0]] += points(currentRank)
            serverTeamrankLadder[row[0]] += points(currentRank)


      if currentPosition <= 10 and time > 0:
        fNames = []
        for name in names:
          fNames.append('<a href="%s">%s</a>' % (escape(playerWebsite(u'%s' % name)), escape(name)))
        teamRanks.append((currentRank, joinNames(fNames), time, timestamp, foundCountry, foundGameId))

      if time > 0:
        countTeamFinishes += 1

      rows = []
      ranks = []
      countFinishes = 0

      try:
        cur.execute("select l.Name, minTime, l.Timestamp, playCount, minTimestamp, l.Server, l.GameID from (select * from record_race where Map = '%s' %s) as l JOIN (select Name, min(Time) as minTime, count(*) as playCount, min(Timestamp) as minTimestamp from record_race where Map = '%s' %s group by Name order by minTime ASC) as r on l.Time = r.minTime and l.Name = r.Name GROUP BY Name ORDER BY minTime, l.Name;" % (con.escape_string(originalMapName).decode("utf-8"), mbCountry, con.escape_string(originalMapName).decode("utf-8"), mbCountry))
        rows = cur.fetchall()
      except:
        incomplete = True
        traceback.print_exc()

      countFinishes = len(rows)
      maps[type].append(Map(originalMapName, globalPoints(type, stars), countFinishes))

      currentRank = 0
      currentPosition = 0
      lastTime = 0
      skips = 1

      for row in rows:
        if row[1] != lastTime:
          lastTime = row[1]
          currentRank += skips
          skips = 1
        else:
          skips += 1

        currentPosition += 1

        pointsLadder[row[0]] += globalPoints(type, stars)
        serverPointsLadder[row[0]] += globalPoints(type, stars)

        if datetime.now() - timedelta(days=7) <= row[4]:
          weeklyPointsLadder[row[0]] += globalPoints(type, stars)
          weeklyServerPointsLadder[row[0]] += globalPoints(type, stars)

        if datetime.now() - timedelta(days=30) <= row[4]:
          monthlyPointsLadder[row[0]] += globalPoints(type, stars)
          monthlyServerPointsLadder[row[0]] += globalPoints(type, stars)

        if datetime.now() - timedelta(days=365) <= row[4]:
          yearlyPointsLadder[row[0]] += globalPoints(type, stars)
          yearlyServerPointsLadder[row[0]] += globalPoints(type, stars)

        if row[0] not in players:
          players[row[0]] = Player({}, {})
        if row[0] not in mapMaps:
          mapMaps[row[0]] = PlayerMap(0, currentRank, row[3], row[4], row[1])
        else:
          mapMaps[row[0]] = PlayerMap(mapMaps[row[0]][0], currentRank, row[3], row[4], row[1])
        mapServers[row[0]] = row[5]

        if row[5] != None:
          if row[5] not in players[row[0]].servers:
            players[row[0]].servers[row[5]] = 1
          else:
            players[row[0]].servers[row[5]] += 1

        if currentPosition <= 10:
          ranks.append((currentRank, row[0], row[1], row[2], row[3], row[5] if row[5] else 'UNK', row[6]))
        if currentRank <= 10 and type != "Fun":
          rankLadder[row[0]] += points(currentRank)
          serverRankLadder[row[0]] += points(currentRank)

      # Stream this map's per-player records to the temp store (global run only).
      if country == None:
        reccur.executemany("INSERT INTO records VALUES (?,?,?,?,?,?,?,?)",
          [(p, originalMapName, pm[0], pm[1], pm[2], str(pm[3]), pm[4], mapServers.get(p)) for p, pm in mapMaps.items()])

      if countTeamFinishes == 1:
        mbS = ""
      else:
        mbS = "s"

      if countFinishes == 1:
        mbS2 = ""
      else:
        mbS2 = "s"

      avgTime = ""
      finishTimes = ""

      if countFinishes:
        try:
          cur.execute("select (select median(Time) over (partition by Map) from record_race where Map = '%s' %s limit 1), min(Timestamp), max(Timestamp) from record_race where Map = '%s' %s;" % (con.escape_string(originalMapName).decode("utf-8"), mbCountry, con.escape_string(originalMapName).decode("utf-8"), mbCountry))
          rows = cur.fetchall()
          avgTime = " (median time: %s)" % formatTime(rows[0][0])
          finishTimes = "first finish: %s, last finish: %s" % (escape(formatDate(rows[0][1])), escape(formatDate(rows[0][2])))
        except:
          pass

      biggestTeam = ""

      try:
        if country == None:
          cur.execute("select count(Name) from record_teamrace where Map = '%s' group by ID order by count(Name) desc limit 1;" % con.escape_string(originalMapName).decode("utf-8"))
        else:
          cur.execute("select count(record_teamrace.Name) from (record_teamrace join record_race on record_teamrace.Map = record_race.Map and record_teamrace.Name = record_race.Name and record_teamrace.Time = record_race.Time) where record_teamrace.Map = '%s' %s group by ID order by count(record_teamrace.Name) desc limit 1;" % (con.escape_string(originalMapName).decode("utf-8"), mbCountry))
        rows = cur.fetchall()
        biggestTeam = " (biggest team: %d)" % rows[0][0]
      except:
        pass

      if not mapperName:
        mbMapperName = ""
      else:
        names = splitMappers(mapperName)
        newNames = []
        for name in names:
          newNames.append('<a href="%s">%s</a>' % (mapperWebsite(name), escape(name)))

        mbMapperName = "<strong>by %s</strong><br/>" % makeAndString(newNames)

      formattedMapName = escape(originalMapName)
      mbMapInfo = ""
      try:
        with open('maps/%s.msgpack' % originalMapName, 'rb') as inp:
          unpacker = msgpack.Unpacker(inp)
          width = unpacker.unpack()
          height = unpacker.unpack()
          tiles = unpacker.unpack()

          formattedMapName = '<span title="Map size: %dx%d">%s</span>' % (width, height, escape(originalMapName))

          mbMapInfo = "<br/>"
          for tile in sorted(tiles.keys(), key=lambda i:order(i)):
            mbMapInfo += tileHtml(tile)
      except IOError:
        traceback.print_exc()

      mbReleased = ""
      if originalMapName in releasedByMap:
        released = releasedByMap[originalMapName]
        if released != "0000-00-00":
          mbReleased = "Released: %s<br/>" % released

      if type == "Solo" or type == "Race" or type == "Dummy":
        mapsStrings[-1] += u'<div class="block2 info" id="map-%s"><h3 class="inline"><a href="%s">%s</a></h3><p class="inline">%s</p><p>%sDifficulty: %s, Points: %d<br/><a href="/mappreview/?map=%s"><img class="screenshot" alt="Screenshot" src="/ranks/maps/%s.png" width="360" height="225" /></a>%s<br/><span title="%s">%d tee%s finished%s</span></p></div>\n' % (escape(mapName), mapWebsite(originalMapName, country), formattedMapName, mbMapperName, mbReleased, escape(renderStars(stars)), globalPoints(type, stars), quote_plus(originalMapName), escape(mapName), mbMapInfo, finishTimes, countFinishes, mbS2, escape(avgTime))
        mapsStrings[-1] += printExactSoloRecords("Records", "records", ranks, not country, watchable.get((originalMapName, 'solo')))
      else:
        mapsStrings[-1] += u'<div class="block2 info" id="map-%s"><h3 class="inline"><a href="%s">%s</a></h3><p class="inline">%s</p><p>%sDifficulty: %s, Points: %d<br/><a href="/mappreview/?map=%s"><img class="screenshot" alt="Screenshot" src="/ranks/maps/%s.png" width="360" height="225" /></a>%s<br/><span title="%s">%d tee%s finished%s</span><br/>%d team%s finished%s</p></div>\n' % (escape(mapName), mapWebsite(originalMapName, country), formattedMapName, mbMapperName, mbReleased, escape(renderStars(stars)), globalPoints(type, stars), quote_plus(originalMapName), escape(mapName), mbMapInfo, finishTimes, countFinishes, mbS2, escape(avgTime), countTeamFinishes, mbS, escape(biggestTeam))
        mapsStrings[-1] += printTeamRecords("Team Records", "teamrecords", teamRanks, not country, watchable.get((originalMapName, 'team')))
        mapsStrings[-1] += printSoloRecords("Records", "records", ranks, not country, watchable.get((originalMapName, 'solo')))
      mapsStrings[-1] += '<br/>\n'

    serverPointsRanks = sorted(serverPointsLadder.items(), key=lambda r: r[1], reverse=True)
    weeklyServerPointsRanks = sorted(weeklyServerPointsLadder.items(), key=lambda r: r[1], reverse=True)
    monthlyServerPointsRanks = sorted(monthlyServerPointsLadder.items(), key=lambda r: r[1], reverse=True)
    yearlyServerPointsRanks = sorted(yearlyServerPointsLadder.items(), key=lambda r: r[1], reverse=True)
    serverTeamrankRanks = sorted(serverTeamrankLadder.items(), key=lambda r: r[1], reverse=True)
    serverRankRanks = sorted(serverRankLadder.items(), key=lambda r: r[1], reverse=True)

    serverRanks[type] = (totalServerPoints, serverPointsRanks, serverTeamrankRanks, serverRankRanks)

    serversString2 = printLadder("Points (%d total)" % totalServerPoints, serverPointsRanks, players, not country)
    if type != "Solo" and type != "Race" and type != "Dummy":
      serversString2 += printLadder("Team Rank", serverTeamrankRanks, players, not country)
    serversString2 += printLadder("Rank", serverRankRanks, players, not country)
    serversString2 += '<br/>'

    lastString = ""
    cur.execute("select * from (select l.Timestamp, l.Map, Name, Time, l.Server, record_maps.Server as Type from (select Timestamp, Map, Name, Time, Server from record_race %s) as l inner join record_maps on l.Map = record_maps.Map) as r where Type = '%s' and Timestamp > '%s' order by Timestamp desc limit 500;" % (mbCountry2, type, formatDate(datetime.now() - timedelta(days=7))))
    rows = cur.fetchall()

    lastString = '<div class="block4"><h3>Latest Finishes <button style="display: inline-block; margin-left: 10px;" id="play-button">⏸︎</button></h3><table class="tight" id="last-finishes">'

    for i, row in enumerate(rows):
      lastString += '<tr>' if i < 10 else '<tr class="allPoints" style="display: none">'
      dateWithTz = escape(formatDateTimeTz(row[0]))
      if country:
        lastString += '<td><span data-type="date" data-date="%s" data-datefmt="time" title="%s">%s</span>: <a href="%s">%s</a> by <a href="%s">%s</a> (%s)</td></tr>' % (dateWithTz, escape(formatDate(row[0])), escape(formatDateShort(row[0])), mapWebsite(row[1], country), escape(row[1]), escape(playerWebsite(row[2])), escape(row[2]), escape(formatTime(row[3])))
      else:
        lastString += '<td><span data-type="date" data-date="%s" data-datefmt="time" title="%s">%s</span>: <img src="/countryflags/%s.png" alt="%s" height="15"/> <a href="%s">%s</a> by <a href="%s">%s</a> (%s)</td></tr>' % (dateWithTz, escape(formatDate(row[0])), escape(formatDateShort(row[0])), row[4], row[4], mapWebsite(row[1], country), escape(row[1]), escape(playerWebsite(row[2])), escape(row[2]), escape(formatTime(row[3])))

    lastString += '</table></div><br/>'
    lastString += '''<script>
  function updateLastFinishes(finishes) {
      const tbody = document.querySelector('#last-finishes tbody');

      tbody.innerHTML = '';

      finishes.forEach(finish => {
        const row = document.createElement('tr');
        const date = new Date(finish.timestamp * 1000);
        const time = Number(finish.time);
        const seconds = Math.floor(time %% 60);
        const minutes = Math.floor((time %% 3600) / 60);
        const hours = Math.floor(time / 3600);
        const finishTime = {
          hours: String(hours).padStart(2, '0'),
          minutes: String(minutes).padStart(2, '0'),
          seconds: String(seconds).padStart(2, '0'),
        }

        const cells = [
          `<td>
            <span data-type="date" data-date="${date}" data-datefmt="time" title="${date.toLocaleTimeString()}">${date.toLocaleTimeString()}</span>:
            <img src="/countryflags/${finish.server}.png" alt="${finish.server}" height="15">
            <a href="/maps/${finish.map}/">${finish.map}</a> by
            <a href="/players/${finish.name}/">${finish.name}</a>
            (${finishTime.hours > 0 ? `${finishTime.hours}:` : ''}${finishTime.minutes}:${finishTime.seconds})
          </td>`
        ];

        row.innerHTML = cells.join('');
        tbody.appendChild(row);
      });
    }


  async function fetchQueryResults() {
    try {
      const response = await fetch("/maps/?latest=1&server=%s%s");

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      const finishes = data?.slice(0,20) ?? [];
      updateLastFinishes(finishes);
    } catch (error) {
      console.error("Error fetching data:", error);
    }
  }

  let intervalId = setInterval(fetchQueryResults, 1000);

  fetchQueryResults();

  const playButton = document.querySelector('#play-button');


  playButton.addEventListener('click', () => {
    if (intervalId) {
      // Stop the interval
      clearInterval(intervalId);
      intervalId = null;
      playButton.textContent = '⏵︎';
    } else {
      // Start the interval
      fetchQueryResults();
      intervalId = setInterval(fetchQueryResults, 1000);
      playButton.textContent = '⏸︎';
    }
  });
</script>''' % (type, mbCountryQuery,)

    serversString2 += printLadder("Points (past 365 days)", yearlyServerPointsRanks, players, not country)
    serversString2 += printLadder("Points (past 30 days)", monthlyServerPointsRanks, players, not country)
    serversString2 += printLadder("Points (past 7 days)", weeklyServerPointsRanks, players, not country)
    serversString2 += lastString
    serversString2 += '</div>\n'

    for i, mapsString in enumerate(mapsStrings):
      if i == 0:
        if country == None:
          filename = "%s/ranks/%s/index.html" % (webDir, type.lower())
          tmpname = "%s/ranks/%s/index.%d.tmp" % (webDir, type.lower(), os.getpid())
        else:
          filename = "%s/ranks/%s/%s/index.html" % (webDir, country.lower(), type.lower())
          tmpname = "%s/ranks/%s/%s/index.%d.tmp" % (webDir, country.lower(), type.lower(), os.getpid())
      else:
        if country == None:
          filename = "%s/ranks/%s/%d/index.html" % (webDir, type.lower(), i+1)
          tmpname = "%s/ranks/%s/%d/index.%d.tmp" % (webDir, type.lower(), i+1, os.getpid())
        else:
          filename = "%s/ranks/%s/%s/%d/index.html" % (webDir, country.lower(), type.lower(), i+1)
          tmpname = "%s/ranks/%s/%s/%d/index.%d.tmp" % (webDir, country.lower(), type.lower(), i+1, os.getpid())

      directory = os.path.dirname(filename)
      if not os.path.exists(directory):
        os.makedirs(directory)

      tf = open(tmpname, 'w', encoding='utf-8')

      mbPage = " (%d/%d)" % (i+1, len(mapsStrings)) if len(mapsStrings) > 1 else ""
      if country == None:
        print(header("%s Server Ranks%s - DDraceNetwork" % (type, mbPage), menuText, ""), file=tf)
      else:
        print(header("%s %s Server Ranks%s - DDraceNetwork" % (country, type, mbPage), menuText, ""), file=tf)
      print('<p class="toggle"><a href="#" onclick="showClass(\'allPoints\'); return false;">Top 500 / Top 10</a></p>', file=tf)

      print('<div id="serverranks" style="display: ">', file=tf)
      print(serversString1 % mbPage, file=tf)
      print(serversString2, file=tf)
      print('<div class="all-%s" style="display: ">\n' % type, file=tf)
      print(mapsString, file=tf)
      print('</div>\n', file=tf)
      print('</div>', file=tf)
      if len(mapsStrings) > 1:
        if country:
          baseLink = '/ranks/%s/%s/' % (country.lower(), type.lower())
        else:
          baseLink = '/ranks/%s/' % type.lower()
        print(printPagination(baseLink, i+1, len(mapsStrings)), file=tf)
      print(printFooter(), file=tf)

      tf.close()
      os.rename(tmpname, filename)

  lastString = ""
  cur.execute("select l.Timestamp, l.Map, Name, Time, l.Server, record_maps.Server from ((select * from record_race %s order by Timestamp desc limit 500) as l inner join record_maps on l.Map = record_maps.Map) order by Timestamp desc;" % mbCountry2)
  rows = cur.fetchall()

  lastString += '<div class="block4"><h3>Latest Finishes <button style="display: inline-block; margin-left: 10px;" id="play-button">⏸︎</button></h3><table class="tight" id="last-finishes">'

  for i, row in enumerate(rows):
    lastString += '<tr>' if i < 20 else '<tr class="allPoints" style="display: none">'
    dateWithTz = escape(formatDateTimeTz(row[0]))
    if country:
      lastString += '<td><span data-type="date" data-date="%s" data-datefmt="time" title="%s">%s</span>: <a href="%s/">%s</a>: <a href="%s">%s</a> by <a href="%s">%s</a> (%s)</td></tr>' % (dateWithTz, escape(formatDate(row[0])), escape(formatDateShort(row[0])), row[5].lower(), row[5], mapWebsite(row[1], country), escape(row[1]), escape(playerWebsite(row[2])), escape(row[2]), escape(formatTime(row[3])))
    else:
      lastString += '<td><span data-type="date" data-date="%s" data-datefmt="time" title="%s">%s</span>: <img src="/countryflags/%s.png" alt="%s" height="15"/> <a href="%s/">%s</a>: <a href="%s">%s</a> by <a href="%s">%s</a> (%s)</td></tr>' % (dateWithTz, escape(formatDate(row[0])), escape(formatDateShort(row[0])), row[4], row[4], row[5].lower(), row[5], mapWebsite(row[1], country), escape(row[1]), escape(playerWebsite(row[2])), escape(row[2]), escape(formatTime(row[3])))

  lastString += '</table></div><br/>'
  lastString += '''<script>
  function updateLastFinishes(finishes) {
      const tbody = document.querySelector('#last-finishes tbody');

      tbody.innerHTML = '';

      finishes.forEach(finish => {
        const row = document.createElement('tr');
        const date = new Date(finish.timestamp * 1000);
        const time = Number(finish.time);
        const seconds = Math.floor(time %% 60);
        const minutes = Math.floor((time %% 3600) / 60);
        const hours = Math.floor(time / 3600);
        const finishTime = {
          hours: String(hours).padStart(2, '0'),
          minutes: String(minutes).padStart(2, '0'),
          seconds: String(seconds).padStart(2, '0'),
        }

        const cells = [
          `<td>
            <span data-type="date" data-date="${date}" data-datefmt="time" title="${date.toLocaleTimeString()}">${date.toLocaleTimeString()}</span>:
            <img src="/countryflags/${finish.server}.png" alt="${finish.server}" height="15">
            <a href="/maps/${finish.map}/">${finish.map}</a> by
            <a href="/players/${finish.name}/">${finish.name}</a>
            (${finishTime.hours > 0 ? `${finishTime.hours}:` : ''}${finishTime.minutes}:${finishTime.seconds})
          </td>`
        ];

        row.innerHTML = cells.join('');
        tbody.appendChild(row);
      });
    }


  async function fetchQueryResults() {
    try {
      const response = await fetch("/maps/?latest=1%s");

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      const finishes = data?.slice(0,20) ?? [];
      updateLastFinishes(finishes);
    } catch (error) {
      console.error("Error fetching data:", error);
    }
  }

  let intervalId = setInterval(fetchQueryResults, 1000);

  fetchQueryResults();

  const playButton = document.querySelector('#play-button');


  playButton.addEventListener('click', () => {
    if (intervalId) {
      // Stop the interval
      clearInterval(intervalId);
      intervalId = null;
      playButton.textContent = '⏵︎';
    } else {
      // Start the interval
      fetchQueryResults();
      intervalId = setInterval(fetchQueryResults, 1000);
      playButton.textContent = '⏸︎';
    }
  });
</script>''' % (mbCountryQuery,)

  #cur.execute('show profiles')
  #for row in cur:
  #  print(row)

pointsRanks = sorted(pointsLadder.items(), key=lambda r: r[1], reverse=True)
del pointsLadder
weeklyPointsRanks = sorted(weeklyPointsLadder.items(), key=lambda r: r[1], reverse=True)
del weeklyPointsLadder
monthlyPointsRanks = sorted(monthlyPointsLadder.items(), key=lambda r: r[1], reverse=True)
del monthlyPointsLadder
yearlyPointsRanks = sorted(yearlyPointsLadder.items(), key=lambda r: r[1], reverse=True)
del yearlyPointsLadder
teamrankRanks = sorted(teamrankLadder.items(), key=lambda r: r[1], reverse=True)
del teamrankLadder
rankRanks = sorted(rankLadder.items(), key=lambda r: r[1], reverse=True)
del rankLadder

if country == None:
  filename = "%s/ranks/index.html" % webDir
  tmpname = "%s/ranks/index.%d.tmp" % (webDir, os.getpid())
else:
  filename = "%s/ranks/%s/index.html" % (webDir, country.lower())
  tmpname = "%s/ranks/%s/index.%d.tmp" % (webDir, country.lower(), os.getpid())
directory = os.path.dirname(filename)
if not os.path.exists(directory):
  os.makedirs(directory)

tf = open(tmpname, 'w', encoding='utf-8')

if country == None:
  print(header("Ranks - DDraceNetwork", menuText, ""), file=tf)
else:
  print(header("%s Ranks - DDraceNetwork" % country, menuText, ""), file=tf)
print('<p class="toggle"><a href="#" onclick="showClass(\'allPoints\'); return false;">Top 500 / Top 20</a></p>', file=tf)

print('<div id="global" class="block">\n', file=tf)
print('<div class="right"><form id="mapform" action="/maps/" method="get">%s<input name="map" class="typeahead" type="text" placeholder="Map search"><input type="submit" value="Map search" style="position: absolute; left: -9999px"></form><br><form id="mapperform" action="/maps/" method="get"><input id="mappersearch" name="mapper" class="typeahead" type="text" placeholder="Mapper search"><input type="submit" value="Mapper search" style="position: absolute; left: -9999px"></form><br><form id="playerform" action="/players/" method="get"><input name="player" class="typeahead" type="text" placeholder="Player search"><input type="submit" value="Player search" style="position: absolute; left: -9999px"></form></div>' % mbCountryInput, file=tf)
print('<script src="/jquery.js" type="text/javascript"></script>', file=tf)
print('<script src="/typeahead.bundle.js" type="text/javascript"></script>', file=tf)
print('<script src="/mapsearch.js" type="text/javascript"></script>', file=tf)
print('<script src="/mappersearch.js" type="text/javascript"></script>', file=tf)
print('<script src="/playersearch.js?version=2" type="text/javascript"></script>', file=tf)
if country == None:
  print('<div class="block7"><h2>Global Ranks</h2></div><br/>', file=tf)
else:
  print('<div class="block7"><h2>%s Ranks</h2></div><br/>' % country, file=tf)
print(printLadder("Points (%d total)" % totalPoints, pointsRanks, players, not country, 20), file=tf)
print(printLadder("Team Rank", teamrankRanks, players, not country, 20), file=tf)
print(printLadder("Rank", rankRanks, players, not country, 20), file=tf)
print('<br/>', file=tf)
print(printLadder("Points (past 365 days)", yearlyPointsRanks, players, not country, 20), file=tf)
print(printLadder("Points (past 30 days)", monthlyPointsRanks, players, not country, 20), file=tf)
print(printLadder("Points (past 7 days)", weeklyPointsRanks, players, not country, 20), file=tf)
print(lastString, file=tf)
print('</div>', file=tf)
print(printFooter(), file=tf)

tf.close()
os.rename(tmpname, filename)

if country == None:
  msgpackFile = '%s/players.msgpack' % webDir
  msgpackTmpFile = '%s.tmp' % msgpackFile
  with open(msgpackTmpFile, 'wb') as out:
    out.write(msgpack.packb(types))
    out.write(msgpack.packb(maps))
    out.write(msgpack.packb(totalPoints))
    out.write(msgpack.packb(pointsRanks))
    out.write(msgpack.packb(weeklyPointsRanks))
    out.write(msgpack.packb(monthlyPointsRanks))
    out.write(msgpack.packb(yearlyPointsRanks))
    out.write(msgpack.packb(teamrankRanks))
    out.write(msgpack.packb(rankRanks))
    out.write(msgpack.packb(serverRanks))
  os.rename(msgpackTmpFile, msgpackFile)

  # Finalize the records temp store (atomically); players-cache.py streams it
  # into the diskcache sorted by player, so nothing holds all players in memory.
  # user_version = 1 signals a complete run (all queries succeeded); players-cache.py
  # only prunes stale players when this is 1, so a partial run can't empty the cache.
  if incomplete:
    print("ranks.py: WARNING incomplete run (a records query failed); players-cache will NOT prune", file=sys.stderr)
  recdb.execute("PRAGMA user_version = %d" % (0 if incomplete else 1))
  recdb.commit()
  recdb.close()
  os.rename(recordsFile + '.tmp', recordsFile)

#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from ddnet import *
import sys
import os
from cgi import escape
from urllib import quote_plus
from datetime import datetime, timedelta
from collections import defaultdict
import msgpack
from diskcache import Cache
import traceback
from time import strftime

reload(sys)
sys.setdefaultencoding('utf8')

def printFooter():
  return """
  <div id="points" class="block div-ranks">
    <div class="back-up"><a href="#top">&#8593;</a></div>
    <h2>Points Calculation</h2>
    <div class="block2">
      <h3>Points</h3>
      <p>
        You earn points for finishing a map you've never finished before. Every map has a difficulty indicated by its <strong>stars</strong>. The servers have the following <strong>multiplier</strong>s and <strong>offset</strong>s:
      </p>
      <table>
        <tr>
          <th>Server Type</th>
          <th>Multiplier</th>
          <th>Offset</th>
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
          <td>DDmaX</td>
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
        <tr><td>10th place</td><td>1 points</td></tr>
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
        <tr><td>10th place</td><td>1 points</td></tr>
      </table>
    </div>
    <br/>
  </div>
  <p class="toggle">Refreshed: %s</p>
  </section>
  </article>
  </body>
</html>""" % strftime("%Y-%m-%d %H:%M")

con = mysqlConnect()

rankLadder = defaultdict(int)
teamrankLadder = defaultdict(int)
pointsLadder = defaultdict(int)
weeklyPointsLadder = defaultdict(int)
monthlyPointsLadder = defaultdict(int)
players = {}
maps = {}
totalPoints = 0
serverRanks = {}
if sys.argv[1].startswith("--country="):
  country = sys.argv[1][10:]
  types = sys.argv[2:]
  if country == "OLD": # Old ranks had no country
    mbCountry = "and Server = \"\""
    mbCountry2 = "where Server = \"\""
  else:
    mbCountry = "and Server = \"%s\"" % country
    mbCountry2 = "where Server = \"%s\"" % country
else:
  country = None
  types = sys.argv[1:]
  mbCountry = ""
  mbCountry2 = ""

menuText = '<ul>'
menuText += '<li><a href="/ranks/">Global Ranks</a> (<a href="/ranks/ger/">GER</a>, <a href="/ranks/fra/">FRA</a>, <a href="/ranks/rus/">RUS</a>, <a href="/ranks/irn/">IRN</a>, <a href="/ranks/chl/">CHL</a>, <a href="/ranks/bra/">BRA</a>, <a href="/ranks/zaf/">ZAF</a>, <a href="/ranks/usa/">USA</a>, <a href="/ranks/can/">CAN</a>, <a href="/ranks/chn/">CHN</a>, <a href="/ranks/old/">OLD</a>)</li>'
for type in types:
  if country == None:
    menuText += '<li><a href="/ranks/%s/">%s Server</a></li>\n' % (type.lower(), type)
  else:
    menuText += '<li><a href="/ranks/%s/%s/">%s %s Server</a></li>\n' % (country.lower(), type.lower(), country, type)
menuText += '<li><a href="#points">Points Calculation</a></li>\n'
menuText += '</ul>'

with con:
  cur = con.cursor()
  cur.execute("set names 'utf8mb4';")
  #cur.execute("set profiling = 1;")
  for type in types:
    if country == None:
      filename = "%s/ranks/%s/index.html" % (webDir, type.lower())
      tmpname = "%s/ranks/%s/index.%d.tmp" % (webDir, type.lower(), os.getpid())
    else:
      filename = "%s/ranks/%s/%s/index.html" % (webDir, country.lower(), type.lower())
      tmpname = "%s/ranks/%s/%s/index.%d.tmp" % (webDir, country.lower(), type.lower(), os.getpid())
    directory = os.path.dirname(filename)
    if not os.path.exists(directory):
      os.makedirs(directory)

    serversString = ""
    subserversString = ""
    totalServerPoints = 0
    serverRankLadder = defaultdict(int)
    serverTeamrankLadder = defaultdict(int)
    serverPointsLadder = defaultdict(int)
    weeklyServerPointsLadder = defaultdict(int)
    monthlyServerPointsLadder = defaultdict(int)

    f = open("types/%s/maps" % type.lower(), 'r')

    serversString += '<div id="%s" class="longblock div-ranks">\n' % type
    serversString += '<div id="remote" class="right"><form id="playerform" action="/players/" method="get"><input name="player" class="typeahead" type="text" placeholder="Player search"><input type="submit" value="Player search" style="position: absolute; left: -9999px"></form></div>\n'
    serversString += '<script src="/jquery.js" type="text/javascript"></script>\n'
    serversString += '<script src="/typeahead.bundle.js" type="text/javascript"></script>\n'
    serversString += '<script src="/playersearch.js" type="text/javascript"></script>\n'
    if country == None:
      serversString += '<div class="block7"><h2>%s Server Ranks</h2></div><br/>\n' % type
    else:
      serversString += '<div class="block7"><h2>%s %s Server Ranks</h2></div><br/>\n' % (country, type)

    mapsString = ""

    maps[type] = []

    for line in f:
      if line.startswith('───') and line.endswith('───\n'):
        subname = line.lstrip('─ ').rstrip('\n─ ')
        if mapsString != '':
          mapsString += '<br/></div>\n'
        mapsString += '<div class="longblock div-ranks"><h2 id="%s">%s</h2><br/>\n' % (subname.lower().replace(' ', '-'), titleSubtype(subname))
        continue

      words = line.rstrip('\n').split('|')
      if len(words) == 0 or not words[0].isdigit():
        continue

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

      try:
        if country == None:
          cur.execute("select Name, r.ID, Time, Timestamp from ((select distinct ID from record_teamrace where Map = '%s' ORDER BY Time) as l) left join (select * from record_teamrace where Map = '%s') as r on l.ID = r.ID order by r.Time, r.ID, Name;" % (con.escape_string(originalMapName), con.escape_string(originalMapName)))
        else:
          cur.execute("select distinct r.Name, r.ID, r.Time, r.Timestamp from ((select distinct ID from record_teamrace where Map = '%s' ORDER BY Time) as l) left join (select * from record_teamrace where Map = '%s') as r on l.ID = r.ID join record_race on r.Map = record_race.Map and r.Name = record_race.Name and r.Time = record_race.Time %s order by r.Time, r.ID, r.Name;" % (con.escape_string(originalMapName), con.escape_string(originalMapName), mbCountry2))
        rows = cur.fetchall()
      except:
        traceback.print_exc()
      if len(rows) > 0:
        ID = rows[0][1]

      for row in rows:
        if row[1] != ID:
          if currentPosition <= 10:
            fNames = []
            for name in names:
              fNames.append('<a href="%s">%s</a>' % (escape(playerWebsite(u'%s' % name)), escape(name)))
            teamRanks.append((currentRank, joinNames(fNames), time, timestamp))
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
        if originalMapName not in players[row[0]].maps:
          players[row[0]].maps[originalMapName] = PlayerMap(currentRank, 0, 0, "2030-10-10 00:00:00", 0.0)

        if currentPosition <= 10:
          time = row[2]
          timestamp = row[3]
          names.append(row[0])

        if currentRank <= 10 and row[0] not in namesOnMap:
          namesOnMap[row[0]] = True

          teamrankLadder[row[0]] += points(currentRank)
          serverTeamrankLadder[row[0]] += points(currentRank)

      if currentPosition <= 10 and time > 0:
        fNames = []
        for name in names:
          fNames.append('<a href="%s">%s</a>' % (escape(playerWebsite(u'%s' % name)), escape(name)))
        teamRanks.append((currentRank, joinNames(fNames), time, timestamp))

      if time > 0:
        countTeamFinishes += 1

      rows = []
      ranks = []
      countFinishes = 0

      try:
        cur.execute("select l.Name, minTime, l.Timestamp, playCount, minTimestamp, l.Server from (select * from record_race where Map = '%s' %s) as l JOIN (select Name, min(Time) as minTime, count(*) as playCount, min(Timestamp) as minTimestamp from record_race where Map = '%s' %s group by Name order by minTime ASC) as r on l.Time = r.minTime and l.Name = r.Name GROUP BY Name ORDER BY minTime;" % (con.escape_string(originalMapName), mbCountry, con.escape_string(originalMapName), mbCountry))
        rows = cur.fetchall()
      except:
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

        if row[0] not in players:
          players[row[0]] = Player({}, {})
        if originalMapName not in players[row[0]].maps:
          players[row[0]].maps[originalMapName] = PlayerMap(0, currentRank, row[3], row[4], row[1])
        else:
          players[row[0]].maps[originalMapName] = PlayerMap(players[row[0]].maps[originalMapName][0], currentRank, row[3], row[4], row[1])

        if row[5] != None:
          if row[5] not in players[row[0]].servers:
            players[row[0]].servers[row[5]] = 1
          else:
            players[row[0]].servers[row[5]] += 1

        if currentPosition <= 10:
          ranks.append((currentRank, row[0], row[1], row[2], row[3]))
        if currentRank <= 10:
          rankLadder[row[0]] += points(currentRank)
          serverRankLadder[row[0]] += points(currentRank)

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
          cur.execute("select avg(Time), min(Timestamp), max(Timestamp) from record_race where Map = '%s' %s;" % con.escape_string(originalMapName), mbCountry)
          rows = cur.fetchall()
          avgTime = " (average time: %s)" % formatTime(rows[0][0])
          finishTimes = "first finish: %s, last finish: %s" % (escape(formatDate(rows[0][1])), escape(formatDate(rows[0][2])))
        except:
          pass

        try:
            cur.execute("select count(Name) from record_race where Map = '%s' %s;" % con.escape_string(originalMapName), mbCountry)
            rows = cur.fetchall()
            finishTimes += ", total finishes: %d" % rows[0][0]
        except:
          pass

      biggestTeam = ""

      try:
        if country == None:
          cur.execute("select count(Name) from record_teamrace where Map = '%s' group by ID order by count(Name) desc limit 1;" % con.escape_string(originalMapName))
        else:
          cur.execute("select count(record_teamrace.Name) from (record_teamrace join record_race on record_teamrace.Map = record_race.Map and record_teamrace.Name = record_race.Name and record_teamrace.Time = record_race.Time) where record_teamrace.Map = '%s' %s group by ID order by count(record_teamrace.Name) desc limit 1;" % (con.escape_string(originalMapName), mbCountry))
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

          formattedMapName = '<span title="%dx%d">%s</span>' % (width, height, escape(originalMapName))

          mbMapInfo = "<br/>"
          for tile in sorted(tiles.keys(), key=lambda i:order(i)):
            mbMapInfo += '<span title="%s"><img alt="%s" src="/tiles/%s.png" width="32" height="32"/></span> ' % (description(tile), description(tile), tile)
      except IOError:
        traceback.print_exc()

      if type == "Solo" or type == "Race" or type == "Dummy":
        mapsString += u'<div class="block2 info" id="map-%s"><h3 class="inline">%s</h3><p class="inline">%s</p><p>Difficulty: %s, Points: %d<br/><a href="/maps/?map=%s"><img class="screenshot" alt="Screenshot" src="/ranks/maps/%s.png" width="360" height="225" /></a>%s<br/><span title="%s">%d tee%s finished%s</span></p></div>\n' % (escape(mapName), formattedMapName, mbMapperName, escape(renderStars(stars)), globalPoints(type, stars), quote_plus(originalMapName), escape(mapName), mbMapInfo, finishTimes, countFinishes, mbS2, escape(avgTime))
        mapsString += printExactSoloRecords("Records", "records", ranks)
      else:
        mapsString += u'<div class="block2 info" id="map-%s"><h3 class="inline">%s</h3><p class="inline">%s</p><p>Difficulty: %s, Points: %d<br/><a href="/maps/?map=%s"><img class="screenshot" alt="Screenshot" src="/ranks/maps/%s.png" width="360" height="225" /></a>%s<br/><span title="%s">%d tee%s finished%s</span><br/>%d team%s finished%s</p></div>\n' % (escape(mapName), formattedMapName, mbMapperName, escape(renderStars(stars)), globalPoints(type, stars), quote_plus(originalMapName), escape(mapName), mbMapInfo, finishTimes, countFinishes, mbS2, escape(avgTime), countTeamFinishes, mbS, escape(biggestTeam))
        mapsString += printTeamRecords("Team Records", "teamrecords", teamRanks)
        mapsString += printSoloRecords("Records", "records", ranks)
      mapsString += '<br/>\n'

    serverPointsRanks = sorted(serverPointsLadder.items(), key=lambda r: r[1], reverse=True)
    weeklyServerPointsRanks = sorted(weeklyServerPointsLadder.items(), key=lambda r: r[1], reverse=True)
    monthlyServerPointsRanks = sorted(monthlyServerPointsLadder.items(), key=lambda r: r[1], reverse=True)
    serverTeamrankRanks = sorted(serverTeamrankLadder.items(), key=lambda r: r[1], reverse=True)
    serverRankRanks = sorted(serverRankLadder.items(), key=lambda r: r[1], reverse=True)

    serverRanks[type] = (totalServerPoints, serverPointsRanks, serverTeamrankRanks, serverRankRanks)

    serversString += printLadder("Points (%d total)" % totalServerPoints, serverPointsRanks, players)
    if type != "Solo" and type != "Race" and type != "Dummy":
      serversString += printLadder("Team Rank", serverTeamrankRanks, players)
    serversString += printLadder("Rank", serverRankRanks, players)
    serversString += '<br/>'

    lastString = ""
    cur.execute("select l.Timestamp, l.Map, Name, Time from (select Timestamp, Map, Name, Time from record_race %s) as l join record_maps on l.Map = record_maps.Map where Server = '%s' order by l.Timestamp desc limit 10;" % (mbCountry2, type))
    rows = cur.fetchall()

    lastString = '<div class="block4"><h3>Last Finishes</h3><table class="tight">'

    for row in rows:
      if country == None:
        mapLink = "/ranks/%s/#map-%s" % (type.lower(), escape(normalizeMapname(row[1])))
      else:
        mapLink = "/ranks/%s/%s/#map-%s" % (country.lower(), type.lower(), escape(normalizeMapname(row[1])))
      lastString += '<tr><td><span title="%s">%s</span>: <a href="%s">%s</a> by <a href="%s">%s</a> (%s)</td></tr>' % (escape(formatDate(row[0])), escape(formatDateShort(row[0])), mapLink, escape(row[1]), escape(playerWebsite(row[2])), escape(row[2]), escape(formatTime(row[3])))

    lastString += '</table></div><br/>'

    serversString += printLadder("Points (last month)", monthlyServerPointsRanks, players)
    serversString += printLadder("Points (last week)", weeklyServerPointsRanks, players)
    serversString += lastString
    serversString += '</div>\n'
    serversString += '<div class="all-%s" style="display: ">\n' % type
    serversString += mapsString
    serversString += '</div>\n'

    tf = open(tmpname, 'w')

    if country == None:
      print >>tf, header("%s Server Ranks - DDraceNetwork" % type, menuText, "")
    else:
      print >>tf, header("%s %s Server Ranks - DDraceNetwork" % (country, type), menuText, "")
    print >>tf, '<p class="toggle"><a href="#" onclick="showClass(\'allPoints\'); return false;">Top 500 / Top 10</a></p>'

    print >>tf, '<div id="serverranks" style="display: ">'
    print >>tf, serversString
    print >>tf, '</div>'
    print >>tf, printFooter()

    tf.close()
    os.rename(tmpname, filename)

  lastString = ""
  cur.execute("select l.Timestamp, l.Map, Name, Time, record_maps.Server from ((select * from record_race %s order by Timestamp desc limit 20) as l join record_maps on l.Map = record_maps.Map);" % mbCountry2)
  rows = cur.fetchall()

  lastString = '<div class="block4"><h3>Last Finishes</h3><table>'

  for row in rows:
    if country == None:
      mapLink = "/ranks/%s/#map-%s" % (row[4].lower(), escape(normalizeMapname(row[1])))
    else:
      mapLink = "/ranks/%s/%s/#map-%s" % (country.lower(), row[4].lower(), escape(normalizeMapname(row[1])))
    lastString += '<tr><td><span title="%s">%s</span>: <a href="%s">%s</a> by <a href="%s">%s</a> (%s)</td></tr>' % (escape(formatDate(row[0])), escape(formatDateShort(row[0])), mapLink, escape(row[1]), escape(playerWebsite(row[2])), escape(row[2]), escape(formatTime(row[3])))

  lastString += '</table></div><br/>'

  #cur.execute('show profiles')
  #for row in cur:
  #  print(row)

pointsRanks = sorted(pointsLadder.items(), key=lambda r: r[1], reverse=True)
del pointsLadder
weeklyPointsRanks = sorted(weeklyPointsLadder.items(), key=lambda r: r[1], reverse=True)
del weeklyPointsLadder
monthlyPointsRanks = sorted(monthlyPointsLadder.items(), key=lambda r: r[1], reverse=True)
del monthlyPointsLadder
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

tf = open(tmpname, 'w')

if country == None:
  print >>tf, header("Ranks - DDraceNetwork", menuText, "")
else:
  print >>tf, header("%s Ranks - DDraceNetwork" % country, menuText, "")
print >>tf, '<p class="toggle"><a href="#" onclick="showClass(\'allPoints\'); return false;">Top 500 / Top 20</a></p>'

print >>tf, '<div id="global" class="block">\n'
print >>tf, '<div id="remote" class="right"><form id="playerform" action="/players/" method="get"><input name="player" class="typeahead" type="text" placeholder="Player search"><input type="submit" value="Player search" style="position: absolute; left: -9999px"></form></div>'
print >>tf, '<script src="/jquery.js" type="text/javascript"></script>'
print >>tf, '<script src="/typeahead.bundle.js" type="text/javascript"></script>'
print >>tf, '<script src="/playersearch.js" type="text/javascript"></script>'
if country == None:
  print >>tf, '<div class="block7"><h2>Global Ranks</h2></div><br/>'
else:
  print >>tf, '<div class="block7"><h2>%s Ranks</h2></div><br/>' % country
print >>tf, printLadder("Points (%d total)" % totalPoints, pointsRanks, players, 20)
print >>tf, printLadder("Team Rank", teamrankRanks, players, 20)
print >>tf, printLadder("Rank", rankRanks, players, 20)
print >>tf, '<br/>'
print >>tf, printLadder("Points (last month)", monthlyPointsRanks, players, 20)
print >>tf, printLadder("Points (last week)", weeklyPointsRanks, players, 20)
print >>tf, lastString
print >>tf, '</div>'
print >>tf, printFooter()

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
    out.write(msgpack.packb(teamrankRanks))
    out.write(msgpack.packb(rankRanks))
    out.write(msgpack.packb(serverRanks))
  os.rename(msgpackTmpFile, msgpackFile)

  with Cache('/home/teeworlds/servers/players-cache') as cache:
    for player, value in players.items():
        cache[player] = value

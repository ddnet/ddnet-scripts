#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ddnet import *
import sys
import os
from cgi import escape
from urllib import quote_plus
from datetime import datetime, timedelta
from collections import defaultdict
import msgpack
import traceback
from time import sleep

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
          <td>Hitomi</td>
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
  </section>
  </article>
  </body>
</html>"""

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
types = sys.argv[1:]

menuText = '<ul>'
menuText += '<li><a href="/ranks/">Global Ranks</a></li>'
for type in types:
  menuText += '<li><a href="/ranks/%s/">%s Server</a></li>\n' % (type, type.title())
menuText += '<li><a href="#points">Points Calculation</a></li>\n'
menuText += '</ul>'

print header("Ranks - DDraceNetwork", menuText, "")
print '<p class="toggle"><a title="Click to toggle whether only the top 10 ranks or all ranks are shown" href="#" onclick="showClass(\'allPoints\'); return false;">Top 500 / Top 20</a></p>'

with con:
  cur = con.cursor()
  cur.execute("set names 'utf8';")
  for type in types:
    filename = "%s/ranks/%s/index.html" % (webDir, type)
    tmpname = "%s/ranks/%s/index.tmp" % (webDir, type)
    directory = os.path.dirname(filename)
    if not os.path.exists(directory):
      os.makedirs(directory)
    tf = open(tmpname, 'w')

    print >>tf, header("%s Ranks - DDraceNetwork" % type.title(), menuText, "")
    print >>tf, '<p class="toggle"><a title="Click to toggle whether only the top 10 ranks or all ranks are shown" href="#" onclick="showClass(\'allPoints\'); return false;">Top 500 / Top 10</a></p>'

    serversString = ""
    totalServerPoints = 0
    serverRankLadder = defaultdict(int)
    serverTeamrankLadder = defaultdict(int)
    serverPointsLadder = defaultdict(int)
    weeklyServerPointsLadder = defaultdict(int)
    monthlyServerPointsLadder = defaultdict(int)

    f = open("types/%s/maps" % type, 'r')

    serversString += '<div id="%s" class="longblock div-ranks">\n' % type
    serversString += '<div id="remote" class="right"><form id="playerform" action="/players/" method="get"><input name="player" class="typeahead" type="text" placeholder="Player search"><input type="submit" value="Player search" style="position: absolute; left: -9999px"></form></div>\n'
    serversString += '<script src="/jquery.js" type="text/javascript"></script>\n'
    serversString += '<script src="/typeahead.bundle.js" type="text/javascript"></script>\n'
    serversString += '<script src="/playersearch.js" type="text/javascript"></script>\n'
    serversString += '<div class="block7"><h2>%s Server Ranks</h2></div><br/>\n' % type.title()

    mapsString = ""

    maps[type] = []

    for line in f:
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

      maps[type].append(originalMapName)

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
        cur.execute("select Name, r.ID, Time, Timestamp from ((select distinct ID from record_teamrace where Map = '%s' ORDER BY Time) as l) left join (select * from record_teamrace where Map = '%s') as r on l.ID = r.ID order by r.Time, r.ID, Name;" % (con.escape_string(originalMapName), con.escape_string(originalMapName)))
        sleep(0.1)
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
          players[row[0]].maps[originalMapName] = PlayerMap(currentRank, 0, 0, 0, date(2015,10,10),  date(2016,10,10))

        if currentPosition > 10:
          continue

        time = row[2]
        timestamp = row[3]
        names.append(row[0])

        if row[0] in namesOnMap:
          continue

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
        cur.execute("select l.Name, minTime, l.Timestamp, playCount, minTimestamp, l.Server from (select * from record_race where Map = '%s') as l JOIN (select Name, min(Time) as minTime, count(*) as playCount, min(Timestamp) as minTimestamp from record_race where Map = '%s' group by Name order by minTime ASC) as r on l.Time = r.minTime and l.Name = r.Name GROUP BY Name ORDER BY minTime;" % (con.escape_string(originalMapName), con.escape_string(originalMapName)))
        sleep(0.1)
        rows = cur.fetchall()
      except:
        traceback.print_exc()

      countFinishes = len(rows)
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
          players[row[0]].maps[originalMapName] = PlayerMap(0, currentRank, globalPoints(type, stars), row[3], row[4], row[1])
        else:
          players[row[0]].maps[originalMapName] = PlayerMap(players[row[0]].maps[originalMapName][0], currentRank, globalPoints(type, stars), row[3], row[4], row[1])

        if row[5] != None:
          if row[5] not in players[row[0]].servers:
            players[row[0]].servers[row[5]] = 1
          else:
            players[row[0]].servers[row[5]] += 1

        if currentPosition > 10:
          continue

        ranks.append((currentRank, row[0], row[1], row[2], row[3]))

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
          cur.execute("select avg(Time), min(Timestamp), max(Timestamp) from record_race where Map = '%s';" % con.escape_string(originalMapName))
          rows = cur.fetchall()
          avgTime = " (average time: %s)" % formatTime(rows[0][0])
          finishTimes = "first finish: %s, last finish: %s" % (escape(formatDate(rows[0][1])), escape(formatDate(rows[0][2])))
        except:
          pass

        try:
            cur.execute("select count(Name) from record_race where Map = '%s';" % con.escape_string(originalMapName))
            rows = cur.fetchall()
            finishTimes += ", total finishes: %d" % rows[0][0]
        except:
          pass

      biggestTeam = ""

      try:
        cur.execute("select count(Name) from record_teamrace where Map = '%s' group by ID order by count(Name) desc limit 1;" % con.escape_string(originalMapName))
        rows = cur.fetchall()
        sleep(0.1)
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

      if type == "solo":
        mapsString += u'<div class="block2 info" id="map-%s"><h3 class="inline">%s</h3><p class="inline">%s</p><p>Difficulty: %s, Points: %d<br/><a href="/maps/?map=%s"><img class="screenshot" alt="Screenshot" src="../maps/%s.png" /></a>%s<br/><span title="%s">%d tee%s finished%s</span></p></div>\n' % (escape(mapName), formattedMapName, mbMapperName, escape(renderStars(stars)), globalPoints(type, stars), quote_plus(originalMapName), escape(mapName), mbMapInfo, finishTimes, countFinishes, mbS2, escape(avgTime))
      else:
        mapsString += u'<div class="block2 info" id="map-%s"><h3 class="inline">%s</h3><p class="inline">%s</p><p>Difficulty: %s, Points: %d<br/><a href="/maps/?map=%s"><img class="screenshot" alt="Screenshot" src="../maps/%s.png" /></a>%s<br/><span title="%s">%d tee%s finished%s</span><br/>%d team%s finished%s</p></div>\n' % (escape(mapName), formattedMapName, mbMapperName, escape(renderStars(stars)), globalPoints(type, stars), quote_plus(originalMapName), escape(mapName), mbMapInfo, finishTimes, countFinishes, mbS2, escape(avgTime), countTeamFinishes, mbS, escape(biggestTeam))
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
    if type != "solo":
      serversString += printLadder("Team Rank", serverTeamrankRanks, players)
    serversString += printLadder("Rank", serverRankRanks, players)
    serversString += '<br/>'

    lastString = ""
    cur.execute("select Timestamp, l.Map, Name, Time from (select Timestamp, Map, Name, Time from record_race) as l join record_maps on l.Map = record_maps.Map where Server = '%s' order by Timestamp desc limit 10;" % type)
    rows = cur.fetchall()
    sleep(0.1)

    lastString = '<div class="block4"><h3>Last Finishes</h3><table class="tight">'

    for row in rows:
      lastString += '<tr><td><span title="%s">%s</span>: <a href="/ranks/%s/#map-%s">%s</a> by <a href="%s">%s</a> (%s)</td></tr>' % (escape(formatDate(row[0])), escape(formatDateShort(row[0])), type, escape(normalizeMapname(row[1])), escape(row[1]), escape(playerWebsite(row[2])), escape(row[2]), escape(formatTime(row[3])))

    lastString += '</table></div><br/>'

    serversString += printLadder("Points (last month)", monthlyServerPointsRanks, players)
    serversString += printLadder("Points (last week)", weeklyServerPointsRanks, players)
    serversString += lastString
    serversString += '<div class="all-%s" style="display: ">\n' % type
    serversString += mapsString
    serversString += '</div>\n'
    serversString += '</div>\n'

    print >>tf, '<div id="serverranks" style="display: ">'
    print >>tf, serversString
    print >>tf, '</div>'
    print >>tf, printFooter()

    tf.close()
    os.rename(tmpname, filename)
    sleep(1)

  lastString = ""
  cur.execute("select Timestamp, Map, Name, Time from record_race order by Timestamp desc limit 20;")
  rows = cur.fetchall()
  sleep(0.1)

  lastString = '<div class="block4"><h3>Last Finishes</h3><table>'

  for row in rows:
    for t in types:
      if row[1] in maps[t]:
        type = t
        break

    lastString += '<tr><td><span title="%s">%s</span>: <a href="/ranks/%s/#map-%s">%s</a> by <a href="%s">%s</a> (%s)</td></tr>' % (escape(formatDate(row[0])), escape(formatDateShort(row[0])), type, escape(normalizeMapname(row[1])), escape(row[1]), escape(playerWebsite(row[2])), escape(row[2]), escape(formatTime(row[3])))

  lastString += '</table></div><br/>'

pointsRanks = sorted(pointsLadder.items(), key=lambda r: r[1], reverse=True)
weeklyPointsRanks = sorted(weeklyPointsLadder.items(), key=lambda r: r[1], reverse=True)
monthlyPointsRanks = sorted(monthlyPointsLadder.items(), key=lambda r: r[1], reverse=True)
teamrankRanks = sorted(teamrankLadder.items(), key=lambda r: r[1], reverse=True)
rankRanks = sorted(rankLadder.items(), key=lambda r: r[1], reverse=True)

print '<div id="global" class="block">\n'
print '<div id="remote" class="right"><form id="playerform" action="/players/" method="get"><input name="player" class="typeahead" type="text" placeholder="Player search"><input type="submit" value="Player search" style="position: absolute; left: -9999px"></form></div>'
print '<script src="/jquery.js" type="text/javascript"></script>'
print '<script src="/typeahead.bundle.js" type="text/javascript"></script>'
print '<script src="/playersearch.js" type="text/javascript"></script>'
print '<div class="block7"><h2>Global Ranks</h2></div><br/>'
print printLadder("Points (%d total)" % totalPoints, pointsRanks, players, 20)
print printLadder("Team Rank", teamrankRanks, players, 20)
print printLadder("Rank", rankRanks, players, 20)
print '<br/>'
print printLadder("Points (last month)", monthlyPointsRanks, players, 20)
print printLadder("Points (last week)", weeklyPointsRanks, players, 20)
print lastString
print '</div>'
print printFooter()

tmpname = '%s/players/index.tmp' % webDir
filename = '%s/players/index.html' % webDir
with open(tmpname, 'wb') as out:
  print >>out, header("Player not found - DDraceNetwork", "", "")
  print >>out, '<div id="global" class="longblock"><h2>Player not found</h2><h3>Maybe who you\'re looking for is in this list:</h3>'
  print >>out, '<ol>'

  for player in sorted(players.keys()):
    print >>out, '<li><a href="%s">%s</a></li>' % (playerWebsite(u'%s' % player), escape(player))

  print >>out, '</ol>'
  print >>out, '</div>'
  print >>out, """  </section>
</article>
</body>
</html>"""
os.rename(tmpname, filename)
sleep(1)

tmpname = '%s/playerNames.tmp' % webDir
filename = '%s/playerNames.msgpack' % webDir
with open(tmpname, 'wb') as out:
  out.write(msgpack.packb(players.keys()))
os.rename(tmpname, filename)
sleep(1)

tmpname = '%s/players.tmp' % webDir
filename = '%s/players.msgpack' % webDir
with open(tmpname, 'wb') as out:
  out.write(msgpack.packb(types))
  out.write(msgpack.packb(maps))
  out.write(msgpack.packb(totalPoints))
  out.write(msgpack.packb(pointsRanks))
  out.write(msgpack.packb(weeklyPointsRanks))
  out.write(msgpack.packb(monthlyPointsRanks))
  out.write(msgpack.packb(teamrankRanks))
  out.write(msgpack.packb(rankRanks))
  out.write(msgpack.packb(serverRanks))
  out.write(msgpack.packb(players, default=str))
os.rename(tmpname, filename)

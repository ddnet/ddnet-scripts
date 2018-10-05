#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ddnet import *
import sys
import msgpack
from cgi import escape
import os

reload(sys)
sys.setdefaultencoding('utf8')

def printFooter():
  print """
  </section>
  </article>
  </body>
</html>"""

def printTeamRecords2(recordName, className, topFinishes):
  string = u'<div class="block4"><h4>%s:</h4>\n' % recordName
  if len(topFinishes) > 0:
    string += '<table class="tight">\n'
    for f in topFinishes:
      # Best time wins
      #string += u'  <tr title="%s, %s"><td class="rank">%d.</td><td>%s</td><td><img src="/countryflags/%s.png" alt="%s" height="15" /></td><td>%s</td></tr>\n' % (escape(formatTimeExact(f[2])), escape(formatDate(f[3])), f[0], escape(formatTimeExact(f[2])), f[4], f[4], f[1])
      # First finish wins
      string += u'  <tr title="%s, %s"><td class="rank">%d.</td><td>%s</td><td><img src="/countryflags/%s.png" alt="%s" height="15" /></td><td>%s</td></tr>\n' % (escape(formatTimeExact(f[2])), escape(formatDate(f[3])), f[0], escape(formatDateShort(f[3])), f[4], f[4], f[1])
    string += '</table>\n'
  string += '</div>\n'

  return string

con = mysqlConnect()

rankLadder = {}
teamrankLadder = {}
pointsLadder = {}
serversString = ""
players = {}
maps = {}
totalPoints = 0
serverRanks = {}

types = sys.argv[1:]
os.chdir("/home/teeworlds/servers/")

menuText = '<ul>\n'
for type in types:
  menuText += '<li><a href="#%s">%s Server</a></li>\n' % (type, type)
menuText += '</ul>'
print header("4rd Birthday Tournament #4 - DDraceNetwork", menuText, '<script src="/youtube.js" type="text/javascript"></script>')

f = open("tournament")
tournamentMaps = []
for line in f:
  words = line.rstrip('\n').split('|')
  tournamentMaps.append(tuple(words))

with con:
  cur = con.cursor()
  cur.execute("set names 'utf8mb4';");
  for type in types:
    totalServerPoints = 0
    serverRankLadder = {}
    serverTeamrankLadder = {}
    serverPointsLadder = {}

    f = open("types/%s/maps" % type.lower(), 'r')

    serversString += '<div id="%s" class="block div-tournament"><div class="back-up"><a href="#top">&#8593;</a></div><h2>%s Server</h2>\n' % (type, type)
    mapsString = ""

    maps[type] = []

    for x in tournamentMaps:
      thisType, stars, originalMapName, mapperName = x

      if thisType != type:
        continue

      stars = int(stars)

      totalPoints += globalPoints(type, stars)
      totalServerPoints += globalPoints(type, stars)

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
        # Best time wins
        #cur.execute("select Name, r.ID, Time, Timestamp from ((select distinct ID from record_teamrace where Map = '%s' ORDER BY Time) as l) left join (select * from record_teamrace where Map = '%s') as r on l.ID = r.ID order by r.Time, r.ID, Name;" % (con.escape_string(originalMapName), con.escape_string(originalMapName)))
        # First finish wins
        cur.execute("select Name, r.ID, Time, Timestamp from ((select distinct ID from record_teamrace where Map = '%s' ORDER BY Timestamp) as l) left join (select * from record_teamrace where Map = '%s') as r on l.ID = r.ID order by r.Timestamp, r.ID, Name;" % (con.escape_string(originalMapName), con.escape_string(originalMapName)))
        rows = cur.fetchall()
      except:
        pass
      if len(rows) > 0:
        ID = rows[0][1]

      for row in rows:
        if row[1] != ID:
          fNames = []
          for name in names:
            fNames.append('<a href="%s">%s</a>' % (escape(playerWebsite(u'%s' % name)), escape(name)))
          cur.execute("select Server from record_race where Map = '%s' and Name = '%s'" % (con.escape_string(originalMapName), con.escape_string(names[0])))
          rows = cur.fetchall()
          teamRanks.append((currentRank, joinNames(fNames), time, timestamp, rows[0][0]))
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
          players[row[0]].maps[originalMapName] = PlayerMap(currentRank, 0, 0, date(2015,10,10),  date(2016,10,10))

        time = row[2]
        timestamp = row[3]
        names.append(row[0])

        if row[0] in namesOnMap:
          continue

        namesOnMap[row[0]] = True

        if row[0] in teamrankLadder:
          teamrankLadder[row[0]] += points(currentRank)
        else:
          teamrankLadder[row[0]] = points(currentRank)

        if row[0] in serverTeamrankLadder:
          serverTeamrankLadder[row[0]] += points(currentRank)
        else:
          serverTeamrankLadder[row[0]] = points(currentRank)

      if time > 0:
        fNames = []
        for name in names:
          fNames.append('<a href="%s">%s</a>' % (escape(playerWebsite(u'%s' % name)), escape(name)))
        cur.execute("select Server from record_race where Map = '%s' and Name = '%s'" % (con.escape_string(originalMapName), con.escape_string(names[0])))
        rows = cur.fetchall()
        teamRanks.append((currentRank, joinNames(fNames), time, timestamp, rows[0][0]))
        countTeamFinishes += 1

      rows = []
      ranks = []
      countFinishes = 0

      try:
        # Best time wins
        #cur.execute("select l.Name, minTime, l.Timestamp, playCount, minTimestamp, maxTimestamp from (select * from record_race where Map = '%s') as l JOIN (select Name, min(Time) as minTime, count(*) as playCount, min(Timestamp) as minTimestamp, max(Timestamp) as maxTimestamp from record_race where Map = '%s' group by Name order by minTimestamp ASC) as r on l.Time = r.minTime and l.Name = r.Name GROUP BY Name ORDER BY minTime;" % (con.escape_string(originalMapName), con.escape_string(originalMapName)))
        # First finish wins
        cur.execute("select l.Name, minTime, l.Timestamp, playCount, minTimestamp, maxTimestamp from (select * from record_race where Map = '%s') as l JOIN (select Name, min(Time) as minTime, count(*) as playCount, min(Timestamp) as minTimestamp, max(Timestamp) as maxTimestamp from record_race where Map = '%s' group by Name order by minTimestamp ASC) as r on l.Time = r.minTime and l.Name = r.Name GROUP BY Name ORDER BY minTimestamp;" % (con.escape_string(originalMapName), con.escape_string(originalMapName)))
        rows = cur.fetchall()
      except:
        pass

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

        if row[0] in pointsLadder:
          pointsLadder[row[0]] += globalPoints(type, stars)
        else:
          pointsLadder[row[0]] = globalPoints(type, stars)

        if row[0] in serverPointsLadder:
          serverPointsLadder[row[0]] += globalPoints(type, stars)
        else:
          serverPointsLadder[row[0]] = globalPoints(type, stars)

        if row[0] not in players:
          players[row[0]] = Player({}, {})
        if originalMapName not in players[row[0]].maps:
          players[row[0]].maps[originalMapName] = PlayerMap(0, currentRank, row[3], row[4], row[1])
        else:
          players[row[0]].maps[originalMapName] = PlayerMap(players[row[0]].maps[originalMapName][0], currentRank, row[3], row[4], row[1])

        if currentPosition > 10:
          continue

        ranks.append((currentRank, row[0], row[1], row[2], row[3]))

        if row[0] in rankLadder:
          rankLadder[row[0]] += points(currentRank)
        else:
          rankLadder[row[0]] = points(currentRank)

        if row[0] in serverRankLadder:
          serverRankLadder[row[0]] += points(currentRank)
        else:
          serverRankLadder[row[0]] = points(currentRank)

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

      try:
        cur.execute("select avg(Time), min(Timestamp), max(Timestamp) from record_race where Map = '%s';" % con.escape_string(originalMapName))
        rows = cur.fetchall()
        avgTime = " (average time: %s)" % formatTime(rows[0][0])
        finishTimes = "first finish: %s, last finish: %s" % (escape(formatDate(rows[0][1])), escape(formatDate(rows[0][2])))
      except:
        pass

      biggestTeam = ""

      try:
        cur.execute("select count(Name) from record_teamrace where Map = '%s' group by ID order by count(Name) desc limit 1;" % con.escape_string(originalMapName))
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
        pass

      mapsString += u'<div class="block3 info" id="map-%s"><h3 class="inline">%s</h3><p class="inline">%s</p><p>Difficulty: %s, Points: %d<br/><a href="/maps/?map=%s"><img class="screenshot" alt="Screenshot" src="/ranks/maps/%s.png" width="360" height="225" /></a>%s<br/><span title="%s">%d tee%s finished%s</span><br/>%d team%s finished%s</p></div>\n' % (escape(mapName), formattedMapName, mbMapperName, escape(renderStars(stars)), globalPoints(type, stars), quote_plus(originalMapName), escape(mapName), mbMapInfo, finishTimes, countFinishes, mbS2, escape(avgTime), countTeamFinishes, mbS, escape(biggestTeam))
      mapsString += printTeamRecords2("Team Records", "teamrecords", teamRanks)
      mapsString += '<br/>\n'

    serverPointsRanks = sorted(serverPointsLadder.items(), key=lambda r: r[1], reverse=True)
    serverTeamrankRanks = sorted(serverTeamrankLadder.items(), key=lambda r: r[1], reverse=True)
    serverRankRanks = sorted(serverRankLadder.items(), key=lambda r: r[1], reverse=True)

    serverRanks[type] = (totalServerPoints, serverPointsRanks, serverTeamrankRanks, serverRankRanks)

    serversString += '<br/><div class="all-%s" style="display: ">\n' % type
    serversString += mapsString
    serversString += '</div>\n'
    serversString += '</div>\n'

print '<div id="global" class="block div-tournament"><h2>4th Birthday Tournament #4</h2>'
print '<p>This tournament is played on Sunday, 2017-08-06 at 20:00 CEST as part of our <a href="https://forum.ddnet.tw/viewtopic.php?t=5449">4th Birthday Tournament</a>.</p>'
print '<div class="video-container"><div class="ytplayer" data-id="lSy9bepW-O4"></div></div>'
print '</div>'
print '<div id="serverranks" style="display: ">'
print serversString
print '</div>'
printFooter()

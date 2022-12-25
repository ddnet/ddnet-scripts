#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from ddnet import *
import sys
import msgpack
from cgi import escape

reload(sys)
sys.setdefaultencoding('utf8')

def printExactSoloRecords2(recordName, className, topFinishes):
  string = u'<div class="block4 %s"><h4>%s:</h4>\n' % (className, recordName)
  if len(topFinishes) > 0:
    string += '<table class="tight">\n'
    for i, f in enumerate(topFinishes):
      if f[4] > 1:
        mbS = "es"
      else:
        mbS = ""
      #string += u'  <tr title="%s, %s, %d finish%s total"><td class="rank">%d.</td><td class="time">%s</td><td><a href="%s">%s</a></td></tr>\n' % (escape(formatTimeExact(f[2])), escape(formatDate(f[3])), f[4], mbS, f[0], escape(formatTimeExact(f[2])), escape(playerWebsite(u'%s' % f[1])), escape(f[1]))
      string += u'  <tr %s title="%s, %s, %d finish%s total"><td class="rank">%d.</td><td class="time">%s</td><td><img src="/countryflags/%s.png" alt="%s" height="15" /></td><td><a href="%s">%s</a></td></tr>\n' % ('' if i < 20 else 'class="allPoints" style="display: none"', escape(formatTimeExact(f[2])), escape(formatDate(f[3])), f[4], mbS, f[0], escape(formatTimeExact(f[2])), f[5], f[5], escape(playerWebsite(u'%s' % f[1])), escape(f[1]))
    string += '</table>\n'
  string += '</div>\n'

  return string

def printFooter():
  print """
  </section>
  </article>
  </body>
</html>"""

def printLadder(ranks):
  string = '<div class="ladder">\n'
  currentPos = 0
  currentRank = 0
  skips = 1
  lastPoints = 0
  if len(ranks) > 0:
    string += '<table class="tight">\n'
    for r in ranks:
      currentPos += 1
      if r[1] != lastPoints:
        lastPoints = r[1]
        currentRank += skips
        skips = 1
      else:
        skips += 1
      if currentPos > 20:
        string += '<tr class="allPoints" style="display: none">\n'
      else:
        string += '<tr>\n'
      string += u'  <td class="rankglobal">%d.</td><td class="points">%d points</td><td><a href="%s">%s</a></td></tr>' % (currentRank, r[1], escape(playerWebsite(u'%s' % r[0])), escape(r[0]))
    string += '</table>\n'
  string += '</div>'

  return string

con = mysqlConnect()

rankLadder = {}
teamrankLadder = {}
pointsLadder = {}
serversString = ""
players = {}
serverRanks = {}

f = open("advent")
tournamentMaps = []
menuText = '<ul>\n'
day = 0
for line in f:
  day += 1
  menuText += '<li><a href="#day%d">Day %d</a></li>\n' % (day, day)
  words = line.rstrip('\n').split('|')
  tournamentMaps.append(tuple(words))
if day < 24:
  day += 1
  menuText += '<li><a href="#day%d">Day %d</a></li>\n' % (day, day)
menuText += '</ul>'
print header("Advent of DDNet 2022 - DDraceNetwork", menuText, "")
print '<p class="toggle"><a href="#" onclick="showClass(\'allPoints\'); return false;">All / Top 20</a></p>'

def betweenDate(day):
  return "Timestamp between '2022-12-%02d' and '2022-12-%02d'" % (day, day + 1)

def adventPoints(rank):
  if rank <= 10:
    return 21 - rank
  else:
    return 10

with con:
  cur = con.cursor()
  cur.execute("set names 'utf8mb4';");
  totalServerPoints = 0
  serverRankLadder = {}
  serverTeamrankLadder = {}

  day = 0

  for x in tournamentMaps:
    mapsString = ""
    day += 1
    type, stars, originalMapName, mapperName = x
    serversString += '<div id="day%s" class="block div-tournament"><div class="back-up"><a href="#top">&#8593;</a></div><h2>Day %d: %s</h2>\n' % (day, day, type)

    f = open("types/%s/maps" % type.lower(), 'r')

    stars = int(stars)

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
      cur.execute("select Name, r.ID, Time, Timestamp from ((select distinct ID from record_teamrace where Map = '%s' AND %s ORDER BY Time) as l) left join (select * from record_teamrace where Map = '%s' and %s) as r on l.ID = r.ID order by r.Time, r.ID, Name;" % (con.escape_string(originalMapName), betweenDate(day), con.escape_string(originalMapName), betweenDate(day)))
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
        players[row[0]].maps[originalMapName] = PlayerMap(currentRank, 0, 0, date(2015,10,10),  date(2016,10,10))

      #if currentPosition > 10:
      #  continue

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
      teamRanks.append((currentRank, joinNames(fNames), time, timestamp))
      countTeamFinishes += 1

    rows = []
    ranks = []
    countFinishes = 0

    try:
      cur.execute("select l.Name, minTime, l.Timestamp, playCount, minTimestamp, maxTimestamp, Server from (select * from record_race where Map = '%s' and %s) as l JOIN (select Name, min(Time) as minTime, count(*) as playCount, min(Timestamp) as minTimestamp, max(Timestamp) as maxTimestamp from record_race where Map = '%s' and %s group by Name order by minTime ASC) as r on l.Time = r.minTime and l.Name = r.Name GROUP BY Name ORDER BY minTime, Name;" % (con.escape_string(originalMapName), betweenDate(day), con.escape_string(originalMapName), betweenDate(day)))
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
        pointsLadder[row[0]] += adventPoints(currentRank)
      else:
        pointsLadder[row[0]] = adventPoints(currentRank)

      if row[0] not in players:
        players[row[0]] = Player({}, {})
      if originalMapName not in players[row[0]].maps:
        players[row[0]].maps[originalMapName] = PlayerMap(0, currentRank, row[3], row[4], row[1])
      else:
        players[row[0]].maps[originalMapName] = PlayerMap(players[row[0]].maps[originalMapName][0], currentRank, row[3], row[4], row[1])

      #if currentPosition > 10:
      #  continue

      ranks.append((currentRank, row[0], row[1], row[2], row[3], row[6]))

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
      cur.execute("select (select median(Time) over (partition by Map) from record_race where Map = '%s' and %s limit 1), min(Timestamp), max(Timestamp) from record_race where Map = '%s' and %s;" % (con.escape_string(originalMapName), betweenDate(day), con.escape_string(originalMapName), betweenDate(day)))
      rows = cur.fetchall()
      avgTime = " (median time: %s)" % formatTime(rows[0][0])
      finishTimes = "first finish: %s, last finish: %s" % (escape(formatDate(rows[0][1])), escape(formatDate(rows[0][2])))
    except:
      pass

    biggestTeam = ""

    try:
      cur.execute("select count(Name) from record_teamrace where Map = '%s' and %s group by ID order by count(Name) desc limit 1;" % con.escape_string(originalMapName), betweenDate(day))
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

        formattedMapName = '<span title="Map size: %dx%d"><a href="/maps/%s">%s</a></span>' % (width, height, slugify2(u'%s' % originalMapName), escape(originalMapName))

        mbMapInfo = "<br/>"
        for tile in sorted(tiles.keys(), key=lambda i:order(i)):
          mbMapInfo += tileHtml(tile)
    except IOError:
      pass

    mapsString += u'<div class="block3 info" id="map-%s"><h3 class="inline">%s</h3><p class="inline">%s</p><p>Server: <a href="/ranks/%s/">%s</a>, Difficulty: %s, Points: %d<br/><a href="/maps/%s"><img class="screenshot" alt="Screenshot" src="/ranks/maps/%s.png" width="360" height="225" /></a>%s<br/><span title="%s">%d tee%s finished%s</span><br/>%d team%s finished%s</p></div>\n' % (escape(mapName), formattedMapName, mbMapperName, type.lower(), type, escape(renderStars(stars)), globalPoints(type, stars), slugify2(u'%s' % originalMapName), escape(mapName), mbMapInfo, finishTimes, countFinishes, mbS2, escape(avgTime), countTeamFinishes, mbS, escape(biggestTeam))
    #mapsString += printTeamRecords("Team Records", "teamrecords", teamRanks)
    mapsString += printExactSoloRecords2("Records", "records", ranks)
    mapsString += '<br/>\n'

    serversString += '<br/><div class="all-%s" style="display: ">\n' % type
    serversString += mapsString
    serversString += '</div>\n'
    serversString += '</div>\n'

if day < 24:
  serversString += '<div id="day%s" class="block div-tournament"><div class="back-up"><a href="#top">&#8593;</a></div><h2>Day %d: Coming in <span id="nextday"></span></h2>\n' % (day+1, day+1)
  serversString += '''<script>
    const span = document.getElementById('nextday');
    const date = new Date(Date.UTC(2022,11,%d,23,0,0,0));
    function func() {
        let rem = date - new Date();
        if (rem > 0) {
            rem = rem / 1000;
            let s = parseInt(rem %% 60, 10);
            rem /= 60;
            let m = parseInt(rem %% 60, 10);
            rem /= 60;
            let h = parseInt(rem, 10);
            span.textContent = String(h).padStart(2, '0') + ":" + String(m).padStart(2, '0') + ":" + String(s).padStart(2, '0');
        } else {
            span.innerHTML = "a few moments. <a href=\\\".\\\">Reload</a>";
            clearInterval(func);
        }
    }
    func();
    var interval = setInterval(func, 1000);
</script>''' % (day)
  serversString += '</div>\n'

pointsRanks = sorted(pointsLadder.items(), key=lambda r: r[1], reverse=True)
#teamrankRanks = sorted(teamrankLadder.items(), key=lambda r: r[1], reverse=True)
#rankRanks = sorted(rankLadder.items(), key=lambda r: r[1], reverse=True)

print '<div id="global" class="block div-tournament"><h2>Advent of DDNet 2022</h2>'
print '<p>Finish the (already released) map behind each door on the assigned day to land on the leaderboard. Doors are opened at 00:00 CET and have to be finished within 24 hours. Best finish time gets 20 points, second 19 points and so on with a minimum of 10 points just for finishing. The points are accumulated for the entire time from December 1 to December 24 and don\'t count outside of this event.</p>'
print printLadder(pointsRanks)
print '</div>'
print '<div id="serverranks" style="display: ">'
print serversString
print '</div>'
printFooter()

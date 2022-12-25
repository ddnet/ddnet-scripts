#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from ddnet import *
import sys
from cgi import escape
from datetime import datetime, timedelta
import cStringIO
import msgpack
from operator import itemgetter
import urllib
import json
from gc import collect
from os.path import getmtime
from urlparse import parse_qs
from time import mktime

reload(sys)
sys.setdefaultencoding('utf8')

con = mysqlConnect()
con.autocommit(True)

def getTeamRanks(originalMapName, country, mbCountry2, html):
  rows = []
  teamRanks = []
  namesOnMap = {}
  names = []
  time = 0
  currentRank = 1
  currentPosition = 1
  skips = 1

  if country == None:
    query("select distinct r.Name, r.ID, r.Time, r.Timestamp, (select substring(Server, 1, 3) from record_race where Map = r.Map and Name = r.Name and Time = r.Time limit 1) as Server from ((select distinct ID from record_teamrace where Map = '%s' ORDER BY Time limit 20) as l) left join record_teamrace as r on l.ID = r.ID order by r.Time, r.ID, r.Name;" % (con.escape_string(originalMapName)))
  else:
    query("select distinct r.Name, r.ID, r.Time, r.Timestamp, SUBSTRING(n.Server, 1, 3) from ((select distinct ID from record_teamrace where Map = '%s' ORDER BY Time) as l) left join record_teamrace as r on l.ID = r.ID inner join ((select * from record_race %s) as n) on r.Map = n.Map and r.Name = n.Name and r.Time = n.Time order by r.Time, r.ID, r.Name limit 160;" % (con.escape_string(originalMapName), mbCountry2))
  rows = cur.fetchall()
  if len(rows) > 0:
    ID = rows[0][1]

  for row in rows:
    if row[1] != ID:
      if currentPosition <= 20:
        fNames = []
        for name in names:
          fNames.append('<a href="%s">%s</a>' % (escape(playerWebsite(u'%s' % name)), escape(name)))
        teamRanks.append((currentRank, joinNames(fNames) if html else names, time, timestamp, foundCountry))
        names = []

      if row[2] != time:
        time = row[2]
        timestamp = row[3]
        currentRank += skips
        skips = 1
      else:
        skips += 1
      currentPosition += 1
      ID = row[1]

    if currentPosition <= 20:
      time = row[2]
      timestamp = row[3]
      names.append(row[0])
      foundCountry = row[4] if row[4] else 'UNK'

    if currentRank <= 20 and row[0] not in namesOnMap:
      namesOnMap[row[0]] = True

  if currentPosition <= 20 and time > 0:
    fNames = []
    for name in names:
      fNames.append('<a href="%s">%s</a>' % (escape(playerWebsite(u'%s' % name)), escape(name)))
    teamRanks.append((currentRank, joinNames(fNames) if html else names, time, timestamp, foundCountry))
  return teamRanks

def getFinishes(originalMapName, country, mbCountry):
  query("select Name, count(*), sum(Time), min(Timestamp), max(Timestamp) from record_race where Map = '%s' %s group by Name order by count(*) desc limit 20;" % (con.escape_string(originalMapName), mbCountry))
  rows = cur.fetchall()
  ranks = []

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
    ranks.append((currentRank, row[0], row[1], row[2], row[3], row[4]))

  return ranks

def getRanks(originalMapName, country, mbCountry):
  rows = []
  ranks = []
  countFinishes = 0

  query("select l.Name, minTime, l.Timestamp, playCount, minTimestamp, SUBSTRING(l.Server, 1, 3) from (select * from record_race where Map = '%s' %s) as l JOIN (select Name, min(Time) as minTime, count(*) as playCount, min(Timestamp) as minTimestamp from record_race where Map = '%s' %s group by Name order by minTime ASC limit 20) as r on l.Time = r.minTime and l.Name = r.Name GROUP BY Name ORDER BY minTime, l.Name;" % (con.escape_string(originalMapName), mbCountry, con.escape_string(originalMapName), mbCountry))
  rows = cur.fetchall()

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

    if currentPosition <= 20:
      ranks.append((currentRank, row[0], row[1], row[2], row[3], row[5] if row[5] else 'UNK'))

  return (ranks, countFinishes)

with con:
  cur = con.cursor()
  cur.execute("set names 'utf8mb4';")

  def query(sql):
    global con, cur
    try:
      cur.execute(sql)
    except:
      con = mysqlConnect()
      con.autocommit(True)
      cur = con.cursor()
      cur.execute("set names 'utf8mb4';")
      cur.execute(sql)

  def application(env, start_response):
    path = env['PATH_INFO']
    parts = path.split('/')

    country = None
    if path in ['/maps/', '/maps2/']:
      qs = parse_qs(env['QUERY_STRING'])

      if 'json' in qs:
        originalMapName = qs['json'][0]

        start_response('200 OK', [('Content-Type', 'application/json')])

        jsonT = OrderedDict()

        query("select Server, Points, Stars, Mapper, Timestamp from record_maps where Map = '%s';" % con.escape_string(originalMapName))
        rows = cur.fetchall()
        if len(rows) > 0:
          jsonT['name'] = originalMapName
          slugifiedMapName = slugify2(u'%s' % originalMapName)
          jsonT['website'] = 'https://ddnet.org/maps/%s' % slugifiedMapName
          normalizedMapName = normalizeMapname(originalMapName)
          jsonT['thumbnail'] = 'https://ddnet.org/ranks/maps/%s.png' % normalizedMapName
          jsonT['web_preview'] = 'https://ddnet.org/mappreview/?map=%s' % quote_plus(originalMapName)

          (type, points, stars, mapperName, mapTimestamp) = rows[0]
          jsonT['type'] = type
          jsonT['points'] = points
          jsonT['difficulty'] = stars
          jsonT['mapper'] = mapperName
          if mapTimestamp:
              jsonT['release'] = mktime(mapTimestamp.timetuple())

          country = qs['country'][0] if 'country' in qs else None
          if country == "OLD": # Old ranks had no country
            mbCountry = "and Server = \"\""
            mbCountry2 = "where Server = \"\""
          elif country:
            mbCountry = "and Server like \"%s%%%%\"" % con.escape_string(country)
            mbCountry2 = "where Server like \"%s%%%%\"" % con.escape_string(country)
          else:
            mbCountry = ""
            mbCountry2 = ""

          finishes = getFinishes(originalMapName, country, mbCountry)
          (ranks, countFinishes) = getRanks(originalMapName, country, mbCountry)
          teamRanks = getTeamRanks(originalMapName, country, mbCountry2, html=False)
          if countFinishes:
            query("select (select median(Time) over (partition by Map) from record_race where Map = '%s' %s limit 1), min(Timestamp), max(Timestamp), count(*), count(distinct Name) from record_race where Map = '%s' %s;" % (con.escape_string(originalMapName), mbCountry, con.escape_string(originalMapName), mbCountry))
            rows = cur.fetchall()
            jsonT['median_time'] = rows[0][0]
            jsonT['first_finish'] = mktime(rows[0][1].timetuple())
            jsonT['last_finish'] = mktime(rows[0][2].timetuple())
            jsonT['finishes'] = rows[0][3]
            jsonT['finishers'] = rows[0][4]

          if type == "Solo" or type == "Race" or type == "Dummy":
            jsonT['biggest_team'] = 0
          else:
            if country == None:
              query("select count(Name) from record_teamrace where Map = '%s' group by ID order by count(Name) desc limit 1;" % con.escape_string(originalMapName))
            else:
              query("select count(record_teamrace.Name) from (record_teamrace join record_race on record_teamrace.Map = record_race.Map and record_teamrace.Name = record_race.Name and record_teamrace.Time = record_race.Time) where record_teamrace.Map = '%s' %s group by ID order by count(record_teamrace.Name) desc limit 1;" % (con.escape_string(originalMapName), mbCountry))
            rows = cur.fetchall()
            jsonT['biggest_team'] = 0 if len(rows) == 0 else rows[0][0]

          with open('/home/teeworlds/servers/maps/%s.msgpack' % originalMapName, 'rb') as inp:
            unpacker = msgpack.Unpacker(inp)
            jsonT['width'] = unpacker.unpack()
            jsonT['height'] = unpacker.unpack()
            tiles = unpacker.unpack()
            jsonT['tiles'] = sorted(tiles.keys(), key=lambda i:order(i))

          jsonT['team_ranks'] = []
          for teamRank in teamRanks:
            (currentRank, names, time, timestamp, foundCountry) = teamRank
            teamRankT = OrderedDict()
            teamRankT['rank'] = currentRank
            teamRankT['players'] = names
            teamRankT['time'] = time
            teamRankT['timestamp'] = mktime(timestamp.timetuple())
            teamRankT['country'] = foundCountry
            jsonT['team_ranks'].append(teamRankT)

          jsonT['ranks'] = []
          for rank in ranks:
            (rank, name, time, timestamp, playCount, foundCountry) = rank
            rankT = OrderedDict()
            rankT['rank'] = rank
            rankT['player'] = name
            rankT['time'] = time
            rankT['timestamp'] = mktime(timestamp.timetuple())
            rankT['country'] = foundCountry
            jsonT['ranks'].append(rankT)

          jsonT['max_finishes'] = []
          for rank in finishes:
            (rank, name, num, time, minTime, maxTime) = rank
            rankT = OrderedDict()
            rankT['rank'] = rank
            rankT['player'] = name
            rankT['num'] = num
            rankT['time'] = time
            rankT['min_timestamp'] = mktime(minTime.timetuple())
            rankT['max_timestamp'] = mktime(minTime.timetuple())
            jsonT['max_finishes'].append(rankT)

        return json.dumps(jsonT)
      if 'map' in qs:
        q = qs['map'][0]
        if 'country' in qs:
          newPath = '/maps/%s/%s' % (qs['country'][0].lower(), slugify2(u'%s' % q).encode('utf-8'))
        else:
          newPath = '/maps/%s' % slugify2(u'%s' % q).encode('utf-8')
        start_response('301 Moved Permanently', [('Location', newPath)])
        return ''

      if 'mapper' in qs:
        q = qs['mapper'][0]
        newPath = '/mappers/%s' % slugify2(u'%s' % q).encode('utf-8')
        start_response('301 Moved Permanently', [('Location', newPath)])
        return ''

      if 'query' in qs:
        q = qs['query'][0]
        jsonT = []
        query("""
        SELECT l.Map, l.Server, Mapper
        FROM (
          SELECT * FROM record_maps
          WHERE Map LIKE '%%%s%%' COLLATE utf8mb4_general_ci or Mapper LIKE '%%%s%%' COLLATE utf8mb4_general_ci
          ORDER BY
            CASE WHEN Map = '%s' THEN 0 ELSE 1 END,
            CASE WHEN Map LIKE '%s%%' COLLATE utf8mb4_general_ci THEN 0 ELSE 1 END,
            CASE WHEN Map LIKE '%%%s%%' COLLATE utf8mb4_general_ci THEN 0 ELSE 1 END,
            CASE WHEN Mapper = '%s' THEN 0 ELSE 1 END,
            CASE WHEN Mapper LIKE '%s%%' COLLATE utf8mb4_general_ci THEN 0 ELSE 1 END,
            LENGTH(Map),
            Map
          LIMIT 10
        ) as l;""" % (con.escape_string('%'.join(q)), con.escape_string('%'.join(q)), con.escape_string(q), con.escape_string(q), con.escape_string('%'.join(q)), con.escape_string(q), con.escape_string(q)))
        rows = cur.fetchall()
        if len(rows) > 0:
          for row in rows:
            jsonT.append({'name': row[0], 'type': row[1]})
            if row[2] != "Unknown Mapper":
              jsonT[-1]['mapper'] = row[2]

        start_response('200 OK', [('Content-Type', 'application/json')])
        return json.dumps(jsonT)

      if 'qmapper' in qs:
        q = qs['qmapper'][0]
        jsonT = []
        query("""
        SELECT Mapper, l.NumMaps
        FROM (
          SELECT * FROM record_mappers
          WHERE Mapper LIKE '%%%s%%' COLLATE utf8mb4_general_ci
          ORDER BY
            CASE WHEN Mapper = '%s' COLLATE utf8mb4_general_ci THEN 0 ELSE 1 END,
            CASE WHEN Mapper LIKE '%s%%' COLLATE utf8mb4_general_ci THEN 0 ELSE 1 END,
            NumMaps DESC,
            LENGTH(Mapper),
            Mapper
          LIMIT 10
        ) as l;""" % (con.escape_string('%'.join(q)), con.escape_string(q), con.escape_string(q)))
        rows = cur.fetchall()
        if len(rows) > 0:
          for row in rows:
            jsonT.append({'mapper': row[0], 'num_maps': row[1]})

        start_response('200 OK', [('Content-Type', 'application/json')])
        return json.dumps(jsonT)

    if len(parts) >= 4 and parts[3] != '':
      country = parts[2].upper()
      mapName = parts[3]
      if country not in countries:
        start_response('404 Not Found', [('Content-Type', 'text/html')])
        with open('%s/maps/index.html' % webDir, 'rb') as err:
          return err.read()
    elif len(parts) >= 3:
      mapName = parts[2]
    else:
      start_response('404 Not Found', [('Content-Type', 'text/html')])
      with open('%s/maps/index.html' % webDir, 'rb') as err:
        return err.read()

    if country == "OLD": # Old ranks had no country
      mbCountry = "and Server = \"\""
      mbCountry2 = "where Server = \"\""
    elif country:
      mbCountry = "and Server like \"%s%%%%\"" % con.escape_string(country)
      mbCountry2 = "where Server like \"%s%%%%\"" % con.escape_string(country)
    else:
      mbCountry = ""
      mbCountry2 = ""

    originalMapName = deslugify2(u'%s' % mapName.encode('utf-8'))
    if originalMapName.rstrip() != originalMapName:
      if country:
        newPath = '/maps/%s/%s' % (country.lower(), slugify2(u'%s' % originalMapName.rstrip()).encode('utf-8'))
      else:
        newPath = '/maps/%s' % slugify2(u'%s' % originalMapName.rstrip()).encode('utf-8')
      start_response('301 Moved Permanently', [('Location', newPath)])
      return ''

    query("select Server, Points, Stars, Mapper, Timestamp from record_maps where Map = '%s';" % con.escape_string(originalMapName))
    rows = cur.fetchall()
    if len(rows) == 0:
      start_response('404 Not Found', [('Content-Type', 'text/html')])
      with open('%s/maps/index.html' % webDir, 'rb') as err:
        return err.read()

    start_response('200 OK', [('Content-Type', 'text/html')])

    out = cStringIO.StringIO()

    (type, points, stars, mapperName, mapTimestamp) = rows[0]
    normalizedMapName = normalizeMapname(originalMapName)

    if not mapperName:
      mbMapperName = ""
      mbMapperNameHtml = ""
    else:
      names = splitMappers(mapperName)
      newNames = []
      newNamesHtml = []
      for name in names:
        newNames.append(escape(name))
        newNamesHtml.append('<a href="%s">%s</a>' % (mapperWebsite(name), escape(name)))

      mbMapperNameHtml = " by %s" % makeAndString(newNamesHtml)
      mbMapperName = " by %s" % makeAndString(newNames)

    slugifiedMapName = slugify2(u'%s' % originalMapName)
    menuText = '<ul>'
    menuText += '<li><a href="/maps/%s">Global Ranks</a></li>' % slugifiedMapName
    for c in countries:
      menuText += '<li><a href="/maps/%s/%s">%s Ranks</a></li>\n' % (c.lower(), slugifiedMapName, c)
    menuText += '</ul>'
    menuText += '</ul>'

    mbCountryString = ' (%s)' % (country) if country else ""
    print >>out, header("%s%s - %s Server Ranks%s - DDraceNetwork" % (escape(originalMapName), mbMapperName, type, mbCountryString), menuText, "")

    ranksLink = '/ranks/%s/%s/' % (country.lower(), type.lower()) if country else '/ranks/%s/' % type.lower()
    print >>out, '<div id="global" class="longblock div-ranks">'
    print >>out, '<div class="right"><form id="mapform" action="/maps/" method="get"><input id="mapsearch" name="map" class="typeahead" type="text" placeholder="Map search"><input type="submit" value="Map search" style="position: absolute; left: -9999px"></form><br><form id="mapperform" action="/maps/" method="get"><input id="mappersearch" name="mapper" class="typeahead" type="text" placeholder="Mapper search"><input type="submit" value="Mapper search" style="position: absolute; left: -9999px"></form></div>'
    print >>out, '<h2><a href="%s">%s Server Ranks%s</a></h2>' % (ranksLink, type, mbCountryString)
    print >>out, '<script src="/jquery.js" type="text/javascript"></script>'
    print >>out, '<script src="/typeahead.bundle.js" type="text/javascript"></script>'
    print >>out, '<script src="/mapsearch.js" type="text/javascript"></script>'
    print >>out, '<script src="/mappersearch.js" type="text/javascript"></script>'
    print >>out, '<script>'
    print >>out, '  var input = document.getElementById("mapsearch");'
    print >>out, '  input.focus();'
    print >>out, '  input.select();'
    print >>out, '</script>'

    print >>out, '<br></div>'
    print >>out, '<div id="global" class="longblock div-ranks">'

    print >>out, '<h2>%s%s</h2>' % (escape(originalMapName), mbMapperNameHtml)
    print >>out, '<br>'

    finishes = getFinishes(originalMapName, country, mbCountry)
    teamRanks = getTeamRanks(originalMapName, country, mbCountry2, html=True)
    (ranks, countFinishes) = getRanks(originalMapName, country, mbCountry)

    if countFinishes == 1:
      mbS2 = ""
    else:
      mbS2 = "s"

    avgTime = ""
    finishTimes = ""

    if countFinishes:
      query("select (select median(Time) over (partition by Map) from record_race where Map = '%s' %s limit 1), min(Timestamp), max(Timestamp), count(*), count(distinct Name) from record_race where Map = '%s' %s;" % (con.escape_string(originalMapName), mbCountry, con.escape_string(originalMapName), mbCountry))
      rows = cur.fetchall()
      avgTime = " (median time: %s)" % formatTime(rows[0][0])
      finishTimes = "first finish: %s, last finish: %s" % (escape(formatDate(rows[0][1])), escape(formatDate(rows[0][2])))
      finishTimes += ", total finishes: %d" % rows[0][3]
      countFinishes = rows[0][4]

    if type == "Solo" or type == "Race" or type == "Dummy":
      biggestTeam = ""
    else:
      if country == None:
        query("select count(Name) from record_teamrace where Map = '%s' group by ID order by count(Name) desc limit 1;" % con.escape_string(originalMapName))
      else:
        query("select count(record_teamrace.Name) from (record_teamrace join record_race on record_teamrace.Map = record_race.Map and record_teamrace.Name = record_race.Name and record_teamrace.Time = record_race.Time) where record_teamrace.Map = '%s' %s group by ID order by count(record_teamrace.Name) desc limit 1;" % (con.escape_string(originalMapName), mbCountry))
      rows = cur.fetchall()
      biggestTeam = "" if len(rows) == 0 else " (biggest team: %d)" % rows[0][0]

    formattedMapName = escape(originalMapName)
    mbMapInfo = ""
    with open('/home/teeworlds/servers/maps/%s.msgpack' % originalMapName, 'rb') as inp:
      unpacker = msgpack.Unpacker(inp)
      width = unpacker.unpack()
      height = unpacker.unpack()
      tiles = unpacker.unpack()

      formattedMapName = '<span title="Map size: %dx%d">%s</span>' % (width, height, escape(originalMapName))

      mbMapInfo = "<br/>"
      for tile in sorted(tiles.keys(), key=lambda i:order(i)):
        mbMapInfo += tileHtml(tile)

    mbReleased = ""
    try:
      cur.execute("select DATE_FORMAT(Timestamp, '%%Y-%%m-%%d') from record_maps where Map = '%s';" % con.escape_string(originalMapName))
      rows = cur.fetchall()
      if rows[0][0] != "0000-00-00":
        mbReleased = "Released: %s<br/>" % rows[0][0]
    except:
      pass

    if type == "Solo" or type == "Race" or type == "Dummy":
      print >>out, u'<div class="block2 info"><p>%sDifficulty: %s, Points: %d<br/><a href="/mappreview/?map=%s"><img class="screenshot" alt="Screenshot" src="/ranks/maps/%s.png" width="360" height="225" /></a>%s<br/><span title="%s">%d tee%s finished%s</span></p></div>' % (mbReleased, escape(renderStars(stars)), globalPoints(type, stars), quote_plus(originalMapName), escape(normalizedMapName), mbMapInfo, finishTimes, countFinishes, mbS2, escape(avgTime))
      print >>out, printExactSoloRecords("Records", "records", ranks, not country)
    else:
      query("select count(distinct ID) from record_teamrace left join record_race on record_teamrace.Map = record_race.Map and record_teamrace.Name = record_race.Name and record_teamrace.Time = record_race.Time where record_teamrace.Map = '%s' %s" % (con.escape_string(originalMapName), mbCountry))
      rows = cur.fetchall()
      countTeamFinishes = rows[0][0]
      if countTeamFinishes == 1:
        mbS = ""
      else:
        mbS = "s"

      print >>out, u'<div class="block2 info"><p>%sDifficulty: %s, Points: %d<br/><a href="/mappreview/?map=%s"><img class="screenshot" alt="Screenshot" src="/ranks/maps/%s.png" width="360" height="225" /></a>%s<br/><span title="%s">%d tee%s finished%s</span><br/>%d team%s finished%s</p></div>' % (mbReleased, escape(renderStars(stars)), globalPoints(type, stars), quote_plus(originalMapName), escape(normalizedMapName), mbMapInfo, finishTimes, countFinishes, mbS2, escape(avgTime), countTeamFinishes, mbS, escape(biggestTeam))
      print >>out, printTeamRecords("Team Records", "teamrecords", teamRanks, not country)
      print >>out, printSoloRecords("Records", "records", ranks, not country)

    print >>out, printFinishes("Most Finishes", "finishes", finishes)

    print >>out, '<br>'
    if country:
        print >>out, '<a href="/maps/?json=%s&country=%s"><img width="36" src="/json.svg"/></a> Ranks and information for this map on %s server are also available in JSON format.' % (quote_plus(originalMapName), quote_plus(country), country)
    else:
        print >>out, '<a href="/maps/?json=%s"><img width="36" src="/json.svg"/></a> Ranks and information for this map are also available in JSON format.' % quote_plus(originalMapName)
    print >>out, '<br>'
    print >>out, '</div>'
    print >>out, """  </section>
  </article>
  </body>
  </html>"""

    return out.getvalue()

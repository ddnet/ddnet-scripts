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

reload(sys)
sys.setdefaultencoding('utf8')

con = mysqlConnect()
con.autocommit(True)

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
    if path == '/maps/':
      qs = parse_qs(env['QUERY_STRING'])

      if 'map' in qs:
        q = qs['map'][0]
        if 'country' in qs:
          newPath = '/maps/%s/%s' % (qs['country'][0].lower(), slugify2(u'%s' % q).encode('utf-8'))
        else:
          newPath = '/maps/%s' % slugify2(u'%s' % q).encode('utf-8')
        start_response('301 Moved Permanently', [('Location', newPath)])
        return ''

      if 'query' in qs:
        q = qs['query'][0]
        jsonT = []
        query("""
        SELECT l.Map, l.Server, Mapper
        FROM (
          SELECT * FROM record_maps
          WHERE Map LIKE '%s' COLLATE utf8mb4_general_ci
          ORDER BY
            CASE WHEN Map = '%s' THEN 0 ELSE 1 END,
            CASE WHEN Map LIKE '%s%%' THEN 0 ELSE 1 END,
            LENGTH(Map),
            Map
          LIMIT 10
        ) as l;""" % ('%' + '%'.join(con.escape_string(q)) + '%', con.escape_string(q), con.escape_string(q)))
        rows = cur.fetchall()
        if len(rows) > 0:
          for row in rows:
            jsonT.append({'name': row[0], 'type': row[1]})
            if row[2] != "Unknown Mapper":
              jsonT[-1]['mapper'] = row[2]

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

    slugifiedMapName = slugify2(originalMapName)
    menuText = '<ul>'
    menuText += '<li><a href="/maps/%s">Global Ranks</a></li>' % slugifiedMapName
    for c in countries:
      menuText += '<li><a href="/maps/%s/%s">%s Ranks</a></li>\n' % (c.lower(), slugifiedMapName, c)
    menuText += '</ul>'
    menuText += '</ul>'

    print >>out, header("%s%s - Map on %s Server - DDraceNetwork" % (escape(originalMapName), mbMapperName, type), menuText, "")

    mbCountryString = ' (%s)' % (country) if country else ""
    ranksLink = '/ranks/%s/%s/' % (country.lower(), type.lower()) if country else '/ranks/%s/' % type.lower()
    print >>out, '<div id="global" class="longblock div-ranks">'
    print >>out, '<div class="right"><form id="mapform" action="/maps/" method="get"><input id="mapsearch" name="map" class="typeahead" type="text" placeholder="Map search"><input type="submit" value="Map search" style="position: absolute; left: -9999px"></form></div>'
    print >>out, '<h2><a href="%s">%s Server Ranks%s</a></h2>' % (ranksLink, type, mbCountryString)
    print >>out, '<script src="/jquery.js" type="text/javascript"></script>'
    print >>out, '<script src="/typeahead.bundle.js" type="text/javascript"></script>'
    print >>out, '<script src="/mapsearch.js" type="text/javascript"></script>'
    print >>out, '<script>'
    print >>out, '  var input = document.getElementById("mapsearch");'
    print >>out, '  input.focus();'
    print >>out, '  input.select();'
    print >>out, '</script>'

    print >>out, '<br></div>'
    print >>out, '<div id="global" class="longblock div-ranks">'

    print >>out, '<h2>%s%s</h2>' % (escape(originalMapName), mbMapperNameHtml)
    print >>out, '<br>'

    rows = []
    teamRanks = []
    namesOnMap = {}
    names = []
    time = 0
    currentRank = 1
    currentPosition = 1
    skips = 1

    if country == None:
      query("select distinct r.Name, r.ID, r.Time, r.Timestamp, SUBSTRING(n.Server, 1, 3) from ((select distinct ID from record_teamrace where Map = '%s' ORDER BY Time limit 20) as l) left join record_teamrace as r on l.ID = r.ID inner join record_race as n on r.Map = n.Map and r.Name = n.Name and r.Time = n.Time order by r.Time, r.ID, r.Name;" % (con.escape_string(originalMapName)))
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
          teamRanks.append((currentRank, joinNames(fNames), time, timestamp, foundCountry))
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
      teamRanks.append((currentRank, joinNames(fNames), time, timestamp, foundCountry))

    rows = []
    ranks = []
    countFinishes = 0

    query("select l.Name, minTime, l.Timestamp, playCount, minTimestamp, SUBSTRING(l.Server, 1, 3) from (select * from record_race where Map = '%s' %s) as l JOIN (select Name, min(Time) as minTime, count(*) as playCount, min(Timestamp) as minTimestamp from record_race where Map = '%s' %s group by Name order by minTime ASC limit 20) as r on l.Time = r.minTime and l.Name = r.Name GROUP BY Name ORDER BY minTime;" % (con.escape_string(originalMapName), mbCountry, con.escape_string(originalMapName), mbCountry))
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

    print >>out, '<br>'
    print >>out, '</div>'
    print >>out, """  </section>
  </article>
  </body>
  </html>"""

    return out.getvalue()
